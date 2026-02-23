from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.fichas import bp
from app.extensions import db
from app.models.produto import Produto
from app.models.ficha_tecnica import FichaTecnica, FichaTecnicaItem
from app.models.insumo import Insumo
from app.services.ficha_service import resumo_ficha


@bp.route("/")
@login_required
def listar():
    produtos = db.session.execute(select(Produto).where(Produto.ativo == True).order_by(Produto.nome)).scalars().all()
    return render_template("fichas/list.html", produtos=produtos)


@bp.route("/<int:produto_id>", methods=["GET", "POST"])
@login_required
def editar(produto_id: int):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
    insumos = db.session.execute(select(Insumo).where(Insumo.ativo == True).order_by(Insumo.nome)).scalars().all()

    # Create ficha if it doesn't exist yet
    ficha = produto.ficha_tecnica
    if not ficha:
        ficha = FichaTecnica(produto_id=produto_id, rendimento_unidades=1,
                             mao_de_obra_total=0, perdas_percentual=0, margem_desejada_percentual=60)
        db.session.add(ficha)
        db.session.commit()

    if request.method == "POST":
        action = request.form.get("action", "save")

        if action == "save_header":
            ficha.rendimento_unidades = float(request.form.get("rendimento_unidades", ficha.rendimento_unidades) or 1)
            ficha.mao_de_obra_total = float(request.form.get("mao_de_obra_total", ficha.mao_de_obra_total) or 0)
            ficha.perdas_percentual = float(request.form.get("perdas_percentual", ficha.perdas_percentual) or 0)
            ficha.margem_desejada_percentual = float(request.form.get("margem_desejada_percentual", ficha.margem_desejada_percentual) or 60)
            db.session.commit()
            flash("Ficha técnica atualizada.", "success")

        elif action == "add_item":
            insumo_id = int(request.form.get("insumo_id"))
            qtd = float(request.form.get("quantidade_por_receita", 0) or 0)
            tipo = request.form.get("tipo_item", "Insumo")
            item = FichaTecnicaItem(
                ficha_tecnica_id=ficha.id,
                insumo_id=insumo_id,
                quantidade_por_receita=qtd,
                tipo_item=tipo,
            )
            db.session.add(item)
            db.session.commit()
            flash("Item adicionado.", "success")

        elif action == "remove_item":
            item_id = int(request.form.get("item_id"))
            item = db.session.get(FichaTecnicaItem, item_id)
            if item and item.ficha_tecnica_id == ficha.id:
                db.session.delete(item)
                db.session.commit()
                flash("Item removido.", "success")

        return redirect(url_for("fichas.editar", produto_id=produto_id))

    resumo = resumo_ficha(ficha)
    return render_template("fichas/edit.html", produto=produto, ficha=ficha,
                           insumos=insumos, resumo=resumo)
