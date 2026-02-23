import os
from flask import Flask
from app.config import config_map
from app.extensions import db, migrate, login_manager, csrf
from app.models import (  # noqa: F401 — registers all models with SQLAlchemy
    Usuario, Cliente, Produto, Insumo, CompraInsumo,
    FichaTecnica, FichaTecnicaItem, Pedido, PedidoItem,
    Pagamento, Despesa, MovimentacaoEstoque
)


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_map[config_name])
    app.jinja_env.add_extension('jinja2.ext.do')

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.main import bp as main_bp
    from app.blueprints.pedidos import bp as pedidos_bp
    from app.blueprints.clientes import bp as clientes_bp
    from app.blueprints.produtos import bp as produtos_bp
    from app.blueprints.insumos import bp as insumos_bp
    from app.blueprints.fichas import bp as fichas_bp
    from app.blueprints.compras import bp as compras_bp
    from app.blueprints.financeiro import bp as financeiro_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(insumos_bp)
    app.register_blueprint(fichas_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(financeiro_bp)

    # CLI commands
    from app.cli import register_commands
    register_commands(app)

    # Jinja2 filters
    from app.filters import register_filters
    register_filters(app)

    return app
