from datetime import datetime, timezone
from app.extensions import db


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False, index=True)
    data_recebimento = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(20), nullable=False)
    # PIX / Dinheiro / Cartão / Transferência
    valor_recebido = db.Column(db.Numeric(10, 2), nullable=False)
    taxa_cartao = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pedido = db.relationship("Pedido", back_populates="pagamentos")

    def __repr__(self) -> str:
        return f"<Pagamento pedido={self.pedido_id} valor={self.valor_recebido}>"
