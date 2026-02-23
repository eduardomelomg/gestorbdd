from datetime import datetime, timezone
from app.extensions import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    categoria = db.Column(db.String(30), nullable=False, default="Brownie")  # Brownie / Bebida / Outro
    unidade_venda = db.Column(db.String(10), nullable=False, default="un")   # un / caixa
    preco_varejo = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    preco_atacado = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    ficha_tecnica = db.relationship("FichaTecnica", back_populates="produto",
                                    uselist=False, cascade="all, delete-orphan")
    pedido_itens = db.relationship("PedidoItem", backref="produto", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Produto {self.sku} - {self.nome}>"
