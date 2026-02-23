from datetime import date, datetime, timezone
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import select
from . import bp
from app.extensions import db
from app.models.pedido import Pedido, PedidoItem
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.pagamento import Pagamento
from app.blueprints.auth.decorators import admin_required
from app.services.pedido_service import (
    gerar_numero_pedido, atualizar_status_pagamento, mudar_status_pedido
)


@bp.route("/")
@login_required
def listar():
    status = request.args.get("status", "")
    query = select(Pedido).order_by(Pedido.data_hora_agendada.desc().nullslast(), Pedido.id.desc())
    if status:
        query = query.where(Pedido.status_pedido == status)
    pedidos = db.session.execute(query).scalars().all()
    return render_template("pedidos/list.html", pedidos=pedidos, status_filter=status)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    clientes = db.session.execute(select(Cliente).where(Cliente.ativo == True)).scalars().all()
    produtos = db.session.execute(select(Produto).where(Produto.ativo == True)).scalars().all()
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        data_agendada_str = request.form.get("data_hora_agendada")
        tipo_entrega = request.form.get("tipo_entrega", "Retirada")
        endereco_entrega = request.form.get("endereco_entrega", "")
        canal = request.form.get("canal", "B2C")
        desconto = float(request.form.get("desconto", 0) or 0)
        taxa_entrega = float(request.form.get("taxa_entrega", 0) or 0)
        observacoes = request.form.get("observacoes", "")

        pedido = Pedido(
            numero_pedido=gerar_numero_pedido(),
            cliente_id=int(cliente_id),
            canal=canal,
            data_pedido=date.today(),
            tipo_entrega=tipo_entrega,
            endereco_entrega=endereco_entrega,
            desconto=desconto,
            taxa_entrega=taxa_entrega,
            status_pedido="Rascunho",
            status_pagamento="Não pago",
            observacoes=observacoes,
            created_by=current_user.id,
        )

        if data_agendada_str:
            try:
                pedido.data_hora_agendada = datetime.fromisoformat(data_agendada_str).replace(tzinfo=timezone.utc)
                pedido.status_pedido = "Agendado"
            except ValueError:
                pass

        db.session.add(pedido)
        db.session.flush()  # get pedido.id before adding items

        # Items
        produto_ids = request.form.getlist("produto_id[]")
        quantidades = request.form.getlist("quantidade[]")
        precos = request.form.getlist("preco_unitario[]")

        for pid, qty, preco in zip(produto_ids, quantidades, precos):
            if pid and qty and preco:
                item = PedidoItem(
                    pedido_id=pedido.id,
                    produto_id=int(pid),
                    quantidade=float(qty),
                    preco_unitario=float(preco),
                )
                db.session.add(item)

        db.session.commit()
        flash(f"Pedido {pedido.numero_pedido} criado com sucesso!", "success")
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))

    return render_template("pedidos/novo.html", clientes=clientes, produtos=produtos)


@bp.route("/<int:pedido_id>")
@login_required
def detalhe(pedido_id: int):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    return render_template("pedidos/detail.html", pedido=pedido)


@bp.route("/<int:pedido_id>/status", methods=["POST"])
@login_required
def mudar_status(pedido_id: int):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    novo_status = request.form.get("status")
    try:
        warnings = mudar_status_pedido(
            pedido, novo_status, usuario_is_admin=current_user.is_admin
        )
        db.session.commit()
        for w in warnings:
            flash(w, "warning")
        flash(f"Status atualizado para '{novo_status}'.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido_id))


@bp.route("/<int:pedido_id>/pagamento", methods=["POST"])
@login_required
def adicionar_pagamento(pedido_id: int):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    data_rec = request.form.get("data_recebimento")
    forma = request.form.get("forma_pagamento")
    valor = float(request.form.get("valor_recebido", 0) or 0)
    taxa = float(request.form.get("taxa_cartao", 0) or 0)
    obs = request.form.get("observacoes", "")

    pag = Pagamento(
        pedido_id=pedido_id,
        data_recebimento=date.fromisoformat(data_rec),
        forma_pagamento=forma,
        valor_recebido=valor,
        taxa_cartao=taxa,
        observacoes=obs,
    )
    db.session.add(pag)
    db.session.flush()
    atualizar_status_pagamento(pedido)
    db.session.commit()
    flash(f"Pagamento de R$ {valor:.2f} registrado. Status: {pedido.status_pagamento}", "success")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido_id))


@bp.route("/pagamento/<int:pagamento_id>/editar", methods=["POST"])
@login_required
def editar_pagamento(pagamento_id: int):
    pag = db.session.get(Pagamento, pagamento_id)
    if not pag:
        abort(404)
    pedido = pag.pedido
    
    pag.data_recebimento = date.fromisoformat(request.form.get("data_recebimento"))
    pag.forma_pagamento = request.form.get("forma_pagamento")
    pag.valor_recebido = float(request.form.get("valor_recebido", 0) or 0)
    pag.taxa_cartao = float(request.form.get("taxa_cartao", 0) or 0)
    pag.observacoes = request.form.get("observacoes", "")
    
    atualizar_status_pagamento(pedido)
    db.session.commit()
    flash("Pagamento atualizado.", "success")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))


@bp.route("/pagamento/<int:pagamento_id>/deletar", methods=["POST"])
@login_required
def deletar_pagamento(pagamento_id: int):
    pag = db.session.get(Pagamento, pagamento_id)
    if not pag:
        abort(404)
    pedido = pag.pedido
    db.session.delete(pag)
    atualizar_status_pagamento(pedido)
    db.session.commit()
    flash("Pagamento removido.", "success")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))


@bp.route("/<int:pedido_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar(pedido_id: int):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido:
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido removido.", "success")
    return redirect(url_for("pedidos.listar"))
