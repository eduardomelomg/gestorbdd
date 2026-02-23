from datetime import datetime, timezone
from app.extensions import db


class Despesa(db.Model):
    __tablename__ = "despesas"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(30), nullable=False)
    # Insumos / Embalagens / Entregas / Marketing / Aluguel / Água / Luz / Outros
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    forma_pagamento = db.Column(db.String(20), nullable=False)
    # PIX / Dinheiro / Cartão / Boleto / Transferência
    recorrente = db.Column(db.Boolean, nullable=False, default=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Despesa {self.data} {self.categoria} R${self.valor}>"
