"""PDF-Export der aktuellen Aufgabe mit den Rechenwegen (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from bpo_evaluation import Analysis, verdict_answers, way_rows

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "ⁿ": "^n", "²": "^2", "ₖ": "k", "∞": "unendlich",
            "⁻": "-", "⁰": "0", "¹": "1", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "ₙ": "n", "×": "x", "Σ": "Summe", "√": "Wurzel", "≈": "~", "ó": "o", "Ó": "O"}


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Zählen bis auf Symmetrie"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    s = a.settings
    pdf.multi_cell(0, 5, _s(f"{s.family}, n = {a.n_eff}, Farben {a.k_eff}, Symmetrie: {a.symmetry_eff}. Alles gerechnet, keine Messdaten."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_answers(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    widths = (40, 80, 50, 20)
    heads = ("Frage", "Weg", "Ergebnis", "Prüfung")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for row in way_rows(a):
        for key, w in zip(heads, widths):
            pdf.cell(w, 5.5, _s(row[key])[:50], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: burnside-polya-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
