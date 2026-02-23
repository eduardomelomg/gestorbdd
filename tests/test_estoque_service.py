"""test_estoque_service.py — Business Rule 5 stock deduction tests."""
from decimal import Decimal
import pytest
from datetime import date
from app.extensions import db
from app.models.pedido import Pedido, PedidoItem
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.insumo import Insumo
from app.services.pedido_service import mudar_status_pedido, gerar_numero_pedido


def test_stock_deduction_on_producao(app):
    """Moving pedido to Em produção must deduct insumos via ficha técnica."""
    with app.app_context():
        cliente = db.session.execute(db.select(Cliente)).scalar()
        produto = db.session.execute(db.select(Produto)).scalar()
        insumo = db.session.execute(db.select(Insumo)).scalar()

        estoque_antes = Decimal(str(insumo.estoque_atual))

        pedido = Pedido(
            numero_pedido=gerar_numero_pedido(),
            cliente_id=cliente.id,
            canal="B2C",
            data_pedido=date.today(),
            status_pedido="Agendado",
            status_pagamento="Não pago",
            desconto=0, taxa_entrega=0,
        )
        db.session.add(pedido)
        db.session.flush()
        db.session.add(PedidoItem(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=1,
            preco_unitario=produto.preco_varejo,
        ))
        db.session.flush()

        mudar_status_pedido(pedido, "Em produção", usuario_is_admin=False)

        # Insumo should have decreased
        assert Decimal(str(insumo.estoque_atual)) < estoque_antes
        db.session.rollback()


def test_negative_stock_raises(app):
    """Without admin override, negative stock must raise ValueError."""
    with app.app_context():
        insumo = db.session.execute(db.select(Insumo)).scalar()
        cliente = db.session.execute(db.select(Cliente)).scalar()
        produto = db.session.execute(db.select(Produto)).scalar()

        # Drain stock to zero
        insumo.estoque_atual = 0
        db.session.flush()

        pedido = Pedido(
            numero_pedido=gerar_numero_pedido(),
            cliente_id=cliente.id,
            canal="B2C",
            data_pedido=date.today(),
            status_pedido="Agendado",
            status_pagamento="Não pago",
            desconto=0, taxa_entrega=0,
        )
        db.session.add(pedido)
        db.session.flush()
        db.session.add(PedidoItem(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=100,  # large quantity to guarantee negative
            preco_unitario=produto.preco_varejo,
        ))
        db.session.flush()

        with pytest.raises(ValueError, match="Estoque insuficiente"):
            mudar_status_pedido(pedido, "Em produção", usuario_is_admin=False)
        db.session.rollback()
