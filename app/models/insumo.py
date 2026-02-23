from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db


class Insumo(db.Model):
    __tablename__ = "insumos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    unidade = db.Column(db.String(10), nullable=False, default="g")          # g / kg / ml / l / un
    quantidade_embalagem_compra = db.Column(db.Numeric(12, 2), nullable=False, default=1)
    peso_por_embalagem = db.Column(db.Numeric(12, 2), nullable=False, default=1)
    preco_compra_embalagem = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estoque_atual = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estoque_minimo = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    minimo_em_embalagem = db.Column(db.Boolean, nullable=False, default=True)
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
    def estoque_embalagens(self) -> Decimal:
        """Calculates current stock in number of packs/units."""
        if self.peso_por_embalagem and self.peso_por_embalagem > 0:
            return Decimal(str(self.estoque_atual)) / Decimal(str(self.peso_por_embalagem))
        return Decimal("0")

    @property
    def estoque_minimo_valor_base(self) -> Decimal:
        """
        Calculates minimum stock requirement in base unit.
        - If minimo_em_embalagem is True, multiplies estoque_minimo by weight per pack.
        - Otherwise, treats estoque_minimo as a value in base units.
        """
        if self.minimo_em_embalagem:
            return Decimal(str(self.estoque_minimo)) * Decimal(str(self.peso_por_embalagem))
        return Decimal(str(self.estoque_minimo))

    @property
    def estoque_baixo(self) -> bool:
        """Checks if current stock (base unit) is below minimum (calculated in base unit)."""
        return Decimal(str(self.estoque_atual)) <= self.estoque_minimo_valor_base

    def __repr__(self) -> str:
        return f"<Insumo {self.nome} [{self.unidade}]>"
