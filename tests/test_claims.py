"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Alles ist deterministisch; Zeiten kommen nicht vor."""

import math
from fractions import Fraction
from pathlib import Path

import pytest

import bpo_algorithm as A
import bpo_constants as C
import bpo_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
SETTINGS = ev.Settings


def test_readme_hand_instances():
    assert A.burnside_terms(A.cyclic_group(4), 2) == [16, 2, 4, 2] and A.burnside_count(A.cyclic_group(4), 2) == 6
    assert A.burnside_terms(A.cyclic_group(6), 2) == [64, 2, 4, 8, 4, 2] and A.burnside_count(A.cyclic_group(6), 2) == 14 and A.bracelets_formula(6, 2) == 13
    assert A.square_formula(2, 2, "Drehungen") == 6 and A.square_formula(2, 2, "Drehungen und Spiegelungen") == 6
    assert A.graphs_polya(3) == 4 and sum(Fraction(s, 6) for s in A.graph_orbit_sizes(3)) / 4 == Fraction(1, 3)
    assert len(A.one_factorizations(4)) == 1 and A.automorphism_count(A.one_factorizations(4)[0], 4) == 24 and A.automorphism_count(A.one_factorizations(6)[0], 6) == 120


def test_readme_standard_case():
    a = ev.analyse(SETTINGS(**C.PRESETS["Standardfall: Halsketten, n = 6, 2 Farben"]))
    assert (a.total, a.orbits, a.group_order) == (64, 14, 6) and round(float(a.approx), 2) == 10.67 and round(100 * ev.approx_error(a), 2) == -23.81
    b = ev.analyse(SETTINGS(**C.PRESETS["Armbänder: mit Spiegelungen, n = 6"]))
    assert b.orbits == 13 and round(float(b.approx), 2) == 5.33 and round(100 * ev.approx_error(b), 2) == -58.97


def test_readme_necklace_and_bracelet_sequences():
    assert [A.necklaces_formula(n, 2) for n in range(1, 15)] == [2, 3, 4, 6, 8, 14, 20, 36, 60, 108, 188, 352, 632, 1182]
    assert [A.bracelets_formula(n, 2) for n in range(1, 15)] == [2, 3, 4, 6, 8, 13, 18, 30, 46, 78, 126, 224, 380, 687]
    assert [A.necklaces_formula(n, 3) for n in range(1, 11)] == [3, 6, 11, 24, 51, 130, 315, 834, 2195, 5934]


def test_readme_board():
    assert [A.square_formula(s, 2, m) for s in (2, 3, 4) for m in ("Drehungen", "Drehungen und Spiegelungen")] == [6, 6, 140, 102, 16456, 8548]
    a = ev.analyse(SETTINGS(**C.PRESETS["Brett 3×3 mit Drehungen und Spiegelungen"]))
    assert a.total == 512 and a.approx == 64 and round(100 * ev.approx_error(a), 2) == -37.25


def test_readme_approximation_table():
    res = ev.approx_rows()
    s2 = res["series"][2]
    assert [round(100 * s2[n], 3) for n in (3, 5, 6, 7, 8, 10, 11, 12, 13, 16, 20, 24, 30)] == [-33.333, -20.0, -23.81, -8.571, -11.111, -5.185, -0.967, -3.03, -0.292, -0.486, -0.113, -0.029, -0.003]
    assert (res["first_below_1"], res["first_below_01"]) == (11, 17) and res["lower_bound"] is True
    assert [round(100 * res["series"][3][n], 3) for n in (4, 8, 12)] == [-15.625, -1.664, -0.183]
    assert [round(100 * res["series"][10][n], 3) for n in (4, 8)] == [-1.186, -0.01] and abs(100 * res["series"][10][12]) < 0.0002
    assert [round(100 * res["bracelets"][n], 2) for n in (6, 8, 10, 12, 16, 20, 30)] == [-58.97, -46.67, -34.36, -23.81, -8.98, -2.95, -0.14]
    assert round(100 * s2[30], 4) == -0.0033


def test_readme_prime_size_formula_and_the_divisor_effect():
    for n in (11, 13):
        assert A.necklaces_formula(n, 2) == (2 ** n + (n - 1) * 2) // n
    assert abs(ev.approx_rows()["series"][2][12]) > 3 * abs(ev.approx_rows()["series"][2][11])


def test_readme_weights():
    res = ev.weight_rows()
    assert res["chain"] == [1, 1, 4, 7, 10, 7, 4, 1, 1] and res["chain_sum"] == 36
    assert res["board"] == [1, 3, 8, 16, 23, 23, 16, 8, 3, 1] and res["board_sum"] == 102 and res["chain_equal_all"] is True


def test_readme_graphs():
    assert [A.graphs_polya(n) for n in range(1, 11)] == [1, 2, 4, 11, 34, 156, 1044, 12346, 274668, 12005168]
    g = ev.graph_rows()
    assert [(r["n"], r["Zyklentypen"]) for r in g["rows"]] == [(5, 7), (8, 22), (10, 42), (15, 176), (20, 627), (30, 5604)]
    assert [math.factorial(r["n"]) for r in g["rows"]][:4] == [120, 40320, 3628800, 1307674368000] and float(f"{math.factorial(20):.2g}") == 2.4e18 and float(f"{math.factorial(30):.2g}") == 2.7e32
    ratios = ev.approx_rows()["graphs"]
    assert [round(float(ratios[n]), 3) for n in range(2, 11)] == [2.0, 3.0, 4.125, 3.984, 3.428, 2.509, 1.854, 1.45, 1.238]
    assert [round(float(ratios[n]), 4) for n in (12, 15, 20)] == [1.0717, 1.0131, 1.0007] and round(float(ratios[30]), 6) == 1.000002
    assert [str(r["Mittel 1/|Aut|"]) for r in g["mean"]] == ["1/2", "1/3", "8/33", "64/255", "512/1755"] and all(r["gleich"] for r in g["mean"])
    assert g["euler"][1:13] == g["polya"][1:13] == [1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1842, 4766]


def test_readme_schedules():
    rows = ev.schedule_rows()
    assert [(r["Teams"], r["Pläne"], r["Bahnen"]) for r in rows] == [(4, 1, 1), (6, 6, 1), (8, 6240, 6)]
    r8 = rows[-1]
    assert r8["Bahngrößen"] == [30, 420, 630, 960, 1680, 2520] and r8["|Aut|"] == [1344, 96, 64, 42, 24, 16] and r8["Σ n!/|Aut|"] == 6240
    assert [round(float(r["Gesamtzahl/n!"]), 4) for r in rows] == [0.0417, 0.0083, 0.1548] and [r["mit Reihenfolge der Runden"] for r in rows] == [6, 720, 31449600]


def test_preset_help_claims():
    h = C.PRESET_HELP
    assert "14 Halsketten" in h["Standardfall: Halsketten, n = 6, 2 Farben"] and "(64 + 2 + 4 + 8 + 4 + 2)/6" in h["Standardfall: Halsketten, n = 6, 2 Farben"] and (64 + 2 + 4 + 8 + 4 + 2) / 6 == 14
    assert "13 Armbänder" in h["Armbänder: mit Spiegelungen, n = 6"] and (84 + 3 * 16 + 3 * 8) / 12 == 13
    board = h["Brett 3×3 mit Drehungen und Spiegelungen"]
    assert "102 Bahnen" in board and "140" in board and "512/8 = 64" in board and "37 %" in board and round(100 * (1 - 64 / 102)) == 37
    graphs = ev.analyse(SETTINGS(**C.PRESETS["Graphen auf 10 Knoten"]))
    assert graphs.orbits == 12005168 and graphs.extras["types"] == 42 and graphs.extras["elements"] == 3628800 and round(-100 * ev.approx_error(graphs)) == 19
    assert "12.005.168" in h["Graphen auf 10 Knoten"] and "42 Summanden" in h["Graphen auf 10 Knoten"] and "19 %" in h["Graphen auf 10 Knoten"]
    plan = ev.analyse(SETTINGS(**C.PRESETS["Spielpläne mit 8 Teams"]))
    assert plan.total == 6240 and plan.orbits == 6 and round(float(plan.approx), 3) == 0.155 and "6.240" in h["Spielpläne mit 8 Teams"] and "0,155" in h["Spielpläne mit 8 Teams"]
    twelve = ev.analyse(SETTINGS(**C.PRESETS["Halsketten n = 12 (viele Teiler)"]))
    assert round(-100 * ev.approx_error(twelve), 1) == 3.0 and "3,0 %" in h["Halsketten n = 12 (viele Teiler)"] and "0,97 %" in h["Halsketten n = 12 (viele Teiler)"] and "0,29 %" in h["Halsketten n = 12 (viele Teiler)"]


def test_readme_states_the_test_count_and_ends_with_the_footer():
    assert "Stück 11 von 16" in README and "Zählen bis auf Symmetrie" in README and "TESTCOUNT" not in README
    assert README.rstrip().endswith("[Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html).")
