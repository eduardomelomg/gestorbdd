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
        """Format a quantity with up to 2 decimal places, removing unnecessary zeros."""
        try:
            v = float(value)
            # Format with 2 decimals and replace separators
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            # Remove redundant ,00
            if s.endswith(",00"): s = s[:-3]
            elif "," in s and s.endswith("0"): s = s[:-1]
            return s
        except (TypeError, ValueError):
            return "0"

    @app.template_filter("qty_smart")
    def qty_smart(value, unit) -> str:
        """Automatically converts g to kg and ml to l if >= 1000."""
        try:
            v = float(value)
            if unit == "g":
                if v >= 1000:
                    val = v / 1000
                    # For kg, we might want 1 or 2 decimals depending on precision
                    s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    if s.endswith(",00"): s = s[:-3]
                    elif "," in s and s.endswith("0"): s = s[:-1]
                    return f"{s} kg"
                return f"{int(v)} g"
            
            if unit == "ml":
                if v >= 1000:
                    val = v / 1000
                    s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    if s.endswith(",00"): s = s[:-3]
                    elif "," in s and s.endswith("0"): s = s[:-1]
                    return f"{s} l"
                return f"{int(v)} ml"
            
            # Default for un, kg, l
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if s.endswith(",00"): s = s[:-3]
            elif "," in s and s.endswith("0"): s = s[:-1]
            return f"{s} {unit}"
        except (TypeError, ValueError):
            return str(value)

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

    @app.template_filter("format_form")
    def format_form(value) -> str:
        """Format a number for HTML5 number input value attribute (always uses dot)."""
        try:
            v = float(value)
            return f"{v:.2f}"
        except (TypeError, ValueError):
            return "0.00"
