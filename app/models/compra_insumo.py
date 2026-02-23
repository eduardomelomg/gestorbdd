from datetime import datetime, timezone
from app.extensions import db


class CompraInsumo(db.Model):
    __tablename__ = "compras_insumos"

    id = db.Column(db.Integer, primary_key=True)
    data_compra = db.Column(db.Date, nullable=False)
    fornecedor = db.Column(db.String(150))
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumos.id"), nullable=False, index=True)
    quantidade_comprada = db.Column(db.Numeric(12, 4), nullable=False)
    custo_total = db.Column(db.Numeric(10, 2), nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<CompraInsumo {self.id} - insumo_id={self.insumo_id}>"
