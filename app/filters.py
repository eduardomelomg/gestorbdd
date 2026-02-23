from flask import Flask


def register_filters(app: Flask) -> None:
    @app.template_filter("brl")
    def brl(value) -> str:
        """Format a number as Brazilian currency: R$ 1.234,56"""
        try:
            v = float(value)
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (TypeError, ValueError):
            return "R$ 0,00"

    @app.template_filter("status_badge")
    def status_badge(status: str) -> str:
        classes = {
            "Rascunho": "secondary",
            "Agendado": "primary",
            "Em produção": "warning",
            "Pronto": "info",
            "Entregue": "success",
            "Cancelado": "danger",
            "Não pago": "danger",
            "Parcial": "warning",
            "Pago": "success",
            "Estornado": "dark",
        }
        cls = classes.get(status, "secondary")
        return f'<span class="badge bg-{cls}">{status}</span>'
