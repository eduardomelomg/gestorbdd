from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db


class FichaTecnica(db.Model):
    __tablename__ = "fichas_tecnicas"

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), unique=True, nullable=False, index=True)
    rendimento_unidades = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    mao_de_obra_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    perdas_percentual = db.Column(db.Numeric(5, 2), nullable=False, default=0)   # e.g. 10 = 10%
    margem_desejada_percentual = db.Column(db.Numeric(5, 2), nullable=False, default=60)
    ultima_atualizacao = db.Column(db.DateTime(timezone=True),
                                   default=lambda: datetime.now(timezone.utc),
                                   onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    produto = db.relationship("Produto", back_populates="ficha_tecnica")
    itens = db.relationship("FichaTecnicaItem", back_populates="ficha_tecnica",
                            cascade="all, delete-orphan", lazy="select")

    # ---- Computed properties (Business Rule 2) ----
    @property
    def custo_total_insumos(self) -> Decimal:
        return sum((Decimal(str(i.custo_item)) for i in self.itens), Decimal("0"))

    @property
    def custo_total_receita(self) -> Decimal:
        base = self.custo_total_insumos + Decimal(str(self.mao_de_obra_total))
        return base * (1 + Decimal(str(self.perdas_percentual)) / 100)

    @property
    def custo_unitario(self) -> Decimal:
        if self.rendimento_unidades and Decimal(str(self.rendimento_unidades)) != 0:
            return self.custo_total_receita / Decimal(str(self.rendimento_unidades))
        return Decimal("0")

    @property
    def preco_sugerido(self) -> Decimal:
        margem = Decimal(str(self.margem_desejada_percentual)) / 100
        if margem >= 1:
            return Decimal("0")
        return self.custo_unitario / (1 - margem)

    @property
    def lucro_unitario_atual(self) -> Decimal:
        """Profit per unit based on the current product price."""
        if self.produto and self.produto.preco_varejo:
            return Decimal(str(self.produto.preco_varejo)) - self.custo_unitario
        return Decimal("0")

    @property
    def margem_atual_percentual(self) -> Decimal:
        """Actual margin percentage based on the product's current retail price."""
        if self.produto and self.produto.preco_varejo and self.produto.preco_varejo > 0:
            lucro = self.lucro_unitario_atual
            return (lucro / Decimal(str(self.produto.preco_varejo))) * 100
        return Decimal("0")

    @property
    def markup_atual(self) -> Decimal:
        """Markup factor (Price / Cost)."""
        if self.custo_unitario > 0 and self.produto and self.produto.preco_varejo:
            return Decimal(str(self.produto.preco_varejo)) / self.custo_unitario
        return Decimal("0")

    # Wholesale Simulation
    @property
    def lucro_unitario_atacado(self) -> Decimal:
        if self.produto and self.produto.preco_atacado:
            return Decimal(str(self.produto.preco_atacado)) - self.custo_unitario
        return Decimal("0")

    @property
    def margem_atacado_percentual(self) -> Decimal:
        if self.produto and self.produto.preco_atacado and self.produto.preco_atacado > 0:
            return (self.lucro_unitario_atacado / Decimal(str(self.produto.preco_atacado))) * 100
        return Decimal("0")

    @property
    def markup_atacado(self) -> Decimal:
        if self.custo_unitario > 0 and self.produto and self.produto.preco_atacado:
            return Decimal(str(self.produto.preco_atacado)) / self.custo_unitario
        return Decimal("0")

    def __repr__(self) -> str:
        return f"<FichaTecnica produto_id={self.produto_id}>"


class FichaTecnicaItem(db.Model):
    __tablename__ = "ficha_tecnica_itens"

    id = db.Column(db.Integer, primary_key=True)
    ficha_tecnica_id = db.Column(db.Integer, db.ForeignKey("fichas_tecnicas.id"),
                                 nullable=False, index=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumos.id"), nullable=False, index=True)
    quantidade_por_receita = db.Column(db.Numeric(12, 4), nullable=False)
    tipo_item = db.Column(db.String(20), nullable=False, default="Insumo")  # Insumo / Embalagem

    # Relationships
    ficha_tecnica = db.relationship("FichaTecnica", back_populates="itens")

    @property
    def custo_item(self) -> Decimal:
        """custo_item = insumo.custo_unitario × quantidade_por_receita"""
        return self.insumo.custo_unitario * Decimal(str(self.quantidade_por_receita))

    def __repr__(self) -> str:
        return f"<FichaTecnicaItem ficha={self.ficha_tecnica_id} insumo={self.insumo_id}>"
