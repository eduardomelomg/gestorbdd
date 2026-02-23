from flask import Blueprint

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

from app.blueprints.pedidos import routes  # noqa: F401, E402
