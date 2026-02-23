from datetime import date
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.compras import bp
from app.extensions import db
from app.models.compra_insumo import CompraInsumo
from app.models.insumo import Insumo
from app.services.pedido_service import registrar_entrada_estoque
from app.blueprints.auth.decorators import admin_required


@bp.route("/")
@login_required
def listar():
    compras = db.session.execute(
        select(CompraInsumo).order_by(CompraInsumo.data_compra.desc())
    ).scalars().all()
    return render_template("compras/list.html", compras=compras)


@bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    insumos = db.session.execute(
        select(Insumo).where(Insumo.ativo == True).order_by(Insumo.nome)
    ).scalars().all()
    if request.method == "POST":
        compra = CompraInsumo(
            data_compra=date.fromisoformat(request.form["data_compra"]),
            fornecedor=request.form.get("fornecedor", ""),
            insumo_id=int(request.form["insumo_id"]),
            quantidade_comprada=float(request.form.get("quantidade_comprada", 0) or 0),
            custo_total=float(request.form.get("custo_total", 0) or 0),
            observacoes=request.form.get("observacoes", ""),
        )
        db.session.add(compra)
        db.session.flush()  # get compra.id
        registrar_entrada_estoque(compra)
        db.session.commit()
        flash("Compra registrada e estoque atualizado.", "success")
        return redirect(url_for("compras.listar"))
    return render_template("compras/form.html", insumos=insumos)


@bp.route("/<int:compra_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar(compra_id: int):
    compra = db.session.get(CompraInsumo, compra_id)
    if compra:
        # Reverse stock
        from decimal import Decimal
        compra.insumo.estoque_atual = (
            Decimal(str(compra.insumo.estoque_atual)) - Decimal(str(compra.quantidade_comprada))
        )
        db.session.delete(compra)
        db.session.commit()
        flash("Compra removida e estoque revertido.", "warning")
    return redirect(url_for("compras.listar"))
