"""
Modelos do banco de dados para o Controle Financeiro Pessoal - VERSÃO 3
Implementa: Usuario, Transacao (base), Receita, Despesa, Categoria, Orcamento
"""

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    """Modelo de usuário para autenticação simples"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    categorias = db.relationship('Categoria', backref='usuario', lazy=True, cascade='all, delete-orphan')
    transacoes = db.relationship('Transacao', backref='usuario', lazy=True, cascade='all, delete-orphan')
    orcamentos = db.relationship('Orcamento', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Definir a senha com hash"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar se a senha está correta"""
        return check_password_hash(self.senha_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Categoria(db.Model):
    """Modelo de categoria para classificar transações"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    transacoes = db.relationship('Transacao', backref='categoria', lazy=True)
    orcamentos = db.relationship('Orcamento', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Transacao(db.Model):
    """Classe base para transações (Receita e Despesa)"""
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'receita' ou 'despesa'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Discriminador para herança de tabela única
    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'transacao'
    }
    
    def __repr__(self):
        return f'<Transacao {self.descricao}: R$ {self.valor}>'


class Receita(Transacao):
    """Modelo de receita (herda de Transacao)"""
    __mapper_args__ = {
        'polymorphic_identity': 'receita'
    }
    
    def __repr__(self):
        return f'<Receita {self.descricao}: R$ {self.valor}>'


class Despesa(Transacao):
    """Modelo de despesa (herda de Transacao)"""
    __mapper_args__ = {
        'polymorphic_identity': 'despesa'
    }
    
    def __repr__(self):
        return f'<Despesa {self.descricao}: R$ {self.valor}>'


class Orcamento(db.Model):
    """Modelo de orçamento para definir metas de gastos"""
    __tablename__ = 'orcamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ano = db.Column(db.Integer, nullable=False)
    limite = db.Column(db.Float, nullable=False)  # Limite de gastos
    alerta_percentual = db.Column(db.Float, default=80.0)  # Percentual para alerta (ex: 80%)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índice composto para garantir um orçamento por categoria/mês/ano
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'categoria_id', 'mes', 'ano', name='uq_orcamento_mes_ano'),
    )
    
    def get_gasto_atual(self):
        """Calcular o gasto atual do mês para esta categoria"""
        from datetime import datetime as dt
        
        primeiro_dia = dt(self.ano, self.mes, 1)
        if self.mes == 12:
            ultimo_dia = dt(self.ano + 1, 1, 1)
        else:
            ultimo_dia = dt(self.ano, self.mes + 1, 1)
        
        gasto = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.usuario_id == self.usuario_id,
            Transacao.categoria_id == self.categoria_id,
            Transacao.tipo == 'despesa',
            Transacao.data >= primeiro_dia,
            Transacao.data < ultimo_dia
        ).scalar() or 0.0
        
        return float(gasto)
    
    def get_percentual_usado(self):
        """Calcular o percentual do orçamento utilizado"""
        if self.limite <= 0:
            return 0.0
        
        gasto = self.get_gasto_atual()
        percentual = (gasto / self.limite) * 100
        return min(percentual, 100.0)  # Máximo 100% para visualização
    
    def get_restante(self):
        """Calcular o valor restante do orçamento"""
        gasto = self.get_gasto_atual()
        restante = self.limite - gasto
        return max(restante, 0.0)
    
    def get_status(self):
        """Retornar o status do orçamento"""
        percentual = self.get_percentual_usado()
        
        if percentual >= 100:
            return 'excedido'
        elif percentual >= self.alerta_percentual:
            return 'aviso'
        else:
            return 'ok'
    
    def get_status_badge(self):
        """Retornar o badge de status para exibição"""
        status = self.get_status()
        
        if status == 'excedido':
            return {'classe': 'danger', 'texto': 'Excedido', 'icone': 'fa-exclamation-circle'}
        elif status == 'aviso':
            return {'classe': 'warning', 'texto': 'Aviso', 'icone': 'fa-exclamation-triangle'}
        else:
            return {'classe': 'success', 'texto': 'Ok', 'icone': 'fa-check-circle'}
    
    def get_dias_restantes_mes(self):
        """Calcular os dias restantes do mês"""
        from datetime import datetime as dt, timedelta
        
        hoje = dt.utcnow()
        
        # Se não é o mês atual, retornar 0
        if hoje.year != self.ano or hoje.month != self.mes:
            return 0
        
        # Calcular o último dia do mês
        if self.mes == 12:
            ultimo_dia_mes = dt(self.ano + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = dt(self.ano, self.mes + 1, 1) - timedelta(days=1)
        
        dias_restantes = (ultimo_dia_mes.date() - hoje.date()).days + 1
        return max(dias_restantes, 0)
    
    def get_projecao_gasto(self):
        """Calcular a projeção de gasto até o final do mês"""
        from datetime import datetime as dt
        
        hoje = dt.utcnow()
        
        # Se não é o mês atual, retornar o gasto atual
        if hoje.year != self.ano or hoje.month != self.mes:
            return self.get_gasto_atual()
        
        # Calcular dias passados
        dias_passados = hoje.day
        dias_restantes = self.get_dias_restantes_mes()
        
        if dias_passados == 0:
            return 0.0
        
        gasto_atual = self.get_gasto_atual()
        media_diaria = gasto_atual / dias_passados
        projecao = gasto_atual + (media_diaria * dias_restantes)
        
        return projecao
    
    def get_alerta_projecao(self):
        """Retornar alerta se a projeção ultrapassar o limite"""
        projecao = self.get_projecao_gasto()
        
        if projecao > self.limite:
            excesso = projecao - self.limite
            return {
                'alerta': True,
                'mensagem': f'Projeção: R$ {projecao:.2f} (Excesso: R$ {excesso:.2f})',
                'classe': 'warning'
            }
        else:
            margem = self.limite - projecao
            return {
                'alerta': False,
                'mensagem': f'Projeção: R$ {projecao:.2f} (Margem: R$ {margem:.2f})',
                'classe': 'info'
            }
    
    def __repr__(self):
        return f'<Orcamento {self.categoria.nome} {self.mes}/{self.ano}: R$ {self.limite}>'
