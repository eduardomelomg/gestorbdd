from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db


class Insumo(db.Model):
    __tablename__ = "insumos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    unidade = db.Column(db.String(10), nullable=False, default="g")          # g / kg / ml / l / un
    quantidade_embalagem_compra = db.Column(db.Numeric(10, 4), nullable=False, default=1)
    peso_por_embalagem = db.Column(db.Numeric(10, 4), nullable=False, default=1)
    preco_compra_embalagem = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estoque_atual = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    estoque_minimo = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships - Added cascades for hard delete
    compras = db.relationship("CompraInsumo", backref="insumo", lazy="dynamic", cascade="all, delete-orphan")
    movimentacoes = db.relationship("MovimentacaoEstoque", backref="insumo", lazy="dynamic", cascade="all, delete-orphan")
    ficha_itens = db.relationship("FichaTecnicaItem", backref="insumo", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def custo_unitario(self) -> Decimal:
        """
        Calculates cost per unit (g, ml, or un).
        Formula: (qty_packs * price_per_pack) / (qty_packs * weight_per_pack)
        Simplified: price_per_pack / weight_per_pack
        """
        if self.peso_por_embalagem and self.peso_por_embalagem != 0:
            return Decimal(str(self.preco_compra_embalagem)) / Decimal(str(self.peso_por_embalagem))
        return Decimal("0")

    @property
    def estoque_baixo(self) -> bool:
        return Decimal(str(self.estoque_atual)) <= Decimal(str(self.estoque_minimo))

    def __repr__(self) -> str:
        return f"<Insumo {self.nome} [{self.unidade}]>"
