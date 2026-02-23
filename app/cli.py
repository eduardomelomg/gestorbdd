"""
CLI commands registered on the Flask app:
  flask seed         — populate DB with test data
  flask create-admin — create admin user interactively
"""
import click
from datetime import date, datetime, timezone
from flask import Flask


def register_commands(app: Flask) -> None:

    @app.cli.command("seed")
    def seed():
        """Seed database with demo data for Brownie do Dudu."""
        from app.extensions import db
        from app.models.usuario import Usuario
        from app.models.cliente import Cliente
        from app.models.produto import Produto
        from app.models.insumo import Insumo
        from app.models.compra_insumo import CompraInsumo
        from app.models.ficha_tecnica import FichaTecnica, FichaTecnicaItem
        from app.models.pedido import Pedido, PedidoItem
        from app.models.pagamento import Pagamento
        from app.services.pedido_service import (
            gerar_numero_pedido, atualizar_status_pagamento, registrar_entrada_estoque
        )

        click.echo("🌱 Seeding database...")

        # ---- Admin user ----
        if not db.session.execute(
            db.select(Usuario).where(Usuario.email == "admin@browniedudu.com")
        ).scalar_one_or_none():
            admin = Usuario(nome="Admin Dudu", email="admin@browniedudu.com", role="Admin")
            admin.set_password("admin123")
            db.session.add(admin)
            click.echo("  ✓ Admin user criado (admin@browniedudu.com / admin123)")

        # ---- Clientes ----
        clientes_data = [
            dict(nome="Maria Silva", tipo="Pessoa", canal_preferencial="B2C",
                 tabela_preco="Varejo", telefone="11999990001"),
            dict(nome="João Santos", tipo="Pessoa", canal_preferencial="B2C",
                 tabela_preco="Varejo", telefone="11999990002"),
            dict(nome="Doceria Bella LTDA", tipo="Empresa", canal_preferencial="B2B",
                 tabela_preco="Atacado", documento="12.345.678/0001-99"),
            dict(nome="Café Gourmet ME", tipo="Empresa", canal_preferencial="B2B",
                 tabela_preco="Atacado", documento="98.765.432/0001-11"),
        ]
        clientes = []
        for cd in clientes_data:
            if not db.session.execute(
                db.select(Cliente).where(Cliente.nome == cd["nome"])
            ).scalar_one_or_none():
                c = Cliente(**cd)
                db.session.add(c)
                clientes.append(c)
        db.session.flush()
        click.echo(f"  ✓ {len(clientes)} clientes criados")

        # ---- Insumos ----
        insumos_data = [
            dict(nome="Chocolate Meio Amargo", unidade="g",
                 quantidade_embalagem_compra=1000, preco_compra_embalagem=32.00,
                 estoque_atual=5000, estoque_minimo=500),
            dict(nome="Farinha de Trigo", unidade="g",
                 quantidade_embalagem_compra=1000, preco_compra_embalagem=5.50,
                 estoque_atual=3000, estoque_minimo=300),
            dict(nome="Açúcar Refinado", unidade="g",
                 quantidade_embalagem_compra=1000, preco_compra_embalagem=4.00,
                 estoque_atual=2000, estoque_minimo=200),
            dict(nome="Manteiga", unidade="g",
                 quantidade_embalagem_compra=200, preco_compra_embalagem=7.00,
                 estoque_atual=600, estoque_minimo=100),
            dict(nome="Ovos", unidade="un",
                 quantidade_embalagem_compra=12, preco_compra_embalagem=9.00,
                 estoque_atual=48, estoque_minimo=12),
            dict(nome="Embalagem Kraft Brownie", unidade="un",
                 quantidade_embalagem_compra=100, preco_compra_embalagem=45.00,
                 estoque_atual=200, estoque_minimo=50),
        ]
        insumos = {}
        for idata in insumos_data:
            existing = db.session.execute(
                db.select(Insumo).where(Insumo.nome == idata["nome"])
            ).scalar_one_or_none()
            if not existing:
                ins = Insumo(**idata)
                db.session.add(ins)
                db.session.flush()
                insumos[idata["nome"]] = ins
            else:
                insumos[idata["nome"]] = existing
        click.echo(f"  ✓ {len(insumos_data)} insumos verificados/criados")

        # ---- Produtos ----
        produtos_data = [
            dict(nome="Brownie Tradicional", sku="BR-001", categoria="Brownie",
                 unidade_venda="un", preco_varejo=12.00, preco_atacado=8.50),
            dict(nome="Brownie com Doce de Leite", sku="BR-002", categoria="Brownie",
                 unidade_venda="un", preco_varejo=14.00, preco_atacado=10.00),
            dict(nome="Caixa 6 Brownies", sku="CX-006", categoria="Brownie",
                 unidade_venda="caixa", preco_varejo=65.00, preco_atacado=48.00),
        ]
        produtos = {}
        for pdata in produtos_data:
            existing = db.session.execute(
                db.select(Produto).where(Produto.sku == pdata["sku"])
            ).scalar_one_or_none()
            if not existing:
                p = Produto(**pdata)
                db.session.add(p)
                db.session.flush()
                produtos[pdata["sku"]] = p
            else:
                produtos[pdata["sku"]] = existing
        click.echo(f"  ✓ {len(produtos_data)} produtos verificados/criados")

        # ---- Ficha Técnica para Brownie Tradicional ----
        produto_bt = produtos["BR-001"]
        if not produto_bt.ficha_tecnica:
            ficha = FichaTecnica(
                produto_id=produto_bt.id,
                rendimento_unidades=12,
                mao_de_obra_total=15.00,
                perdas_percentual=5.0,
                margem_desejada_percentual=60.0,
            )
            db.session.add(ficha)
            db.session.flush()

            # Itens da receita para 12 brownies
            itens = [
                (insumos["Chocolate Meio Amargo"], 200, "Insumo"),
                (insumos["Farinha de Trigo"], 150, "Insumo"),
                (insumos["Açúcar Refinado"], 200, "Insumo"),
                (insumos["Manteiga"], 100, "Insumo"),
                (insumos["Ovos"], 3, "Insumo"),
                (insumos["Embalagem Kraft Brownie"], 12, "Embalagem"),
            ]
            for ins, qty, tipo in itens:
                fi = FichaTecnicaItem(
                    ficha_tecnica_id=ficha.id,
                    insumo_id=ins.id,
                    quantidade_por_receita=qty,
                    tipo_item=tipo,
                )
                db.session.add(fi)
            click.echo("  ✓ Ficha técnica do Brownie Tradicional criada")

        # ---- Pedido agendado com pagamento parcial ----
        # Ensures we have at least one cliente to use
        db.session.flush()
        all_clientes = db.session.execute(db.select(Cliente)).scalars().all()
        cliente_b2c = next((c for c in all_clientes if c.canal_preferencial == "B2C"), all_clientes[0])

        existing_pedido = db.session.execute(
            db.select(Pedido).where(Pedido.numero_pedido.like("BD-%"))
        ).scalar_one_or_none()

        if not existing_pedido:
            nr = gerar_numero_pedido()
            pedido = Pedido(
                numero_pedido=nr,
                cliente_id=cliente_b2c.id,
                canal="B2C",
                data_pedido=date.today(),
                data_hora_agendada=datetime(2026, 2, 28, 14, 0, tzinfo=timezone.utc),
                tipo_entrega="Entrega",
                endereco_entrega="Rua das Flores, 100 - Centro",
                status_pedido="Agendado",
                status_pagamento="Não pago",
                desconto=0,
                taxa_entrega=10.00,
                observacoes="Pedido de demonstração — pagamento parcial para testar regime caixa",
            )
            db.session.add(pedido)
            db.session.flush()

            # 2 itens
            db.session.add(PedidoItem(
                pedido_id=pedido.id,
                produto_id=produtos["BR-001"].id,
                quantidade=5,
                preco_unitario=12.00,
            ))
            db.session.add(PedidoItem(
                pedido_id=pedido.id,
                produto_id=produtos["CX-006"].id,
                quantidade=1,
                preco_unitario=65.00,
            ))
            db.session.flush()

            # Partial payment — total_pedido = 5×12 + 65 + 10 = R$ 135,00
            # Pay R$ 50,00 → status = Parcial
            pag = Pagamento(
                pedido_id=pedido.id,
                data_recebimento=date.today(),
                forma_pagamento="PIX",
                valor_recebido=50.00,
                taxa_cartao=0,
                observacoes="Sinal — teste de regime caixa",
            )
            db.session.add(pag)
            db.session.flush()
            atualizar_status_pagamento(pedido)
            click.echo(f"  ✓ Pedido {nr} criado — status pagamento: {pedido.status_pagamento}")

        db.session.commit()
        click.echo("🎉 Seed completo!")

    @app.cli.command("create-admin")
    @click.option("--nome", prompt="Nome do admin")
    @click.option("--email", prompt="E-mail")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(nome, email, password):
        """Create an Admin user interactively."""
        from app.extensions import db
        from app.models.usuario import Usuario
        u = Usuario(nome=nome, email=email.lower(), role="Admin")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        click.echo(f"✓ Admin '{nome}' ({email}) criado com sucesso.")
