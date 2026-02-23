from datetime import datetime, timezone
from flask import render_template
from flask_login import login_required
from sqlalchemy import select
from . import bp
from app.services.relatorio_service import (
    dashboard_mes, pedidos_proximas_entregas, insumos_estoque_baixo
)


@bp.route("/")
@login_required
def dashboard():
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_nome = meses_pt[now.month]
    return render_template(
        "main/dashboard.html",
        kpis=kpis,
        proximas=proximas,
        alertas=alertas,
        mes_atual=f"{mes_nome} - {now.year}",
    )


@bp.route("/agenda")
@login_required
def agenda():
    from sqlalchemy import select
    from app.models.pedido import Pedido
    from app.extensions import db

    status_filter = None
    from flask import request
    data_filter = request.args.get("data")
    status_filter = request.args.get("status")

    query = select(Pedido).where(
        Pedido.status_pedido.notin_(["Cancelado"])
    ).order_by(Pedido.data_hora_agendada)

    if data_filter:
        from datetime import date
        try:
            d = date.fromisoformat(data_filter)
            query = query.where(
                Pedido.data_hora_agendada >= datetime(d.year, d.month, d.day, 0, 0, tzinfo=timezone.utc),
                Pedido.data_hora_agendada < datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc),
            )
        except ValueError:
            pass

    if status_filter:
        query = query.where(Pedido.status_pedido == status_filter)

    pedidos = db.session.execute(query).scalars().all()
    return render_template("main/agenda.html", pedidos=pedidos,
                           data_filter=data_filter, status_filter=status_filter)
