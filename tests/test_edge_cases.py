"""Randfälle: Grenzen der Regler, unbekannte Eingaben, entartete Gruppen, riesige Zahlen, Formatierung."""

from fractions import Fraction

import pytest

import bpo_algorithm as A
import bpo_constants as C
import bpo_evaluation as ev

SETTINGS = ev.Settings


def test_effective_n_k_and_symmetry():
    assert ev.effective_n("Perlenketten", 0) == 1 and ev.effective_n("Perlenketten", 500) == 60 and ev.effective_n("Brett s×s", 50) == 8 and ev.effective_n("Graphen", 50) == 30
    assert ev.effective_k(0) == 1 and ev.effective_k(99) == 10
    assert ev.effective_symmetry("Perlenketten", "keine") == "keine" and ev.effective_symmetry("Graphen", "keine") == "Drehungen"
    with pytest.raises(ValueError):
        ev.effective_n("Unbekannt", 5)
    with pytest.raises(ValueError):
        ev.effective_symmetry("Perlenketten", "Zauber")


def test_notes_for_clamped_and_fixed_settings():
    a = ev.analyse(SETTINGS("Brett s×s", 20, 99, "Drehungen"))
    assert a.n_eff == 8 and a.k_eff == 10 and len(a.notes) == 2
    b = ev.analyse(SETTINGS("Graphen", 5, 2, "keine"))
    assert any("ist die Symmetrie fest" in n for n in b.notes) and b.symmetry_eff == "Drehungen"
    c = ev.analyse(SETTINGS("Spielpläne eines Rundenturniers", 5, 2, "Drehungen"))
    assert c.n_eff == 6 and any("gerade Teamzahlen" in n for n in c.notes)


def test_smallest_sizes_and_one_colour():
    for fam in ("Perlenketten", "Brett s×s", "Graphen"):
        for sym in C.SYMMETRIES:
            a = ev.analyse(SETTINGS(fam, 1, 1, sym))
            assert a.problems == [] and a.total >= 1 and a.orbits == 1, (fam, sym)
    assert ev.analyse(SETTINGS("Perlenketten", 2, 2, "Drehungen und Spiegelungen")).orbits == 3
    assert ev.analyse(SETTINGS("Perlenketten", 1, 7, "Drehungen")).orbits == 7


def test_no_symmetry_gives_the_total_and_trivial_group():
    a = ev.analyse(SETTINGS("Perlenketten", 8, 3, "keine"))
    assert a.group_order == 1 and a.orbits == a.total == 3 ** 8 and a.approx == a.total
    assert "Ohne Symmetrie ist jedes Objekt eine eigene Bahn" in ev.verdict_answers(a)[1]


def test_huge_numbers_do_not_need_string_conversion():
    a = ev.analyse(SETTINGS("Perlenketten", 60, 10, "Drehungen und Spiegelungen"))
    assert a.group_order == 120 and a.total == 10 ** 60 and A.digit_count(a.orbits) >= 58 and a.problems == []
    assert any(w["Wert"] is None and "Färbungen" in w["Grund"] for w in a.ways)
    b = ev.analyse(SETTINGS("Graphen", 30, 2, "Drehungen"))
    assert A.digit_count(b.total) == 131 and b.extras["types"] == 5604 and b.problems == []
    assert ev.big_text(10 ** 5000).endswith("(5001 Stellen)") and A.digit_count(10 ** 5000) == 5001


def test_graph_ways_by_size():
    assert [len(ev.analyse(SETTINGS("Graphen", n, 2, "Drehungen")).ways) for n in (3, 7, 12)] == [3, 3, 3]
    skipped = {n: [w["Weg"] for w in ev.analyse(SETTINGS("Graphen", n, 2, "Drehungen")).ways if w["Wert"] is None] for n in (5, 7, 12)}
    assert skipped[5] == [] and len(skipped[7]) == 1 and len(skipped[12]) == 2


def test_formatting_helpers():
    assert ev.de(-1.5, 1) == "−1,5" and ev.sci_text(0) == "0" and ev.sci_text(1.23e-4, 3) == "1,23·10⁻⁴" and ev.percent(0.2381, 2) == "23,81 %"
    assert ev.big_text(0) == "0" and ev.big_text(999999999999) == "999.999.999.999" and ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.percent_fine(-3.3e-5, 2) == "−3,30·10⁻³ %" and ev.percent_fine(-0.0011, 2) == "−0,11 %" and ev.percent_fine(0, 2) == "0,00 %"
    assert ev.approx_text(Fraction(64, 1)) == "64" and ev.approx_text(Fraction(32, 3)) == "10,67" and ev.approx_text(Fraction(31, 200)) == "0,155" and ev.approx_text(Fraction(10 ** 60, 60)) == "1,67·10⁵⁸"
    assert ev.fraction_text(Fraction(4, 2)) == "2" and ev.fraction_text(Fraction(8, 33)) == "8/33"


def test_group_closure_limit_and_unknown_modes():
    with pytest.raises(ValueError):
        A.generate_group([A.square_generators(4)[0], A.square_generators(4)[1]], limit=3)
    with pytest.raises(ValueError):
        A.chain_group(4, "Zauber")
    with pytest.raises(ValueError):
        A.one_factorizations(7)


def test_graphs_by_all_elements_and_odd_edge_cases():
    assert A.graphs_by_all_elements(0) == 1 and A.graphs_by_all_elements(1) == 1 and A.graphs_polya(0) == 1
    assert A.graph_orbit_sizes(1) == [1] and A.graph_orbit_sizes(2) == [1, 1]


def test_play_board_clamps_and_skips_enumeration_when_large():
    r = ev.play_board(9, 9, "Drehungen")
    assert r["size"] == C.PLAY_SIDE_MAX and r["k"] == C.PLAY_K_MAX and r["enumerated"] is None and r["boards"] == [] and ev.verdict_play(r)[0] == "info"
    small = ev.play_board(1, 2, "Drehungen und Spiegelungen")
    assert small["orbits"] == 2 and small["enumerated"] == 2 and small["boards"] == [["0"], ["1"]]
    with pytest.raises(ValueError):
        ev.play_board(3, 2, "Zauber")


def test_play_board_shows_at_most_six_representatives_that_are_canonical():
    r = ev.play_board(3, 2, "Drehungen und Spiegelungen")
    assert len(r["boards"]) == C.SHOW_REPRESENTATIVES and r["enumerated"] == r["orbits"] == 102
    group = A.square_group(3, "Drehungen und Spiegelungen")
    assert all(A.canonical_form(rep, group) == rep for rep in r["reps"])
