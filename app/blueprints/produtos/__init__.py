from flask import Blueprint

bp = Blueprint("produtos", __name__, url_prefix="/produtos")

from app.blueprints.produtos import routes  # noqa: F401, E402
