from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(20), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    canal = db.Column(db.String(10), nullable=False, default="B2C")   # B2C / B2B
    data_pedido = db.Column(db.Date, nullable=False)
    data_hora_agendada = db.Column(db.DateTime(timezone=True), index=True)
    tipo_entrega = db.Column(db.String(20), nullable=False, default="Retirada")  # Retirada / Entrega
    endereco_entrega = db.Column(db.Text)
    status_pedido = db.Column(db.String(30), nullable=False, default="Rascunho")
    # Rascunho / Agendado / Em produção / Pronto / Entregue / Cancelado
    status_pagamento = db.Column(db.String(20), nullable=False, default="Não pago")
    # Não pago / Parcial / Pago / Estornado
    desconto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    taxa_entrega = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    itens = db.relationship("PedidoItem", back_populates="pedido",
                            cascade="all, delete-orphan", lazy="select")
    pagamentos = db.relationship("Pagamento", back_populates="pedido",
                                 cascade="all, delete-orphan", lazy="select")
    movimentacoes = db.relationship("MovimentacaoEstoque", backref="pedido", lazy="dynamic",
                                    foreign_keys="MovimentacaoEstoque.pedido_id")

    # ---- Computed properties (Business Rules 3 & 4) ----
    @property
    def subtotal(self) -> Decimal:
        return sum((Decimal(str(i.total_item)) for i in self.itens), Decimal("0"))

    @property
    def total_pedido(self) -> Decimal:
        return self.subtotal - Decimal(str(self.desconto)) + Decimal(str(self.taxa_entrega))

    @property
    def custo_estimado(self) -> Decimal:
        custo_itens = sum((Decimal(str(i.custo_item)) for i in self.itens), Decimal("0"))
        taxa_cartao = sum((Decimal(str(p.taxa_cartao)) for p in self.pagamentos), Decimal("0"))
        return custo_itens + taxa_cartao

    @property
    def lucro_estimado(self) -> Decimal:
        return self.total_pedido - self.custo_estimado

    @property
    def soma_recebida(self) -> Decimal:
        return sum((Decimal(str(p.valor_recebido)) for p in self.pagamentos), Decimal("0"))

    def __repr__(self) -> str:
        return f"<Pedido {self.numero_pedido} [{self.status_pedido}]>"


class PedidoItem(db.Model):
    __tablename__ = "pedido_itens"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False, index=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship("Pedido", back_populates="itens")

    @property
    def total_item(self) -> Decimal:
        return Decimal(str(self.quantidade)) * Decimal(str(self.preco_unitario))

    @property
    def custo_item(self) -> Decimal:
        """Custo via ficha técnica; falls back to 0 if no ficha exists."""
        ficha = self.produto.ficha_tecnica
        if ficha:
            return ficha.custo_unitario * Decimal(str(self.quantidade))
        return Decimal("0")

    def __repr__(self) -> str:
        return f"<PedidoItem pedido={self.pedido_id} produto={self.produto_id}>"
