import json
from datetime import datetime, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config_map

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map['default']))

    db.init_app(app)
    csrf.init_app(app)

    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.transacoes import bp as transacoes_bp
    from app.routes.categorias import bp as categorias_bp
    from app.routes.contas_fixas import bp as contas_fixas_bp
    from app.routes.orcamentos import bp as orcamentos_bp
    from app.routes.relatorios import bp as relatorios_bp
    from app.routes.cartoes import bp as cartoes_bp
    from app.routes.parcelamentos import bp as parcelamentos_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transacoes_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(contas_fixas_bp)
    app.register_blueprint(orcamentos_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(cartoes_bp)
    app.register_blueprint(parcelamentos_bp)

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    @app.context_processor
    def inject_categorias():
        from app.models import Categoria
        cats = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
        return {'categorias_json': json.dumps([c.to_dict() for c in cats])}

    with app.app_context():
        from app.models import Categoria
        db.create_all()
        if not Categoria.query.first():
            _seed_categories()

    return app


def _seed_categories():
    from app.models import Categoria
    receitas = [
        ('Salário', '#10b981'),
        ('Freelance', '#06b6d4'),
        ('Investimentos', '#f59e0b'),
        ('Outras Receitas', '#8b5cf6'),
    ]
    despesas = [
        ('Moradia', '#ef4444'),
        ('Alimentação', '#f97316'),
        ('Transporte', '#eab308'),
        ('Saúde', '#ec4899'),
        ('Educação', '#6366f1'),
        ('Lazer', '#14b8a6'),
        ('Assinaturas', '#a855f7'),
        ('Compras', '#f43f5e'),
        ('Cartão de Crédito', '#78716c'),
        ('Outras Despesas', '#64748b'),
    ]
    for nome, cor in receitas:
        db.session.add(Categoria(nome=nome, tipo='receita', cor=cor))
    for nome, cor in despesas:
        db.session.add(Categoria(nome=nome, tipo='despesa', cor=cor))
    db.session.commit()
