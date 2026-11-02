"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import bpo_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_terms(terms: list, family: str):
    """Die Summanden der Rechnung: Fixpunkte je Gruppenelement (Perlenketten, Bretter), Beitrag je Zyklentyp (Graphen) oder Größe je Bahn (Spielpläne)."""
    fig = go.Figure()
    labels = [t[0] for t in terms]
    if family == "Graphen":
        fig.add_trace(go.Bar(x=labels, y=[float(t[2]) for t in terms], name="Beitrag zur Bahnenzahl", marker_color=C.COLOR_MAIN))
        fig.update_xaxes(title_text="Zyklentyp der Permutation (die größten Beiträge)", type="category")
        fig.update_yaxes(title_text="Beitrag zur Bahnenzahl", type="log")
    elif family == "Spielpläne eines Rundenturniers":
        fig.add_trace(go.Bar(x=labels, y=[float(t[1]) for t in terms], name="Größe der Bahn n!/|Aut|", marker_color=C.COLOR_MAIN))
        fig.update_xaxes(title_text="Bahn (nach |Aut|)", type="category")
        fig.update_yaxes(title_text="Zahl der Pläne in der Bahn")
    else:
        fig.add_trace(go.Bar(x=list(range(1, len(terms) + 1)), y=[float(t[1]) for t in terms], name="Fixpunkte", marker_color=C.COLOR_MAIN))
        fig.update_xaxes(title_text="Gruppenelement (Nummer)")
        fig.update_yaxes(title_text="Fixpunkte (k^Zyklen)", type="log")
    return _base(fig)


def build_approx(res: dict):
    """Betrag des relativen Fehlers der Näherung Gesamtzahl/|G| gegen n (logarithmische Achse)."""
    fig = go.Figure()
    for k, ser in res["series"].items():
        ns = sorted(ser)
        fig.add_trace(go.Scatter(x=ns, y=[max(abs(ser[n]), 1e-16) for n in ns], mode="lines+markers", name=f"Halsketten, {k} Farben"))
    ns = sorted(res["bracelets"])
    fig.add_trace(go.Scatter(x=ns, y=[max(abs(res["bracelets"][n]), 1e-16) for n in ns], mode="lines", name="Armbänder, 2 Farben", line=dict(dash="dot")))
    fig.update_xaxes(title_text="n")
    fig.update_yaxes(title_text="Betrag des relativen Fehlers der Näherung", type="log")
    return _base(fig, 360)


def build_graph_ratio(res: dict):
    """Verhältnis der exakten Zahl der Graphen zur Näherung 2^C(n,2)/n! gegen n."""
    fig = go.Figure()
    ns = sorted(res["graphs"])
    fig.add_trace(go.Scatter(x=ns, y=[float(res["graphs"][n]) for n in ns], mode="lines+markers", name="exakt / Näherung", line=dict(color=C.COLOR_MAIN)))
    fig.add_hline(y=1, line=dict(color=C.COLOR_WARN, dash="dash"))
    fig.update_xaxes(title_text="Zahl der Knoten n")
    fig.update_yaxes(title_text="exakt / (2^C(n,2) / n!)")
    return _base(fig, 320)


def build_weights(res: dict):
    """Bahnen nach Gewicht: binäre Halsketten (n = 8) und das 3×3-Brett unter allen acht Symmetrien."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(len(res["chain"]))), y=res["chain"], name=f"Halsketten, n = {res['n']}", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=list(range(len(res["board"]))), y=res["board"], name="3×3-Brett, Drehungen und Spiegelungen", marker_color=C.COLOR_LINE))
    fig.update_xaxes(title_text="Zahl der Einsen beziehungsweise schwarzen Felder")
    fig.update_yaxes(title_text="Zahl der Bahnen")
    fig.update_layout(barmode="group")
    return _base(fig, 320)


def build_schedules(rows: list[dict]):
    """Zahl der Spielpläne und der Bahnen je Teamzahl (logarithmische Achse)."""
    fig = go.Figure()
    xs = [f"{r['Teams']} Teams" for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["Pläne"] for r in rows], name="Spielpläne", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=xs, y=[r["Bahnen"] for r in rows], name="Bahnen bis auf Umbenennen", marker_color=C.COLOR_MAIN))
    fig.update_yaxes(title_text="Zahl", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 300)
