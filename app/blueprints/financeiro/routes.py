from datetime import date, datetime, timezone
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.financeiro import bp
from app.extensions import db
from app.models.despesa import Despesa
from app.models.pagamento import Pagamento
from app.services.relatorio_service import dashboard_mes
from app.blueprints.auth.decorators import admin_required


@bp.route("/")
@login_required
def index():
    now = datetime.now(timezone.utc)
    ano = int(request.args.get("ano", now.year))
    mes = int(request.args.get("mes", now.month))

    kpis = dashboard_mes(ano, mes)

    # Last 30 payments
    pagamentos = db.session.execute(
        select(Pagamento).order_by(Pagamento.data_recebimento.desc()).limit(50)
    ).scalars().all()

    # Despesas of selected month
    despesas = db.session.execute(
        select(Despesa).where(
            Despesa.data >= date(ano, mes, 1),
            Despesa.data <= date(ano, mes, 28) if mes == 2 else
            date(ano, mes, 30) if mes in [4, 6, 9, 11] else date(ano, mes, 31),
        ).order_by(Despesa.data.desc())
    ).scalars().all()

    return render_template(
        "financeiro/index.html",
        kpis=kpis, pagamentos=pagamentos, despesas=despesas,
        ano=ano, mes=mes,
    )


@bp.route("/despesa/nova", methods=["GET", "POST"])
@login_required
def nova_despesa():
    if request.method == "POST":
        d = Despesa(
            data=date.fromisoformat(request.form["data"]),
            categoria=request.form["categoria"],
            descricao=request.form["descricao"],
            valor=float(request.form.get("valor", 0) or 0),
            forma_pagamento=request.form["forma_pagamento"],
            recorrente="recorrente" in request.form,
            observacoes=request.form.get("observacoes", ""),
        )
        db.session.add(d)
        db.session.commit()
        flash("Despesa registrada.", "success")
        return redirect(url_for("financeiro.index"))
    return render_template("financeiro/despesa_form.html")


@bp.route("/despesa/<int:despesa_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar_despesa(despesa_id: int):
    d = db.session.get(Despesa, despesa_id)
    if d:
        db.session.delete(d)
        db.session.commit()
        flash("Despesa removida.", "success")
    return redirect(url_for("financeiro.index"))
