"""ficha_service.py — Ficha Técnica computation helper (Business Rule 2)."""
from app.models.ficha_tecnica import FichaTecnica


def resumo_ficha(ficha: FichaTecnica) -> dict:
    """Returns a dict with all computed values for use in templates."""
    return {
        "custo_total_insumos": ficha.custo_total_insumos,
        "custo_total_receita": ficha.custo_total_receita,
        "custo_unitario": ficha.custo_unitario,
        "preco_sugerido": ficha.preco_sugerido,
        # Simulation Data
        "preco_venda_atual": ficha.produto.preco_varejo if ficha.produto else Decimal("0"),
        "lucro_unitario_atual": ficha.lucro_unitario_atual,
        "margem_atual_percentual": ficha.margem_atual_percentual,
        "markup_atual": ficha.markup_atual,
        # Wholesale Simulation
        "preco_venda_atacado": ficha.produto.preco_atacado if ficha.produto else Decimal("0"),
        "lucro_unitario_atacado": ficha.lucro_unitario_atacado,
        "margem_atacado_percentual": ficha.margem_atacado_percentual,
        "markup_atacado": ficha.markup_atacado,
    }
