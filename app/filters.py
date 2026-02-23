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

    @app.template_filter("qty")
    def qty(value) -> str:
        """Format a quantity with up to 2 decimal places."""
        try:
            v = float(value)
            # Use localized decimal separator if needed, but for now just 2 decimals
            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (TypeError, ValueError):
            return "0,00"

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
    @app.template_filter("mes_extenso")
    def mes_extenso(mes_num) -> str:
        """Converts month number (1-12) to Portuguese month name."""
        try:
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            return meses.get(int(mes_num), "")
        except (TypeError, ValueError):
            return ""
