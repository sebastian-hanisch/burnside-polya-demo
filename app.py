"""Zählen bis auf Symmetrie – Burnside und Pólya - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 11 der Reihe „Abzählen und erzeugende Funktionen“: Wie viele Objekte gibt es bis auf Symmetrie? Burnside: die Zahl der Bahnen ist das Mittel der Fixpunkte über alle Gruppenelemente; Pólya macht daraus
den Zyklenindex (auch mit Gewicht). Die einfache Näherung Gesamtzahl/|G| ist nur eine untere Schranke und trifft bei Halsketten und Graphen erst für große n. Beispiele: Perlenketten, Bretter, Graphen und die Spielpläne eines Rundenturniers.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import bpo_constants as C
from bpo_evaluation import (
    Settings,
    analyse,
    approx_error,
    approx_rows,
    approx_text,
    big_text,
    de,
    fraction_text,
    graph_rows,
    percent,
    percent_fine,
    play_board,
    schedule_rows,
    sci_text,
    verdict_answers,
    verdict_approx,
    verdict_graphs,
    verdict_play,
    verdict_schedules,
    verdict_ways,
    verdict_weights,
    way_rows,
    ways_rows,
    weight_rows,
)
from bpo_layout import dunkles_design, kopf_css
from bpo_pdf_export import build_pdf
from bpo_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from bpo_visualization import build_approx, build_graph_ratio, build_schedules, build_terms, build_weights

st.set_page_config(page_title="Zählen bis auf Symmetrie – Sebastian Hanisch", layout="wide")

SPINNER = "Die Experimente werden einmal gerechnet …"


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=SPINNER)
def _ways():
    return ways_rows()


@st.cache_data(show_spinner=SPINNER)
def _approx():
    return approx_rows()


@st.cache_data(show_spinner=SPINNER)
def _weights():
    return weight_rows()


@st.cache_data(show_spinner=SPINNER)
def _graphs():
    return graph_rows()


@st.cache_data(show_spinner=SPINNER)
def _schedules():
    return schedule_rows()


@st.cache_data(show_spinner=False)
def _play(size, k, symmetry):
    return play_board(size, k, symmetry)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in bpo_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔄 Zählen bis auf Symmetrie – Burnside und Pólya")
st.markdown(
    """
**Wie viele Objekte gibt es bis auf Symmetrie?** Stück 1 bis 10 haben gezählt, als wären alle Objekte verschieden. Oft sind zwei Objekte „dasselbe“: eine Kette, die man dreht, ein Brett, das man wendet, ein Graph, dessen Knoten man umbenennt,
ein Spielplan, in dem man die Teams umbenennt. Die Frage ist dann die Zahl der **Bahnen** einer Gruppe $G$ auf der Menge $X$ der Objekte. **Burnside:** die Zahl der Bahnen ist das **Mittel der Fixpunkte**,
$|X/G| = \\frac{1}{|G|} \\sum_{g \\in G} |\\mathrm{Fix}(g)|$. **Pólya:** bei Färbungen ist $|\\mathrm{Fix}(g)| = k^{\\text{Zyklen von } g}$ (der **Zyklenindex**), und mit einem Gewicht statt $k$ zählt derselbe Satz die Bahnen nach Gewicht.
Die einfache Näherung **Gesamtzahl$/|G|$** ist nur eine untere Schranke und trifft bei Halsketten und Graphen erst für große $n$ (Experiment 2).

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert das Zählen der Bahnen", expanded=True):
    st.markdown(
        """
1. **Gruppe aufschreiben:** Die Symmetrien als Permutationen der Positionen (Drehungen und Spiegelungen einer Kette, Symmetrien des Quadrats, alle Umbenennungen der Knoten).
2. **Fixpunkte zählen:** Eine Färbung bleibt unter $g$ fest, wenn sie auf jedem Zyklus von $g$ konstant ist: $k^{\\text{Zyklen}}$ Möglichkeiten.
3. **Mitteln:** Summe über alle Gruppenelemente durch $|G|$. Gruppiert man die Elemente nach ihrem Zyklentyp, sind es bei $S_n$ nur $p(n)$ Summanden statt $n!$.
4. **Gegenprobe:** die Bahnen aufzählen (kleinste Form unter allen Bildern) und mit der Formel vergleichen.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    family = st.selectbox("Familie", list(C.FAMILIES), key="family_select", help="Perlenketten (n Perlen im Kreis), Bretter (n×n Felder), Graphen auf n Knoten oder die Spielpläne eines Rundenturniers mit n Teams.")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider", help=f"Zahl der Perlen, Seitenlänge des Bretts, Zahl der Knoten oder der Teams. Höchstens bis {', '.join(f'{k} ({v})' for k, v in C.N_CAP.items())}; Spielpläne nur mit 4, 6 oder 8 Teams.")
    k = st.slider("Zahl der Farben k", *bounds("k_slider"), key="k_slider", help="Nur für Perlenketten und Bretter: wie viele Farben jede Position haben kann.")
    sym = st.selectbox("Symmetrie", list(C.SYMMETRIES), key="symmetry_select", help="Nur für Perlenketten und Bretter: keine, nur Drehungen (Halsketten) oder Drehungen und Spiegelungen (Armbänder). Graphen und Spielpläne haben das Umbenennen als feste Symmetrie.")

sync_query_params({"family_select": family, "n_slider": int(n), "k_slider": int(k), "symmetry_select": sym})

settings = Settings(family, int(n), int(k), sym)
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Objekte ohne Symmetrie", big_text(a.total), help="Gesamtzahl: k^Positionen bei Färbungen, 2^C(n,2) bei Graphen, Zahl der 1-Faktorisierungen bei den Spielplänen.")
m2.metric("Bahnen bis auf Symmetrie", big_text(a.orbits), help="Gleich auf allen gerechneten Wegen; sonst zeigt die App einen Fehler.")
m3.metric("Größe der Gruppe |G|", big_text(a.group_order), help="Zahl der Symmetrien (bei Graphen und Spielplänen n!).")
m4.metric("Näherung Gesamtzahl/|G|", approx_text(a.approx), delta=None if a.orbits == a.total else percent_fine(approx_error(a)), delta_color="off",
          help="Untere Schranke der Bahnenzahl; der Abstand in Prozent steht darunter (negativ: die Näherung liegt zu klein).")
st.plotly_chart(build_terms(a.terms, family), width="stretch", key="main_chart")
st.caption("Die Summanden der Rechnung: bei Perlenketten und Brettern die Fixpunkte je Gruppenelement (logarithmische Achse), bei Graphen die größten Beiträge der Zyklentypen zur Bahnenzahl, bei den Spielplänen die Größe jeder Bahn.")
st.dataframe(way_rows(a), hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="symmetrie-zaehlen.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Objekte gibt es bis auf Symmetrie?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Dieselbe Zahl auf mehreren Wegen")
st.caption("Acht Aufgaben, jede auf drei unabhängigen Wegen (bei den Spielplänen zwei Wege für die Planzahl, einer für die Bahnenzahl): geschlossene Formel aus dem Zyklenindex, Burnside über alle Gruppenelemente, Aufzählen der Bahnen (kleinste Form oder Union-Find).")
ways = _ways()
st.dataframe([{"Familie": r["Familie"], "n": r["n"], "Farben": "–" if r["k"] is None else str(r["k"]), "Symmetrie": r["Symmetrie"] if r["Familie"] in ("Perlenketten", "Brett s×s") else "Umbenennen", "Objekte": big_text(r["Gesamtzahl"]),
               "|G|": big_text(r["|G|"]), "Bahnen": big_text(r["Bahnen"]), "Wege": r["Wege"], "gleich": "ja" if r["gleich"] else "nein"} for r in ways], hide_index=True, width="stretch")
verdict(verdict_ways(ways))

st.markdown("---")

st.subheader("🔬 Experiment 2: Die Näherung Gesamtzahl/|G|")
st.caption("Fehler der Näherung gegen die exakte Bahnenzahl, Halsketten mit 2, 3 und 10 Farben und Armbänder; darunter bei Graphen das Verhältnis der exakten Zahl zu 2^C(n,2)/n!. Die Näherung ist immer eine untere Schranke.")
approx = _approx()
st.plotly_chart(build_approx(approx), width="stretch", key="approx_chart")
st.dataframe([{"n": r["n"], "exakt (2 Farben)": big_text(r["exakt"]), "Näherung 2ⁿ/n": approx_text(r["Näherung"]), "Fehler": percent_fine(r["Fehler"], 3)} for r in approx["table"]], hide_index=True, width="stretch")
st.plotly_chart(build_graph_ratio(approx), width="stretch", key="graph_ratio_chart")
verdict(verdict_approx(approx))

st.markdown("---")

st.subheader("🔬 Experiment 3: Pólya mit Gewicht")
st.caption("Ersetzt man in Zyklenindex k durch 1 + y^Länge, steht in der Summe die Zahl der Bahnen nach Gewicht (Stück 8): hier binäre Halsketten nach Zahl der Einsen und das 3×3-Brett nach Zahl der schwarzen Felder.")
weights = _weights()
st.plotly_chart(build_weights(weights), width="stretch", key="weights_chart")
st.dataframe([{"Zahl der Einsen": j, "Halsketten n = 8": str(weights["chain"][j]) if j < len(weights["chain"]) else "–", "3×3-Brett": str(weights["board"][j]) if j < len(weights["board"]) else "–"} for j in range(max(len(weights["chain"]), len(weights["board"])))],
             hide_index=True, width="stretch")
verdict(verdict_weights(weights))

st.markdown("---")

st.subheader("🔬 Experiment 4: Graphen über Zyklentypen")
st.caption("Graphen auf n Knoten bis auf Umbenennen: Summe über die Zyklentypen statt über n! Permutationen. Dazu die Verbindung zu Stück 5 und 6: beschriftet geteilt durch n! mal unbeschriftet ist das Mittel von 1/|Aut|, und die Wurzelbäume ohne Reihenfolge kommen aus dem Zyklenindex.")
graphs = _graphs()
st.dataframe([{"n": r["n"], "Permutationen": big_text(r["Permutationen"]), "Zyklentypen": r["Zyklentypen"], "Graphen bis auf Umbenennen": big_text(r["Graphen"]), "exakt / Näherung": de(r["Verhältnis"], 4)} for r in graphs["rows"]], hide_index=True, width="stretch")
st.dataframe([{"n": r["n"], "Bahnen (Aufzählen)": r["Bahnen"], "Pólya": r["Pólya"], "Mittel von 1/|Aut|": fraction_text(r["Mittel 1/|Aut|"]), "beschriftet/(n!·Bahnen)": fraction_text(r["beschriftet/(n!·Bahnen)"]), "gleich": "ja" if r["gleich"] else "nein"} for r in graphs["mean"]],
             hide_index=True, width="stretch")
st.dataframe([{"n": i, "Euler-Transformation": graphs["euler"][i], "Pólya": graphs["polya"][i]} for i in range(1, len(graphs["euler"]))], hide_index=True, width="stretch")
verdict(verdict_graphs(graphs))

st.markdown("---")

st.subheader("🔬 Experiment 5: Die Spielpläne eines Rundenturniers")
st.caption("Ein Spielplan ist eine 1-Faktorisierung von Kₙ: n − 1 Runden, in jeder spielt jedes Team genau einmal, und jedes Paar trifft sich genau einmal (die Zirkelmethode aus `round-robin-demo` baut davon einen). Gezählt werden alle Pläne und die Bahnen unter Umbenennen der Teams.")
sched = _schedules()
st.plotly_chart(build_schedules(sched), width="stretch", key="schedule_chart")
st.dataframe([{"Teams": r["Teams"], "Runden": r["Runden"], "Spielpläne": big_text(r["Pläne"]), "Bahnen": r["Bahnen"], "Bahngrößen": ", ".join(map(str, r["Bahngrößen"])), "|Aut| je Bahn": ", ".join(map(str, r["|Aut|"])),
               "Σ n!/|Aut|": big_text(r["Σ n!/|Aut|"]), "Gesamtzahl/n!": de(float(r["Gesamtzahl/n!"]), 4), "mit Reihenfolge der Runden": big_text(r["mit Reihenfolge der Runden"])} for r in sched], hide_index=True, width="stretch")
verdict(verdict_schedules(sched))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Brett mit Vertretern")
st.caption("Ein s×s-Brett mit k Farben und gewählter Symmetrie: Zahl der Bahnen (aus dem Zyklenindex und, wo möglich, durch Aufzählen) und die kleinsten Vertreter der ersten Bahnen als kleine Bretter (Ziffern sind Farben).")
q1, q2, q3 = st.columns(3)
side = q1.slider("Seitenlänge s", C.PLAY_SIDE_MIN, C.PLAY_SIDE_MAX, 3, key="play_side", help="Brett mit s×s Feldern.")
pk = q2.slider("Farben", C.PLAY_K_MIN, C.PLAY_K_MAX, 2, key="play_k", help="Zahl der Farben je Feld.")
psym = q3.selectbox("Symmetrie des Bretts", list(C.SYMMETRIES), index=2, key="play_sym", help="Keine, Drehungen um 90° oder Drehungen und Spiegelungen.")
play = _play(int(side), int(pk), psym)
if play["boards"]:
    cols = st.columns(len(play["boards"]))
    for col, board in zip(cols, play["boards"]):
        col.code("\n".join(board), language=None)
verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Gruppe ist bekannt und klein genug** | Burnside über alle Elemente ist nur für kleine Gruppen möglich (die App rechnet bei den Graphen nur bis {C.GRAPH_ALL_ELEMENTS_MAX}! = 40.320 Permutationen); darüber rechnet der Zyklenindex in $p(n)$ Summanden. | Experiment 4 |
| **Die Symmetrie ist die einzige** | Gezählt werden Bahnen genau dieser Gruppe; weitere Symmetrien (Heim- und Auswärtstausch, Zeitspiegelung bei Turnierplänen, Tausch der Farben) ändern die Zahl. | – |
| **Die Näherung Gesamtzahl durch Gruppengröße ist gut** | Sie ist nur eine untere Schranke; der Fehler hängt von den Teilern von n ab (n = 12 schlechter als 11 und 13) und ist bei Armbändern und Spielplänen viel größer, bei Graphen bis etwa n = 15 größer. | Experiment 2 |
| **Aufzählen als Gegenprobe** | Nur bis {big_text(C.ENUM_LIMIT)} Färbungen, bei Graphen nur bis n = {C.GRAPH_ENUM_MAX} und bei den Spielplänen nur bis 8 Teams; darüber stehen nur die Formeln (gerechnet, nicht gegengeprüft). | – |
| **Spielpläne mit Reihenfolge und Heimrecht** | Gezählt werden die Pläne mit ungeordneten Runden und ohne Heimrecht; mit geordneten Runden sind es (n − 1)! mal so viele. Die Zahl der Pläne für 10 und 12 Teams (396 und 526.915.620 Bahnen) steht nur in der Literatur und wird hier nicht gerechnet. | `round-robin-demo` |
| **Die Größe ist begrenzt** | Perlenketten bis n = {C.N_CAP['Perlenketten']}, Bretter bis {C.N_CAP['Brett s×s']}×{C.N_CAP['Brett s×s']}, Graphen bis n = {C.N_CAP['Graphen']}, Spielpläne mit 4, 6 oder 8 Teams, höchstens {C.K_MAX} Farben. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lemma von Burnside.** Wirkt eine endliche Gruppe $G$ auf einer endlichen Menge $X$, so ist die Zahl der Bahnen $|X/G| = \dfrac{1}{|G|}\sum_{g \in G} |\mathrm{Fix}(g)|$. Der Grund: Jedes Paar $(g, x)$ mit $gx = x$ zählt einmal in der Summe; nach dem Bahn-Stabilisator-Satz ist $|G| = |\mathrm{Bahn}(x)| \cdot |\mathrm{Stab}(x)|$, also trägt jede Bahn genau $|G|$ zur Summe bei.

**Pólya.** Für Färbungen von Positionen mit $k$ Farben ist $|\mathrm{Fix}(g)| = k^{c(g)}$ mit der Zahl $c(g)$ der Zyklen von $g$; der **Zyklenindex** $Z_G(x_1, x_2, \dots) = \frac{1}{|G|}\sum_g \prod_{\text{Zyklen}} x_{\text{Länge}}$ gibt die Bahnenzahl als $Z_G(k, k, \dots, k)$, und mit $x_\ell \to 1 + y^\ell$ die Bahnen nach Zahl der Einsen als Koeffizienten.

**Halsketten und Armbänder.** Für die Drehungen $C_n$: $\dfrac{1}{n}\sum_{d \mid n} \varphi(d)\, k^{n/d}$. Für $D_n$ kommen $n$ Spiegelungen dazu: für ungerades $n$ $k^{(n+1)/2}$ je Spiegelung, für gerades $n$ je $n/2$ Spiegelungen mit $k^{n/2+1}$ und $k^{n/2}$.

**Graphen.** Die Gruppe $S_n$ wirkt auf den Knotenpaaren; eine Permutation vom Zyklentyp $(l_1, \dots, l_m)$ hat $\sum_i \lfloor l_i/2 \rfloor + \sum_{i<j} \gcd(l_i, l_j)$ Zyklen auf den Paaren, und die Zahl der Graphen ist $\sum_\lambda 2^{c(\lambda)} / z_\lambda$ mit $z_\lambda = \prod_i i^{m_i} m_i!$.

**Beschriftet gegen unbeschriftet.** Eine Bahn hat $n!/|\mathrm{Aut}|$ beschriftete Objekte, also ist $\dfrac{\text{beschriftet}}{n! \cdot \text{Bahnen}}$ das Mittel von $1/|\mathrm{Aut}|$ über die Bahnen.

**Untere Schranke.** Aus Burnside folgt $|X/G| \ge |X|/|G|$ (die Identität trägt $|X|$ bei, alle anderen Beiträge sind nicht negativ), mit Gleichheit genau, wenn nur die Identität Fixpunkte hat.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
G. Pólya: *Kombinatorische Anzahlbestimmungen für Gruppen, Graphen und chemische Verbindungen*, Acta Mathematica 68, 1937, S. 145–254.
W. Burnside: *Theory of Groups of Finite Order*, Cambridge University Press, 1897 (das Lemma, das schon früher bei Cauchy und Frobenius stand).
F. Harary und E. M. Palmer: *Graphical Enumeration*, Academic Press, 1973 (Graphen über Zyklentypen).
J. H. Dinitz, D. K. Garnick und B. D. McKay: *There are 526,915,620 nonisomorphic one-factorizations of K₁₂*, Journal of Combinatorial Designs 2, 1994, S. 273–285.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
