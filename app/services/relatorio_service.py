"""
relatorio_service.py
====================
Cash-basis financial reporting.

CASH-BASIS CONVENTION (documented here):
  - 'Faturamento realizado' is computed using Pagamento.data_recebimento,
    NOT Pedido.data_pedido or data_hora_agendada.
  - Only status_pagamento == 'Pago' counts as fully realized revenue.
  - 'Parcial' orders contribute proportionally to realized revenue and profit.
  - 'Cancelado' or 'Estornado' orders are excluded entirely.
"""
from decimal import Decimal
from datetime import date

from sqlalchemy import select, func, extract
from app.extensions import db
from app.models.pedido import Pedido
from app.models.pagamento import Pagamento
from app.models.despesa import Despesa


def dashboard_mes(ano: int, mes: int) -> dict:
    """
    Returns all cash-basis KPIs for a given month.
    """
    # 1. Recebido no mês: all actual receipts recorded in this month
    recebido_mes = db.session.execute(
        select(func.coalesce(func.sum(Pagamento.valor_recebido), 0)).where(
            extract("year", Pagamento.data_recebimento) == ano,
            extract("month", Pagamento.data_recebimento) == mes,
        )
    ).scalar()

    # 2. Faturamento realizado: sum of total_pedido for fully PAID orders
    #    where the LAST payment fell in this month (cash basis by payment date).
    #    We use the max(data_recebimento) per pedido as the realization date.
    pago_subq = (
        select(
            Pagamento.pedido_id,
            func.max(Pagamento.data_recebimento).label("ultima_receita"),
        )
        .group_by(Pagamento.pedido_id)
        .subquery()
    )
    pedidos_pagos = db.session.execute(
        select(Pedido).join(
            pago_subq, Pedido.id == pago_subq.c.pedido_id
        ).where(
            Pedido.status_pagamento == "Pago",
            extract("year", pago_subq.c.ultima_receita) == ano,
            extract("month", pago_subq.c.ultima_receita) == mes,
        )
    ).scalars().all()

    faturamento_realizado = Decimal("0")
    lucro_realizado = Decimal("0")

    for p in pedidos_pagos:
        faturamento_realizado += p.total_pedido
        lucro_realizado += p.lucro_estimado

    # 3. Partial orders — proportional realization
    pedidos_parciais = db.session.execute(
        select(Pedido).where(
            Pedido.status_pagamento == "Parcial",
            Pedido.status_pedido != "Cancelado",
        )
    ).scalars().all()

    for p in pedidos_parciais:
        if p.total_pedido > 0:
            proporcao = p.soma_recebida / p.total_pedido
            faturamento_realizado += p.soma_recebida
            lucro_realizado += p.lucro_estimado * proporcao

    # 4. A receber: open orders not fully paid/canceled
    a_receber_rows = db.session.execute(
        select(Pedido).where(
            Pedido.status_pagamento.in_(["Não pago", "Parcial"]),
            Pedido.status_pedido != "Cancelado",
        )
    ).scalars().all()
    a_receber = sum(
        (p.total_pedido - p.soma_recebida for p in a_receber_rows), Decimal("0")
    )

    # 5. Despesas do mês
    despesas_mes = db.session.execute(
        select(func.coalesce(func.sum(Despesa.valor), 0)).where(
            extract("year", Despesa.data) == ano,
            extract("month", Despesa.data) == mes,
        )
    ).scalar()

    return {
        "recebido_mes": Decimal(str(recebido_mes)),
        "faturamento_realizado": faturamento_realizado,
        "lucro_realizado": lucro_realizado,
        "a_receber": a_receber,
        "despesas_mes": Decimal(str(despesas_mes)),
        "resultado_mes": Decimal(str(recebido_mes)) - Decimal(str(despesas_mes)),
    }


def pedidos_proximas_entregas(limite: int = 10) -> list[Pedido]:
    """Returns upcoming scheduled orders for the agenda dashboard card."""
    from datetime import datetime, timezone
    agora = datetime.now(timezone.utc)
    return db.session.execute(
        select(Pedido).where(
            Pedido.data_hora_agendada >= agora,
            Pedido.status_pedido.notin_(["Cancelado", "Entregue"]),
        ).order_by(Pedido.data_hora_agendada).limit(limite)
    ).scalars().all()


def insumos_estoque_baixo():
    """Returns insumos at or below minimum stock level."""
    from app.models.insumo import Insumo
    insumos = db.session.execute(
        select(Insumo).where(Insumo.ativo == True)
    ).scalars().all()
    return [i for i in insumos if i.estoque_baixo]
