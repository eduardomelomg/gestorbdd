"""test_ficha_service.py — Business Rule 2 computation tests."""
from decimal import Decimal
import pytest


def test_custo_unitario_insumo(app):
    """Business Rule 1: custo_unitario = preco / qty_embalagem."""
    with app.app_context():
        from app.models.insumo import Insumo
        from app.extensions import db
        ins = db.session.execute(db.select(Insumo)).scalar()
        # 30.00 / 1000g = 0.03 per g
        assert ins.custo_unitario == Decimal("30.00") / Decimal("1000")


def test_ficha_custo_unitario(app):
    """Business Rule 2: checks ficha custo_unitario formula."""
    with app.app_context():
        from app.models.ficha_tecnica import FichaTecnica
        from app.models.insumo import Insumo
        from app.extensions import db
        ficha = db.session.execute(db.select(FichaTecnica)).scalar()
        # custo_insumo: 200g × 0.03 = 6.00
        # + mao de obra 10.00 = 16.00
        # + perdas 5% = 16.80
        # / 12 = 1.40
        assert ficha.custo_unitario == pytest.approx(Decimal("1.40"), rel=Decimal("0.01"))


def test_ficha_preco_sugerido(app):
    """Business Rule 2: preco_sugerido = custo_unitario / (1 - margem)."""
    with app.app_context():
        from app.models.ficha_tecnica import FichaTecnica
        from app.extensions import db
        ficha = db.session.execute(db.select(FichaTecnica)).scalar()
        # margem = 60% => / 0.40
        expected = ficha.custo_unitario / Decimal("0.40")
        assert abs(ficha.preco_sugerido - expected) < Decimal("0.01")
