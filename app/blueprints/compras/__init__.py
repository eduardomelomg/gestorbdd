from flask import Blueprint

bp = Blueprint("compras", __name__, url_prefix="/compras")

from app.blueprints.compras import routes  # noqa: F401, E402
