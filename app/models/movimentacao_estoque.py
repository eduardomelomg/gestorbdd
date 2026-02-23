from datetime import datetime, timezone
from app.extensions import db


class MovimentacaoEstoque(db.Model):
    __tablename__ = "movimentacoes_estoque"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)       # Entrada / Saida / Ajuste
    origem = db.Column(db.String(20), nullable=False)     # Compra / Producao / Manual
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumos.id"), nullable=False, index=True)
    quantidade = db.Column(db.Numeric(12, 4), nullable=False)  # positive = in, negative = out
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=True, index=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("compras_insumos.id"), nullable=True)
    observacoes = db.Column(db.Text)

    def __repr__(self) -> str:
        return f"<MovimentacaoEstoque {self.tipo} insumo={self.insumo_id} qty={self.quantidade}>"
