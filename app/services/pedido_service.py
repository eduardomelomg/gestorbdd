"""
pedido_service.py
=================
Central service for all Pedido business logic:
  - Pedido number generation
  - Payment status automation (Business Rule 4)
  - Production start → stock deduction (Business Rule 5)
  - Admin override for negative stock
"""
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import select, func
from app.extensions import db
from app.models.pedido import Pedido, PedidoItem
from app.models.pagamento import Pagamento
from app.models.insumo import Insumo
from app.models.movimentacao_estoque import MovimentacaoEstoque


def gerar_numero_pedido() -> str:
    """Generates next sequential BD-000001 order number."""
    ultimo = db.session.execute(
        select(func.max(Pedido.numero_pedido))
    ).scalar()
    if ultimo:
        try:
            seq = int(ultimo.split("-")[1]) + 1
        except (IndexError, ValueError):
            seq = 1
    else:
        seq = 1
    return f"BD-{seq:06d}"


def atualizar_status_pagamento(pedido: Pedido) -> None:
    """
    Business Rule 4 — Automatically derive payment status from receipts.
    Cash-basis: status is driven by actual money received, NOT by the order itself.
    """
    if pedido.status_pagamento == "Estornado":
        return  # Manual flag; do not auto-update
    soma = pedido.soma_recebida
    total = pedido.total_pedido
    if soma <= 0:
        pedido.status_pagamento = "Não pago"
    elif soma < total:
        pedido.status_pagamento = "Parcial"
    else:
        pedido.status_pagamento = "Pago"


def iniciar_producao(pedido: Pedido, admin_override: bool = False) -> list[str]:
    """
    Business Rule 5 — Deduct ingredients from stock when order moves to 'Em produção'.
    Returns a list of warning messages for low-stock situations.
    Raises ValueError if stock would go negative and admin_override is False.
    """
    warnings: list[str] = []

    for item in pedido.itens:
        ficha = item.produto.ficha_tecnica
        if not ficha:
            continue  # No recipe; skip deduction

        for fi in ficha.itens:
            insumo: Insumo = fi.insumo
            # quantidade_necessaria = (por_receita / rendimento) * qtd_produto_pedido
            quantidade_necessaria = (
                Decimal(str(fi.quantidade_por_receita))
                / Decimal(str(ficha.rendimento_unidades))
                * Decimal(str(item.quantidade))
            )

            novo_estoque = Decimal(str(insumo.estoque_atual)) - quantidade_necessaria

            if novo_estoque < 0 and not admin_override:
                raise ValueError(
                    f"Estoque insuficiente para '{insumo.nome}'. "
                    f"Necessário: {quantidade_necessaria:.4f} {insumo.unidade}, "
                    f"Disponível: {insumo.estoque_atual} {insumo.unidade}."
                )

            if novo_estoque < 0:
                warnings.append(
                    f"Atenção: '{insumo.nome}' ficou negativo ({novo_estoque:.4f} {insumo.unidade})."
                )

            insumo.estoque_atual = novo_estoque
            mov = MovimentacaoEstoque(
                tipo="Saida",
                origem="Producao",
                insumo_id=insumo.id,
                quantidade=-quantidade_necessaria,  # negative = out
                pedido_id=pedido.id,
                observacoes=f"Produção {pedido.numero_pedido}",
            )
            db.session.add(mov)

    return warnings


def registrar_entrada_estoque(compra) -> None:
    """Called after a CompraInsumo is saved — adds stock and creates Movimentacao."""
    insumo: Insumo = compra.insumo
    insumo.estoque_atual = (
        Decimal(str(insumo.estoque_atual)) + Decimal(str(compra.quantidade_comprada))
    )
    mov = MovimentacaoEstoque(
        tipo="Entrada",
        origem="Compra",
        insumo_id=insumo.id,
        quantidade=compra.quantidade_comprada,
        compra_id=compra.id,
        observacoes=f"Compra de {compra.fornecedor or 'fornecedor desconhecido'}",
    )
    db.session.add(mov)


def mudar_status_pedido(pedido: Pedido, novo_status: str,
                        usuario_is_admin: bool = False) -> list[str]:
    """
    Transitions order status and triggers side-effects:
      - 'Em produção' → stock deduction
    Returns a list of warning strings.
    """
    status_validos = [
        "Rascunho", "Agendado", "Em produção", "Pronto", "Entregue", "Cancelado"
    ]
    if novo_status not in status_validos:
        raise ValueError(f"Status inválido: {novo_status}")

    warnings: list[str] = []

    # Only deduct stock on the FIRST transition to production
    if novo_status == "Em produção" and pedido.status_pedido != "Em produção":
        ja_deduziu = db.session.execute(
            select(func.count(MovimentacaoEstoque.id)).where(
                MovimentacaoEstoque.pedido_id == pedido.id,
                MovimentacaoEstoque.origem == "Producao",
            )
        ).scalar()
        if not ja_deduziu:
            warnings = iniciar_producao(pedido, admin_override=usuario_is_admin)

    pedido.status_pedido = novo_status
    pedido.updated_at = datetime.now(timezone.utc)
    return warnings
