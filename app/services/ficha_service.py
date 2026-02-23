"""ficha_service.py — Ficha Técnica computation helper (Business Rule 2)."""
from app.models.ficha_tecnica import FichaTecnica


def resumo_ficha(ficha: FichaTecnica) -> dict:
    """Returns a dict with all computed values for use in templates."""
    return {
        "custo_total_insumos": ficha.custo_total_insumos,
        "custo_total_receita": ficha.custo_total_receita,
        "custo_unitario": ficha.custo_unitario,
        "preco_sugerido": ficha.preco_sugerido,
    }
