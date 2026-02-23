from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db


class Insumo(db.Model):
    __tablename__ = "insumos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    unidade = db.Column(db.String(10), nullable=False, default="g")          # g / kg / ml / l / un
    quantidade_embalagem_compra = db.Column(db.Numeric(10, 4), nullable=False)
    preco_compra_embalagem = db.Column(db.Numeric(10, 2), nullable=False)
    estoque_atual = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    estoque_minimo = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    compras = db.relationship("CompraInsumo", backref="insumo", lazy="dynamic")
    movimentacoes = db.relationship("MovimentacaoEstoque", backref="insumo", lazy="dynamic")
    ficha_itens = db.relationship("FichaTecnicaItem", backref="insumo", lazy="dynamic")

    @property
    def custo_unitario(self) -> Decimal:
        """Business Rule 1: custo_unitario = preco_compra_embalagem / quantidade_embalagem_compra"""
        if self.quantidade_embalagem_compra and self.quantidade_embalagem_compra != 0:
            return Decimal(str(self.preco_compra_embalagem)) / Decimal(str(self.quantidade_embalagem_compra))
        return Decimal("0")

    @property
    def estoque_baixo(self) -> bool:
        return Decimal(str(self.estoque_atual)) <= Decimal(str(self.estoque_minimo))

    def __repr__(self) -> str:
        return f"<Insumo {self.nome} [{self.unidade}]>"
