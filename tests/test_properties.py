"""Eigenschaftstests (Schicht 2): Aussagen, die für ganze Klassen von Eingaben gelten, nicht nur für Einzelwerte."""

import math
from fractions import Fraction

import pytest

import bpo_algorithm as A
import bpo_constants as C
import bpo_evaluation as ev

SETTINGS = ev.Settings


def test_orbits_are_at_least_total_over_group_order_with_equality_only_for_the_free_action():
    for n in range(1, 25):
        for k in (1, 2, 3, 5):
            for group in (A.cyclic_group(n), A.dihedral_group(n)):
                orbits = A.burnside_count(group, k)
                assert orbits * len(group) >= k ** n
    assert [n for n in range(1, 40) if n * A.necklaces_formula(n, 2) == 2 ** n] == [1]


def test_bracelets_are_at_most_necklaces_which_are_at_most_all_colourings():
    for n in range(1, 30):
        for k in (1, 2, 3, 4):
            assert A.bracelets_formula(n, k) <= A.necklaces_formula(n, k) <= k ** n


def test_orbits_grow_with_the_colours_and_with_the_size():
    for n in range(1, 12):
        assert all(A.necklaces_formula(n, k) < A.necklaces_formula(n, k + 1) for k in range(1, 6))
    for k in (2, 3):
        assert all(A.necklaces_formula(n, k) < A.necklaces_formula(n + 1, k) for n in range(1, 30))


def test_group_orders_and_identity_contribution():
    for n in range(3, 16):
        assert len(A.cyclic_group(n)) == n and len(A.dihedral_group(n)) == 2 * n
        terms = A.burnside_terms(A.dihedral_group(n), 3)
        assert max(terms) == 3 ** n and terms.count(3 ** n) == 1 and all(t > 0 for t in terms)


def test_group_is_closed_under_composition():
    for size in (2, 3, 4):
        group = set(A.square_group(size, "Drehungen und Spiegelungen"))
        assert len(group) == (8 if size > 1 else 1)
        assert all(A.compose(g, h) in group for g in group for h in group)


def test_weight_distribution_sums_to_the_orbits_and_is_palindromic_for_two_colours():
    for n in range(1, 13):
        for group in (A.cyclic_group(n), A.dihedral_group(n)):
            dist = A.weight_distribution(group)
            assert sum(dist) == A.burnside_count(group, 2) and dist == dist[::-1]
    for size in (2, 3, 4):
        dist = A.weight_distribution(A.square_group(size, "Drehungen und Spiegelungen"))
        assert dist == dist[::-1] and sum(dist) == A.square_formula(size, 2, "Drehungen und Spiegelungen")


def test_error_of_the_approximation_for_a_prime_size_is_the_second_term_over_the_total():
    """Bei Primzahl n sind die Fixpunkte der n − 1 nichttrivialen Drehungen je k: exakt (k^n + (n − 1)·k)/n, also Fehler (n − 1)·k/(k^n + (n − 1)·k)."""
    for n in (5, 7, 11, 13, 17, 19, 23):
        for k in (2, 3):
            exact = A.necklaces_formula(n, k)
            assert exact == (k ** n + (n - 1) * k) // n
            err = Fraction(k ** n, n) / exact - 1
            assert err == -Fraction((n - 1) * k, k ** n + (n - 1) * k)


def test_graph_ratio_tends_to_one_from_above():
    prev = None
    for n in range(8, 25):
        ratio = Fraction(A.graphs_polya(n)) / Fraction(2 ** (n * (n - 1) // 2), math.factorial(n))
        assert ratio > 1 and (prev is None or ratio < prev)
        prev = ratio
    assert float(prev) < 1.0003


def test_graph_terms_cover_the_symmetric_group():
    for n in range(1, 13):
        terms = A.graph_terms(n)
        assert sum(count for _, count, _ in terms) == math.factorial(n) and len(terms) == A.partition_count(n)
        assert sum(Fraction(count * fix, math.factorial(n)) for _, count, fix in terms) == A.graphs_polya(n)


def test_every_analysis_agrees_on_all_ways_over_a_grid_of_settings():
    for fam, ns in (("Perlenketten", (1, 2, 3, 6, 9, 12, 17, 24)), ("Brett s×s", (1, 2, 3, 4)), ("Graphen", (1, 2, 4, 6, 8, 12))):
        for n in ns:
            for k in (1, 2, 3):
                for sym in C.SYMMETRIES:
                    if fam == "Graphen" and (k != 2 or sym != "Drehungen"):
                        continue
                    a = ev.analyse(SETTINGS(fam, n, k, sym))
                    assert a.problems == [] and a.orbits >= 1 and a.orbits <= a.total, (fam, n, k, sym)
                    assert a.approx <= a.orbits


def test_spielplan_sizes_are_made_even_and_bounded():
    assert [ev.effective_n("Spielpläne eines Rundenturniers", n) for n in (1, 4, 5, 6, 7, 8, 9, 60)] == [4, 4, 6, 6, 8, 8, 8, 8]


def test_schedule_data_is_consistent():
    for nv in (4, 6):
        d = ev.schedule_data(nv)
        assert d["sum_aut"] == d["plans"] == sum(d["sizes"]) and d["orbits"] == len(d["auts"]) == len(d["sizes"])
        assert all(math.factorial(nv) == a * s for a, s in zip(sorted(d["auts"], reverse=True), sorted(d["sizes"])))
