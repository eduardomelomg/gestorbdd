from flask import Blueprint

bp = Blueprint("insumos", __name__, url_prefix="/insumos")

from app.blueprints.insumos import routes  # noqa: F401, E402
