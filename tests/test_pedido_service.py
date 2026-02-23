"""
test_pedido_service.py
======================
Tests for the cash-basis payment logic (Business Rules 3 & 4).
"""
from decimal import Decimal
from datetime import date
from app.extensions import db
from app.models.pedido import Pedido, PedidoItem
from app.models.pagamento import Pagamento
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.services.pedido_service import atualizar_status_pagamento, gerar_numero_pedido


def test_status_pago_fluxo(app):
    """Integrated test for payment status transitions."""
    with app.app_context():
        cliente = db.session.execute(db.select(Cliente)).scalar()
        produto = db.session.execute(db.select(Produto)).scalar()
        
        pedido = Pedido(
            numero_pedido=gerar_numero_pedido(),
            cliente_id=cliente.id,
            canal="B2C",
            data_pedido=date.today(),
            status_pedido="Agendado",
            status_pagamento="Não pago",
            desconto=0,
            taxa_entrega=0,
        )
        db.session.add(pedido)
        db.session.flush()
        
        item = PedidoItem(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=10,
            preco_unitario=12.00,
        )
        db.session.add(item)
        db.session.flush()
        
        # 1. Check Not Paid
        atualizar_status_pagamento(pedido)
        assert pedido.status_pagamento == "Não pago"
        
        # 2. Add partial payment (total is 120.00)
        pag1 = Pagamento(
            pedido_id=pedido.id,
            data_recebimento=date.today(),
            forma_pagamento="PIX",
            valor_recebido=50.00,
        )
        db.session.add(pag1)
        db.session.flush()
        db.session.expire_all() # Force reload on access
        atualizar_status_pagamento(pedido)
        assert pedido.status_pagamento == "Parcial"
        
        # 3. Add full payment (remaining 70.00)
        pag2 = Pagamento(
            pedido_id=pedido.id,
            data_recebimento=date.today(),
            forma_pagamento="PIX",
            valor_recebido=70.00,
        )
        db.session.add(pag2)
        db.session.flush()
        db.session.expire_all()
        atualizar_status_pagamento(pedido)
        assert pedido.status_pagamento == "Pago"


def test_numero_pedido_format(app):
    with app.app_context():
        nr = gerar_numero_pedido()
        assert nr.startswith("BD-")
        assert len(nr) > 6


def test_totals_computation(app):
    with app.app_context():
        cliente = db.session.execute(db.select(Cliente)).scalar()
        produto = db.session.execute(db.select(Produto)).scalar()
        
        pedido = Pedido(
            numero_pedido="CALC",
            cliente_id=cliente.id,
            canal="B2C",
            data_pedido=date.today(),
            status_pedido="Rascunho",
            status_pagamento="Não pago",
            desconto=Decimal("5.00"),
            taxa_entrega=Decimal("10.00"),
        )
        db.session.add(pedido)
        db.session.flush()
        # 2 items of 12.00 = 24.00
        item = PedidoItem(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=Decimal("2"),
            preco_unitario=Decimal("12.00"),
        )
        db.session.add(item)
        db.session.flush()
        
        # subtotal = 24.00
        # total = 24 - 5 + 10 = 29
        assert pedido.subtotal == Decimal("24.00")
        assert pedido.total_pedido == Decimal("29.00")
