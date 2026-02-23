from decimal import Decimal
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Operador")  # Admin / Operador
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    pedidos = db.relationship("Pedido", backref="criado_por", lazy="dynamic",
                              foreign_keys="Pedido.created_by")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "Admin"

    def __repr__(self) -> str:
        return f"<Usuario {self.email} [{self.role}]>"


@login_manager.user_loader
def load_user(user_id: str) -> Usuario | None:
    return db.session.get(Usuario, int(user_id))
