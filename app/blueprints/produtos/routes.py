from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.produtos import bp
from app.extensions import db
from app.models.produto import Produto
from app.blueprints.auth.decorators import admin_required


@bp.route("/")
@login_required
def listar():
    produtos = db.session.execute(select(Produto).order_by(Produto.nome)).scalars().all()
    return render_template("produtos/list.html", produtos=produtos)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        p = Produto(
            nome=request.form["nome"],
            sku=request.form["sku"],
            categoria=request.form.get("categoria", "Brownie"),
            unidade_venda=request.form.get("unidade_venda", "un"),
            preco_varejo=float(request.form.get("preco_varejo", 0) or 0),
            preco_atacado=float(request.form.get("preco_atacado", 0) or 0),
        )
        db.session.add(p)
        db.session.commit()
        flash(f"Produto '{p.nome}' criado.", "success")
        return redirect(url_for("produtos.listar"))
    return render_template("produtos/form.html", produto=None)


@bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
@login_required
def editar(produto_id: int):
    p = db.session.get(Produto, produto_id)
    if not p:
        abort(404)
    if request.method == "POST":
        p.nome = request.form["nome"]
        p.sku = request.form["sku"]
        p.categoria = request.form.get("categoria", p.categoria)
        p.unidade_venda = request.form.get("unidade_venda", p.unidade_venda)
        p.preco_varejo = float(request.form.get("preco_varejo", p.preco_varejo) or 0)
        p.preco_atacado = float(request.form.get("preco_atacado", p.preco_atacado) or 0)
        p.ativo = "ativo" in request.form
        db.session.commit()
        flash(f"Produto '{p.nome}' atualizado.", "success")
        return redirect(url_for("produtos.listar"))
    return render_template("produtos/form.html", produto=p)


@bp.route("/<int:produto_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar(produto_id: int):
    p = db.session.get(Produto, produto_id)
    if p:
        nome = p.nome
        db.session.delete(p)
        db.session.commit()
        flash(f"Produto '{nome}' removido permanentemente.", "success")
    return redirect(url_for("produtos.listar"))
