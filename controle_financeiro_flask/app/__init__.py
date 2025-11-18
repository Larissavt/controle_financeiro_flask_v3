"""
Aplicativo de Controle Financeiro Pessoal
Desenvolvido com Flask e SQLite
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Inicializar a extensão SQLAlchemy
db = SQLAlchemy()


def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração do banco de dados
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "controle_financeiro.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui_mude_em_producao'
    
    # Inicializar a extensão do banco de dados com a app
    db.init_app(app)
    
    # Registrar os modelos
    from app.models import Usuario, Categoria, Transacao, Receita, Despesa
    
    # Registrar os blueprints
    from app.routes import auth_bp, dashboard_bp, categorias_bp, transacoes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(transacoes_bp)
    
    # Criar as tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
