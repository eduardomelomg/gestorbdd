from flask import Blueprint

bp = Blueprint("fichas", __name__, url_prefix="/fichas")

from app.blueprints.fichas import routes  # noqa: F401, E402
