"""
Rotas para gerenciamento de Orçamentos e Metas
Implementa CRUD completo para orçamentos com alertas e projeções
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from app.models import Usuario, Categoria, Transacao, Orcamento
from datetime import datetime, timedelta
from functools import wraps
import calendar

orcamentos_bp = Blueprint('orcamentos', __name__)


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


# ========== ROTAS DE ORÇAMENTOS ==========
@orcamentos_bp.route('/orcamentos', methods=['GET'])
@login_required
def listar_orcamentos():
    """Rota para listar orçamentos do mês atual"""
    usuario_id = session.get('usuario_id')
    
    # Obter mês e ano atuais
    hoje = datetime.utcnow()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Obter orçamentos do mês atual
    orcamentos = Orcamento.query.filter_by(
        usuario_id=usuario_id,
        mes=mes_atual,
        ano=ano_atual
    ).all()
    
    # Obter categorias do usuário
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    
    # Calcular resumo
    total_limite = sum(o.limite for o in orcamentos)
    total_gasto = sum(o.get_gasto_atual() for o in orcamentos)
    
    # Contar status
    status_ok = len([o for o in orcamentos if o.get_status() == 'ok'])
    status_aviso = len([o for o in orcamentos if o.get_status() == 'aviso'])
    status_excedido = len([o for o in orcamentos if o.get_status() == 'excedido'])
    
    # Informações do mês
    nome_mes = calendar.month_name[mes_atual]
    
    return render_template(
        'orcamentos.html',
        orcamentos=orcamentos,
        categorias=categorias,
        total_limite=total_limite,
        total_gasto=total_gasto,
        status_ok=status_ok,
        status_aviso=status_aviso,
        status_excedido=status_excedido,
        mes=nome_mes,
        ano=ano_atual,
        mes_numero=mes_atual
    )


@orcamentos_bp.route('/orcamentos/criar', methods=['GET', 'POST'])
@login_required
def criar_orcamento():
    """Rota para criar novo orçamento"""
    usuario_id = session.get('usuario_id')
    
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id', '')
        limite = request.form.get('limite', '')
        alerta_percentual = request.form.get('alerta_percentual', '80')
        mes = request.form.get('mes', '')
        ano = request.form.get('ano', '')
        
        # Validações
        if not categoria_id or not limite or not mes or not ano:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        try:
            categoria_id = int(categoria_id)
            limite = float(limite)
            alerta_percentual = float(alerta_percentual)
            mes = int(mes)
            ano = int(ano)
        except ValueError:
            flash('Valores inválidos.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        # Validar categoria
        categoria = Categoria.query.get(categoria_id)
        if not categoria or categoria.usuario_id != usuario_id:
            flash('Categoria inválida.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        # Validar valores
        if limite <= 0:
            flash('O limite deve ser positivo.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        if alerta_percentual < 1 or alerta_percentual > 100:
            flash('O percentual de alerta deve estar entre 1 e 100.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        if mes < 1 or mes > 12:
            flash('Mês inválido.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        if ano < 2020 or ano > 2100:
            flash('Ano inválido.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        # Verificar se já existe orçamento para esta categoria/mês/ano
        orcamento_existente = Orcamento.query.filter_by(
            usuario_id=usuario_id,
            categoria_id=categoria_id,
            mes=mes,
            ano=ano
        ).first()
        
        if orcamento_existente:
            flash('Já existe um orçamento para esta categoria neste mês.', 'danger')
            return redirect(url_for('orcamentos.criar_orcamento'))
        
        # Criar novo orçamento
        novo_orcamento = Orcamento(
            usuario_id=usuario_id,
            categoria_id=categoria_id,
            mes=mes,
            ano=ano,
            limite=limite,
            alerta_percentual=alerta_percentual
        )
        
        db.session.add(novo_orcamento)
        db.session.commit()
        
        flash(f'Orçamento criado com sucesso para {categoria.nome}!', 'success')
        return redirect(url_for('orcamentos.listar_orcamentos'))
    
    # Obter dados para o formulário
    categorias = Categoria.query.filter_by(usuario_id=usuario_id).all()
    hoje = datetime.utcnow()
    
    return render_template(
        'criar_orcamento.html',
        categorias=categorias,
        mes_atual=hoje.month,
        ano_atual=hoje.year
    )


@orcamentos_bp.route('/orcamentos/<int:orcamento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_orcamento(orcamento_id):
    """Rota para editar um orçamento"""
    usuario_id = session.get('usuario_id')
    orcamento = Orcamento.query.get_or_404(orcamento_id)
    
    # Verificar se o orçamento pertence ao usuário
    if orcamento.usuario_id != usuario_id:
        flash('Você não tem permissão para editar este orçamento.', 'danger')
        return redirect(url_for('orcamentos.listar_orcamentos'))
    
    if request.method == 'POST':
        limite = request.form.get('limite', '')
        alerta_percentual = request.form.get('alerta_percentual', '80')
        
        # Validações
        if not limite:
            flash('O limite é obrigatório.', 'danger')
            return redirect(url_for('orcamentos.editar_orcamento', orcamento_id=orcamento_id))
        
        try:
            limite = float(limite)
            alerta_percentual = float(alerta_percentual)
        except ValueError:
            flash('Valores inválidos.', 'danger')
            return redirect(url_for('orcamentos.editar_orcamento', orcamento_id=orcamento_id))
        
        if limite <= 0:
            flash('O limite deve ser positivo.', 'danger')
            return redirect(url_for('orcamentos.editar_orcamento', orcamento_id=orcamento_id))
        
        if alerta_percentual < 1 or alerta_percentual > 100:
            flash('O percentual de alerta deve estar entre 1 e 100.', 'danger')
            return redirect(url_for('orcamentos.editar_orcamento', orcamento_id=orcamento_id))
        
        # Atualizar orçamento
        orcamento.limite = limite
        orcamento.alerta_percentual = alerta_percentual
        db.session.commit()
        
        flash('Orçamento atualizado com sucesso!', 'success')
        return redirect(url_for('orcamentos.listar_orcamentos'))
    
    return render_template('editar_orcamento.html', orcamento=orcamento)


@orcamentos_bp.route('/orcamentos/<int:orcamento_id>/deletar', methods=['POST'])
@login_required
def deletar_orcamento(orcamento_id):
    """Rota para deletar um orçamento"""
    usuario_id = session.get('usuario_id')
    orcamento = Orcamento.query.get_or_404(orcamento_id)
    
    # Verificar se o orçamento pertence ao usuário
    if orcamento.usuario_id != usuario_id:
        flash('Você não tem permissão para deletar este orçamento.', 'danger')
        return redirect(url_for('orcamentos.listar_orcamentos'))
    
    categoria_nome = orcamento.categoria.nome
    db.session.delete(orcamento)
    db.session.commit()
    
    flash(f'Orçamento de {categoria_nome} deletado com sucesso!', 'success')
    return redirect(url_for('orcamentos.listar_orcamentos'))


# ========== ROTAS DE HISTÓRICO ==========
@orcamentos_bp.route('/orcamentos/historico', methods=['GET'])
@login_required
def historico_orcamentos():
    """Rota para visualizar histórico de orçamentos"""
    usuario_id = session.get('usuario_id')
    
    # Obter parâmetros de filtro
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    # Se não especificado, usar mês/ano anterior
    hoje = datetime.utcnow()
    if not mes or not ano:
        if hoje.month == 1:
            mes = 12
            ano = hoje.year - 1
        else:
            mes = hoje.month - 1
            ano = hoje.year
    
    # Obter orçamentos do período
    orcamentos = Orcamento.query.filter_by(
        usuario_id=usuario_id,
        mes=mes,
        ano=ano
    ).all()
    
    # Gerar lista de meses disponíveis
    meses_disponiveis = db.session.query(
        Orcamento.mes,
        Orcamento.ano
    ).filter_by(usuario_id=usuario_id).distinct().order_by(
        Orcamento.ano.desc(),
        Orcamento.mes.desc()
    ).all()
    
    # Calcular resumo
    total_limite = sum(o.limite for o in orcamentos)
    total_gasto = sum(o.get_gasto_atual() for o in orcamentos)
    
    nome_mes = calendar.month_name[mes]
    
    return render_template(
        'historico_orcamentos.html',
        orcamentos=orcamentos,
        mes=nome_mes,
        ano=ano,
        mes_numero=mes,
        total_limite=total_limite,
        total_gasto=total_gasto,
        meses_disponiveis=meses_disponiveis
    )


# ========== ROTAS DE API ==========
@orcamentos_bp.route('/api/orcamentos/resumo', methods=['GET'])
@login_required
def api_resumo_orcamentos():
    """API para obter resumo de orçamentos"""
    usuario_id = session.get('usuario_id')
    
    hoje = datetime.utcnow()
    
    # Obter orçamentos do mês atual
    orcamentos = Orcamento.query.filter_by(
        usuario_id=usuario_id,
        mes=hoje.month,
        ano=hoje.year
    ).all()
    
    # Calcular resumo
    total_limite = sum(o.limite for o in orcamentos)
    total_gasto = sum(o.get_gasto_atual() for o in orcamentos)
    total_restante = total_limite - total_gasto
    
    # Contar status
    status_ok = len([o for o in orcamentos if o.get_status() == 'ok'])
    status_aviso = len([o for o in orcamentos if o.get_status() == 'aviso'])
    status_excedido = len([o for o in orcamentos if o.get_status() == 'excedido'])
    
    return jsonify({
        'sucesso': True,
        'total_limite': f"{total_limite:.2f}",
        'total_gasto': f"{total_gasto:.2f}",
        'total_restante': f"{total_restante:.2f}",
        'percentual_usado': f"{(total_gasto / total_limite * 100) if total_limite > 0 else 0:.1f}",
        'status_ok': status_ok,
        'status_aviso': status_aviso,
        'status_excedido': status_excedido,
        'total_orcamentos': len(orcamentos)
    })


@orcamentos_bp.route('/api/orcamentos/<int:orcamento_id>/detalhes', methods=['GET'])
@login_required
def api_detalhes_orcamento(orcamento_id):
    """API para obter detalhes de um orçamento"""
    usuario_id = session.get('usuario_id')
    orcamento = Orcamento.query.get_or_404(orcamento_id)
    
    # Verificar se o orçamento pertence ao usuário
    if orcamento.usuario_id != usuario_id:
        return jsonify({'sucesso': False, 'erro': 'Não autorizado'}), 403
    
    gasto = orcamento.get_gasto_atual()
    percentual = orcamento.get_percentual_usado()
    status = orcamento.get_status()
    projecao = orcamento.get_projecao_gasto()
    
    return jsonify({
        'sucesso': True,
        'categoria': orcamento.categoria.nome,
        'limite': f"{orcamento.limite:.2f}",
        'gasto': f"{gasto:.2f}",
        'restante': f"{orcamento.get_restante():.2f}",
        'percentual': f"{percentual:.1f}",
        'status': status,
        'projecao': f"{projecao:.2f}",
        'dias_restantes': orcamento.get_dias_restantes_mes()
    })


@orcamentos_bp.route('/api/orcamentos/alertas', methods=['GET'])
@login_required
def api_alertas_orcamentos():
    """API para obter alertas de orçamentos"""
    usuario_id = session.get('usuario_id')
    
    hoje = datetime.utcnow()
    
    # Obter orçamentos do mês atual com status de aviso ou excedido
    orcamentos = Orcamento.query.filter_by(
        usuario_id=usuario_id,
        mes=hoje.month,
        ano=hoje.year
    ).all()
    
    alertas = []
    
    for orcamento in orcamentos:
        status = orcamento.get_status()
        
        if status == 'excedido':
            gasto = orcamento.get_gasto_atual()
            excesso = gasto - orcamento.limite
            alertas.append({
                'categoria': orcamento.categoria.nome,
                'tipo': 'excedido',
                'mensagem': f'Orçamento excedido em R$ {excesso:.2f}',
                'valor': f"{excesso:.2f}"
            })
        elif status == 'aviso':
            percentual = orcamento.get_percentual_usado()
            alertas.append({
                'categoria': orcamento.categoria.nome,
                'tipo': 'aviso',
                'mensagem': f'Atingiu {percentual:.0f}% do orçamento',
                'valor': f"{percentual:.0f}%"
            })
    
    return jsonify({
        'sucesso': True,
        'total_alertas': len(alertas),
        'alertas': alertas
    })
