from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.clientes import bp
from app.extensions import db
from app.models.cliente import Cliente
from app.blueprints.auth.decorators import admin_required


@bp.route("/")
@login_required
def listar():
    clientes = db.session.execute(
        select(Cliente).order_by(Cliente.nome)
    ).scalars().all()
    return render_template("clientes/list.html", clientes=clientes)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        c = Cliente(
            nome=request.form["nome"],
            tipo=request.form.get("tipo", "Pessoa"),
            canal_preferencial=request.form.get("canal_preferencial", "B2C"),
            telefone=request.form.get("telefone", ""),
            endereco=request.form.get("endereco", ""),
            documento=request.form.get("documento", ""),
            tabela_preco=request.form.get("tabela_preco", "Varejo"),
            prazo_pagamento_dias=int(request.form.get("prazo_pagamento_dias", 0) or 0),
        )
        db.session.add(c)
        db.session.commit()
        flash(f"Cliente '{c.nome}' criado.", "success")
        return redirect(url_for("clientes.listar"))
    return render_template("clientes/form.html", cliente=None)


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@login_required
def editar(cliente_id: int):
    c = db.session.get(Cliente, cliente_id)
    if not c:
        abort(404)
    if request.method == "POST":
        c.nome = request.form["nome"]
        c.tipo = request.form.get("tipo", c.tipo)
        c.canal_preferencial = request.form.get("canal_preferencial", c.canal_preferencial)
        c.telefone = request.form.get("telefone", c.telefone)
        c.endereco = request.form.get("endereco", c.endereco)
        c.documento = request.form.get("documento", c.documento)
        c.tabela_preco = request.form.get("tabela_preco", c.tabela_preco)
        c.prazo_pagamento_dias = int(request.form.get("prazo_pagamento_dias", c.prazo_pagamento_dias) or 0)
        c.ativo = "ativo" in request.form
        db.session.commit()
        flash(f"Cliente '{c.nome}' atualizado.", "success")
        return redirect(url_for("clientes.listar"))
    return render_template("clientes/form.html", cliente=c)


@bp.route("/<int:cliente_id>/deletar", methods=["POST"])
@login_required
@admin_required
def deletar(cliente_id: int):
    c = db.session.get(Cliente, cliente_id)
    if c:
        c.ativo = False
        db.session.commit()
        flash(f"Cliente '{c.nome}' desativado.", "success")
    return redirect(url_for("clientes.listar"))
