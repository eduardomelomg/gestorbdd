from datetime import datetime, timezone
from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="Pessoa")       # Pessoa / Empresa
    canal_preferencial = db.Column(db.String(10), nullable=False, default="B2C")  # B2C / B2B
    telefone = db.Column(db.String(30))
    endereco = db.Column(db.Text)
    documento = db.Column(db.String(30))                                    # CPF or CNPJ
    tabela_preco = db.Column(db.String(20), nullable=False, default="Varejo")  # Varejo / Atacado
    prazo_pagamento_dias = db.Column(db.Integer, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    pedidos = db.relationship("Pedido", backref="cliente", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Cliente {self.nome}>"
