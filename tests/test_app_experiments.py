"""Oberfläche: jede Familie, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import bpo_constants as C
import bpo_evaluation as ev
import bpo_visualization as V

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_five_experiments_and_the_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == ["🔬 Experiment 1: Dieselbe Zahl auf mehreren Wegen", "🔬 Experiment 2: Die Näherung Gesamtzahl/|G|", "🔬 Experiment 3: Pólya mit Gewicht",
                                                                   "🔬 Experiment 4: Graphen über Zyklentypen", "🔬 Experiment 5: Die Spielpläne eines Rundenturniers"]
    assert any(t.startswith("6 Perlen im Kreis, 2 Farben: 64 Färbungen, 14 Bahnen bis auf Drehungen") for t in _texts(at)) and not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    values = {m.label: m.value for m in at.metric}
    assert values == {"Objekte ohne Symmetrie": "64", "Bahnen bis auf Symmetrie": "14", "Größe der Gruppe |G|": "6", "Näherung Gesamtzahl/|G|": "10,67"}


def test_every_preset_runs_and_shows_its_family():
    for name, preset in C.PRESETS.items():
        at = _run(family_select=preset["family"], n_slider=preset["n"], k_slider=preset["k"], symmetry_select=preset["symmetry"])
        assert at.selectbox(key="family_select").value == preset["family"], name
        assert not at.error, name


def test_every_family_runs_at_the_slider_limits():
    for fam in C.FAMILIES:
        for n in (C.N_MIN, C.N_MAX):
            at = _run(family_select=fam, n_slider=n, k_slider=C.K_MAX)
            assert not at.error, (fam, n)


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"family": "Unsinn", "n": "abc", "k": "99999", "symmetry": "Zauber"})
    assert at.selectbox(key="family_select").value == C.DEFAULT_FAMILY and at.slider(key="n_slider").value == C.DEFAULT_N
    assert at.slider(key="k_slider").value == C.K_MAX and at.selectbox(key="symmetry_select").value == C.DEFAULT_SYMMETRY


def test_note_for_fixed_symmetry_and_odd_team_count():
    at = _run(family_select="Spielpläne eines Rundenturniers", n_slider=5, symmetry_select="keine")
    texts = _texts(at)
    assert any("gerade Teamzahlen" in t for t in texts) and any("ist die Symmetrie fest" in t for t in texts)


def test_play_ground_shows_boards_and_counts():
    at = _run()
    assert any(t.startswith("3×3-Brett mit 2 Farben: 512 Färbungen, 102 Bahnen") for t in _texts(at))
    assert len(at.get("code")) >= 6
    at = _run(play_side=4, play_k=3, play_sym="Drehungen")
    assert any("das Aufzählen der Bahnen entfällt" in t for t in _texts(at))


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("download_button")) == 1


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and {"main_chart", "approx_chart", "graph_ratio_chart", "weights_chart", "schedule_chart"} <= set(keys)


def test_pdf_builds_for_every_family():
    from bpo_pdf_export import build_pdf
    for fam in C.FAMILIES:
        a = ev.analyse(ev.Settings(fam, 6, 2, "Drehungen und Spiegelungen"))
        assert build_pdf(a)[:4] == b"%PDF", fam


def test_chart_builders_return_locked_axes():
    a = ev.analyse(ev.Settings("Graphen", 8, 2, "Drehungen"))
    for fam in C.FAMILIES:
        fig = V.build_terms(ev.analyse(ev.Settings(fam, 6, 2, "Drehungen")).terms, fam)
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange, fam
    assert a.terms and V.build_approx(ev.approx_rows()).layout.yaxis.type == "log"
