"""
Rotas da aplicação Flask para Controle Financeiro Pessoal - VERSÃO 2
Implementa: Autenticação, Dashboard, Categorias, Transações, Edição, Busca e Filtros
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models import Usuario, Categoria, Transacao, Receita, Despesa
from datetime import datetime, timedelta
from functools import wraps
import calendar
from sqlalchemy import or_, and_

# ========== BLUEPRINTS ==========
auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
categorias_bp = Blueprint('categorias', __name__)
transacoes_bp = Blueprint('transacoes', __name__)


# ========== DECORADOR DE AUTENTICAÇÃO ==========
def login_required(f):
    """Decorador para verificar se o usuário está autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login primeiro.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== ROTAS DE AUTENTICAÇÃO ==========
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Rota para registro de novo usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        # Validações
        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if len(nome) < 3:
            flash('O nome deve ter pelo menos 3 caracteres.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.registro'))
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('auth.registro'))
        
        # Verificar se o email já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está registrado.', 'danger')
            return redirect(url_for('auth.registro'))
        
        # Criar novo usuário
        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuário"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'danger')
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(url_for('dashboard.home'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Rota para logout de usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))


# ========== ROTAS DO DASHBOARD ==========
@dashboard_bp.route('/')
@login_required
def home():
    """Rota principal - Dashboard com resumo mensal"""
    usuario_id = session.get('usuario_id')
    
    # Obter o mês e ano atuais
    hoje = datetime.utcnow()
    primeiro_dia_mes = datetime(hoje.year, hoje.month, 1)
    
    # Calcular o primeiro dia do próximo mês
    if hoje.month == 12:
        ultimo_dia_mes = datetime(hoje.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        ultimo_dia_mes = datetime(hoje.year, hoje.month + 1, 1) - timedelta(seconds=1)
    
    # Obter transações do mês
    transacoes_mes = Transacao.query.filter(
        Transacao.usuario_id == usuario_id,
        Transacao.data >= primeiro_dia_mes,
        Transacao.data <= ultimo_dia_mes
    ).all()
    
    # Calcular totais
    total_receitas = sum(t.valor for t in transacoes_mes if t.tipo == 'receita')
    total_despesas = sum(t.valor for t in transacoes_mes if t.tipo == 'despesa')
    saldo = total_receitas - total_despesas
    
    # Agrupar despesas por categoria
    despesas_por_categoria = {}
    for transacao in transacoes_mes:
        if transacao.tipo == 'despesa':
            categoria_nome = transacao.categoria.nome
            if categoria_nome not in despesas_por_categoria:
                despesas_por_categoria[categoria_nome] = 0
            despesas_por_categoria[categoria_nome] += transacao.valor
    
    # Ordenar por valor decrescente
    despesas_por_categoria = dict(sorted(despesas_por_categoria.items(), key=lambda x: x[1], reverse=True))
    
    # Obter categorias do usuário
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    
    # Informações do mês
    nome_mes = calendar.month_name[hoje.month]
    
    return render_template(
        'dashboard.html',
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        saldo=saldo,
        despesas_por_categoria=despesas_por_categoria,
        mes=nome_mes,
        ano=hoje.year,
        categorias=categorias,
        transacoes_mes=transacoes_mes
    )


# ========== ROTAS DE CATEGORIAS ==========
@categorias_bp.route('/categorias', methods=['GET', 'POST'])
@login_required
def listar_categorias():
    """Rota para listar e criar categorias"""
    usuario_id = session.get('usuario_id')
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        
        if not nome:
            flash('O nome da categoria é obrigatório.', 'danger')
            return redirect(url_for('categorias.listar_categorias'))
        
        if len(nome) < 2:
            flash('O nome da categoria deve ter pelo menos 2 caracteres.', 'danger')
            return redirect(url_for('categorias.listar_categorias'))
        
        # Verificar se a categoria já existe para este usuário
        categoria_existente = Categoria.query.filter_by(
            usuario_id=usuario_id,
            nome=nome
        ).first()
        
        if categoria_existente:
            flash('Esta categoria já existe.', 'danger')
            return redirect(url_for('categorias.listar_categorias'))
        
        # Criar nova categoria
        nova_categoria = Categoria(nome=nome, usuario_id=usuario_id)
        db.session.add(nova_categoria)
        db.session.commit()
        
        flash(f'Categoria "{nome}" criada com sucesso!', 'success')
        return redirect(url_for('categorias.listar_categorias'))
    
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    return render_template('categorias.html', categorias=categorias)


@categorias_bp.route('/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(categoria_id):
    """Rota para editar uma categoria"""
    usuario_id = session.get('usuario_id')
    categoria = Categoria.query.get_or_404(categoria_id)
    
    # Verificar se a categoria pertence ao usuário
    if categoria.usuario_id != usuario_id:
        flash('Você não tem permissão para editar esta categoria.', 'danger')
        return redirect(url_for('categorias.listar_categorias'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        
        if not nome:
            flash('O nome da categoria é obrigatório.', 'danger')
            return redirect(url_for('categorias.editar_categoria', categoria_id=categoria_id))
        
        if len(nome) < 2:
            flash('O nome da categoria deve ter pelo menos 2 caracteres.', 'danger')
            return redirect(url_for('categorias.editar_categoria', categoria_id=categoria_id))
        
        categoria.nome = nome
        db.session.commit()
        
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('categorias.listar_categorias'))
    
    return render_template('editar_categoria.html', categoria=categoria)


@categorias_bp.route('/categorias/<int:categoria_id>/deletar', methods=['POST'])
@login_required
def deletar_categoria(categoria_id):
    """Rota para deletar uma categoria"""
    usuario_id = session.get('usuario_id')
    categoria = Categoria.query.get_or_404(categoria_id)
    
    # Verificar se a categoria pertence ao usuário
    if categoria.usuario_id != usuario_id:
        flash('Você não tem permissão para deletar esta categoria.', 'danger')
        return redirect(url_for('categorias.listar_categorias'))
    
    # Verificar se há transações associadas
    transacoes = Transacao.query.filter_by(categoria_id=categoria_id).all()
    if transacoes:
        flash('Não é possível deletar uma categoria que possui transações.', 'danger')
        return redirect(url_for('categorias.listar_categorias'))
    
    nome_categoria = categoria.nome
    db.session.delete(categoria)
    db.session.commit()
    
    flash(f'Categoria "{nome_categoria}" deletada com sucesso!', 'success')
    return redirect(url_for('categorias.listar_categorias'))


# ========== ROTAS DE TRANSAÇÕES ==========
@transacoes_bp.route('/receita/nova', methods=['GET', 'POST'])
@login_required
def nova_receita():
    """Rota para registrar nova receita"""
    usuario_id = session.get('usuario_id')
    
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', '')
        categoria_id = request.form.get('categoria_id', '')
        data = request.form.get('data', '')
        
        # Validações
        if not descricao or not valor or not categoria_id:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('transacoes.nova_receita'))
        
        if len(descricao) < 3:
            flash('A descrição deve ter pelo menos 3 caracteres.', 'danger')
            return redirect(url_for('transacoes.nova_receita'))
        
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            flash('O valor deve ser um número positivo.', 'danger')
            return redirect(url_for('transacoes.nova_receita'))
        
        # Verificar se a categoria pertence ao usuário
        categoria = Categoria.query.get(categoria_id)
        if not categoria or categoria.usuario_id != usuario_id:
            flash('Categoria inválida.', 'danger')
            return redirect(url_for('transacoes.nova_receita'))
        
        # Converter data
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d') if data else datetime.utcnow()
        except ValueError:
            data_obj = datetime.utcnow()
        
        # Criar nova receita
        nova_receita = Receita(
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
            data=data_obj
        )
        
        db.session.add(nova_receita)
        db.session.commit()
        
        flash('Receita registrada com sucesso!', 'success')
        return redirect(url_for('dashboard.home'))
    
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    return render_template('nova_receita.html', categorias=categorias)


@transacoes_bp.route('/despesa/nova', methods=['GET', 'POST'])
@login_required
def nova_despesa():
    """Rota para registrar nova despesa"""
    usuario_id = session.get('usuario_id')
    
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', '')
        categoria_id = request.form.get('categoria_id', '')
        data = request.form.get('data', '')
        
        # Validações
        if not descricao or not valor or not categoria_id:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('transacoes.nova_despesa'))
        
        if len(descricao) < 3:
            flash('A descrição deve ter pelo menos 3 caracteres.', 'danger')
            return redirect(url_for('transacoes.nova_despesa'))
        
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            flash('O valor deve ser um número positivo.', 'danger')
            return redirect(url_for('transacoes.nova_despesa'))
        
        # Verificar se a categoria pertence ao usuário
        categoria = Categoria.query.get(categoria_id)
        if not categoria or categoria.usuario_id != usuario_id:
            flash('Categoria inválida.', 'danger')
            return redirect(url_for('transacoes.nova_despesa'))
        
        # Converter data
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d') if data else datetime.utcnow()
        except ValueError:
            data_obj = datetime.utcnow()
        
        # Criar nova despesa
        nova_despesa = Despesa(
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
            data=data_obj
        )
        
        db.session.add(nova_despesa)
        db.session.commit()
        
        flash('Despesa registrada com sucesso!', 'success')
        return redirect(url_for('dashboard.home'))
    
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    return render_template('nova_despesa.html', categorias=categorias)


# ========== NOVAS ROTAS - EDIÇÃO DE TRANSAÇÕES ==========
@transacoes_bp.route('/transacao/<int:transacao_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_transacao(transacao_id):
    """Rota para editar uma transação existente"""
    usuario_id = session.get('usuario_id')
    transacao = Transacao.query.get_or_404(transacao_id)
    
    # Verificar se a transação pertence ao usuário
    if transacao.usuario_id != usuario_id:
        flash('Você não tem permissão para editar esta transação.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', '')
        categoria_id = request.form.get('categoria_id', '')
        data = request.form.get('data', '')
        
        # Validações
        if not descricao or not valor or not categoria_id:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('transacoes.editar_transacao', transacao_id=transacao_id))
        
        if len(descricao) < 3:
            flash('A descrição deve ter pelo menos 3 caracteres.', 'danger')
            return redirect(url_for('transacoes.editar_transacao', transacao_id=transacao_id))
        
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            flash('O valor deve ser um número positivo.', 'danger')
            return redirect(url_for('transacoes.editar_transacao', transacao_id=transacao_id))
        
        # Verificar se a categoria pertence ao usuário
        categoria = Categoria.query.get(categoria_id)
        if not categoria or categoria.usuario_id != usuario_id:
            flash('Categoria inválida.', 'danger')
            return redirect(url_for('transacoes.editar_transacao', transacao_id=transacao_id))
        
        # Converter data
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d') if data else datetime.utcnow()
        except ValueError:
            data_obj = datetime.utcnow()
        
        # Atualizar transação
        transacao.descricao = descricao
        transacao.valor = valor
        transacao.categoria_id = categoria_id
        transacao.data = data_obj
        
        db.session.commit()
        
        flash('Transação atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard.home'))
    
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    
    # Formatar data para o input HTML
    data_formatada = transacao.data.strftime('%Y-%m-%d')
    
    return render_template(
        'editar_transacao.html',
        transacao=transacao,
        categorias=categorias,
        data_formatada=data_formatada
    )


@transacoes_bp.route('/transacao/<int:transacao_id>/deletar', methods=['POST'])
@login_required
def deletar_transacao(transacao_id):
    """Rota para deletar uma transação"""
    usuario_id = session.get('usuario_id')
    transacao = Transacao.query.get_or_404(transacao_id)
    
    # Verificar se a transação pertence ao usuário
    if transacao.usuario_id != usuario_id:
        flash('Você não tem permissão para deletar esta transação.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    descricao = transacao.descricao
    db.session.delete(transacao)
    db.session.commit()
    
    flash(f'Transação "{descricao}" deletada com sucesso!', 'success')
    return redirect(url_for('dashboard.home'))


# ========== NOVAS ROTAS - BUSCA E FILTRO ==========
@dashboard_bp.route('/api/transacoes/buscar', methods=['POST'])
@login_required
def buscar_transacoes():
    """API para buscar e filtrar transações (AJAX)"""
    usuario_id = session.get('usuario_id')
    
    # Obter parâmetros de filtro
    descricao = request.json.get('descricao', '').strip()
    categoria_id = request.json.get('categoria_id', '')
    tipo = request.json.get('tipo', '')  # 'receita', 'despesa' ou vazio
    data_inicio = request.json.get('data_inicio', '')
    data_fim = request.json.get('data_fim', '')
    
    # Construir query base
    query = Transacao.query.filter_by(usuario_id=usuario_id)
    
    # Aplicar filtros
    if descricao:
        query = query.filter(Transacao.descricao.ilike(f'%{descricao}%'))
    
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Transacao.data >= data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            # Adicionar 1 dia para incluir todo o dia
            data_fim_obj = data_fim_obj + timedelta(days=1)
            query = query.filter(Transacao.data < data_fim_obj)
        except ValueError:
            pass
    
    # Executar query e ordenar
    transacoes = query.order_by(Transacao.data.desc()).all()
    
    # Formatar resposta
    resultado = []
    for t in transacoes:
        resultado.append({
            'id': t.id,
            'descricao': t.descricao,
            'valor': f"{t.valor:.2f}",
            'categoria': t.categoria.nome,
            'tipo': t.tipo,
            'data': t.data.strftime('%d/%m/%Y'),
            'data_iso': t.data.strftime('%Y-%m-%d')
        })
    
    return jsonify({
        'sucesso': True,
        'total': len(resultado),
        'transacoes': resultado
    })


@dashboard_bp.route('/api/categorias/sugeridas', methods=['GET'])
@login_required
def categorias_sugeridas():
    """API para obter categorias sugeridas baseado no histórico"""
    usuario_id = session.get('usuario_id')
    
    # Obter as 5 categorias mais usadas
    categorias_frequentes = db.session.query(
        Categoria.id,
        Categoria.nome,
        db.func.count(Transacao.id).label('uso')
    ).join(Transacao).filter(
        Categoria.usuario_id == usuario_id
    ).group_by(Categoria.id).order_by(
        db.func.count(Transacao.id).desc()
    ).limit(5).all()
    
    resultado = [
        {'id': c[0], 'nome': c[1], 'uso': c[2]}
        for c in categorias_frequentes
    ]
    
    return jsonify({
        'sucesso': True,
        'categorias': resultado
    })


# ========== NOVAS ROTAS - VALIDAÇÕES EM TEMPO REAL ==========
@transacoes_bp.route('/api/validar/descricao', methods=['POST'])
@login_required
def validar_descricao():
    """API para validar descrição em tempo real"""
    descricao = request.json.get('descricao', '').strip()
    
    erros = []
    
    if not descricao:
        erros.append('A descrição é obrigatória')
    elif len(descricao) < 3:
        erros.append('A descrição deve ter pelo menos 3 caracteres')
    elif len(descricao) > 255:
        erros.append('A descrição não pode ter mais de 255 caracteres')
    
    return jsonify({
        'valido': len(erros) == 0,
        'erros': erros
    })


@transacoes_bp.route('/api/validar/valor', methods=['POST'])
@login_required
def validar_valor():
    """API para validar valor em tempo real"""
    valor_str = request.json.get('valor', '')
    
    erros = []
    
    if not valor_str:
        erros.append('O valor é obrigatório')
    else:
        try:
            valor = float(valor_str)
            if valor <= 0:
                erros.append('O valor deve ser positivo')
            elif valor > 999999.99:
                erros.append('O valor é muito alto')
        except ValueError:
            erros.append('O valor deve ser um número válido')
    
    return jsonify({
        'valido': len(erros) == 0,
        'erros': erros
    })
