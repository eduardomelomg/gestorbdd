from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.insumos import bp
from app.extensions import db
from app.models.insumo import Insumo
from app.blueprints.auth.decorators import admin_required


@bp.route("/")
@login_required
def listar():
    insumos = db.session.execute(select(Insumo).order_by(Insumo.nome)).scalars().all()
    return render_template("insumos/list.html", insumos=insumos)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        i = Insumo(
            nome=request.form["nome"],
            unidade=request.form.get("unidade", "g"),
            quantidade_embalagem_compra=float(request.form.get("quantidade_embalagem_compra", 1) or 1),
            peso_por_embalagem=float(request.form.get("peso_por_embalagem", 1) or 1),
            preco_compra_embalagem=float(request.form.get("preco_compra_embalagem", 0) or 0),
            estoque_atual=float(request.form.get("estoque_atual", 0) or 0),
            estoque_minimo=float(request.form.get("estoque_minimo", 0) or 0),
            minimo_em_embalagem=request.form.get("minimo_em_embalagem") == "true",
        )
        db.session.add(i)
        db.session.commit()
        flash(f"Insumo '{i.nome}' criado.", "success")
        return redirect(url_for("insumos.listar"))
    return render_template("insumos/form.html", insumo=None)


@bp.route("/<int:insumo_id>/editar", methods=["GET", "POST"])
@login_required
def editar(insumo_id: int):
    i = db.session.get(Insumo, insumo_id)
    if not i:
        abort(404)
    if request.method == "POST":
        i.nome = request.form["nome"]
        i.unidade = request.form.get("unidade", i.unidade)
        i.quantidade_embalagem_compra = float(request.form.get("quantidade_embalagem_compra", i.quantidade_embalagem_compra) or 1)
        i.peso_por_embalagem = float(request.form.get("peso_por_embalagem", i.peso_por_embalagem) or 1)
        i.preco_compra_embalagem = float(request.form.get("preco_compra_embalagem", i.preco_compra_embalagem) or 0)
        i.estoque_minimo = float(request.form.get("estoque_minimo", i.estoque_minimo) or 0)
        i.minimo_em_embalagem = request.form.get("minimo_em_embalagem") == "true"
        db.session.commit()
        flash(f"Insumo '{i.nome}' atualizado.", "success")
        return redirect(url_for("insumos.listar"))
    return render_template("insumos/form.html", insumo=i)


@bp.route("/<int:insumo_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar(insumo_id: int):
    i = db.session.get(Insumo, insumo_id)
    if i:
        nome = i.nome
        db.session.delete(i)
        db.session.commit()
        flash(f"Insumo '{nome}' removido permanentemente.", "success")
    return redirect(url_for("insumos.listar"))
