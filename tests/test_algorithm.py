"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

import math
from fractions import Fraction

import pytest

import bpo_algorithm as A


def test_digit_count_ln_and_ratio():
    assert [A.digit_count(x) for x in (0, 1, 9, 10, 99, 100, 10 ** 50 - 1, 10 ** 50)] == [1, 1, 1, 2, 2, 3, 50, 51]
    with pytest.raises(ValueError):
        A.digit_count(-1)
    assert A.ln(10 ** 5000) == pytest.approx(5000 * math.log(10), rel=1e-12) and A.ln(Fraction(1, 2)) == pytest.approx(-math.log(2))
    with pytest.raises(ValueError):
        A.ln(0)
    assert A.ratio_minus_one(Fraction(32, 3), 14) == pytest.approx(-0.238095, abs=1e-6)


def test_divisors_phi_partitions():
    assert A.divisors(12) == [1, 2, 3, 4, 6, 12] and [A.phi(n) for n in (1, 2, 6, 12)] == [1, 1, 2, 4]
    assert list(A.partitions(4)) == [(4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1)] and A.partition_count(10) == 42
    assert A.z_lambda((2, 1)) == 2 and A.z_lambda((1, 1, 1)) == 6 and A.z_lambda((3,)) == 3 and A.z_lambda((2, 2)) == 8


def test_cyclic_and_dihedral_groups():
    assert A.cyclic_group(4) == [(0, 1, 2, 3), (1, 2, 3, 0), (2, 3, 0, 1), (3, 0, 1, 2)]
    assert len(A.dihedral_group(3)) == 6 and len(A.dihedral_group(6)) == 12 and len(A.dihedral_group(2)) == 2 and len(A.dihedral_group(1)) == 1
    with pytest.raises(ValueError):
        A.cyclic_group(0)
    assert A.cycle_lengths((1, 2, 0, 3)) == [3, 1] and A.cycle_count((1, 0, 3, 2)) == 2


def test_burnside_necklaces_hand(hand_necklaces):
    assert A.burnside_terms(A.cyclic_group(4), 2) == hand_necklaces["fix4"]
    assert A.burnside_count(A.cyclic_group(4), 2) == hand_necklaces["n4"] == A.necklaces_formula(4, 2)
    assert A.burnside_terms(A.cyclic_group(6), 2) == hand_necklaces["fix6"]
    assert A.burnside_count(A.cyclic_group(6), 2) == hand_necklaces["n6"] and A.burnside_count(A.dihedral_group(6), 2) == hand_necklaces["bracelets6"] == A.bracelets_formula(6, 2)
    reps = A.orbit_representatives(A.cyclic_group(4), 2, 4)
    assert reps == hand_necklaces["classes4"]


def test_formula_special_cases():
    assert [A.necklaces_formula(n, 1) for n in range(1, 8)] == [1] * 7
    assert A.necklaces_formula(5, 2) == 8 and A.necklaces_formula(7, 3) == 315 and A.bracelets_formula(5, 2) == 8 and A.bracelets_formula(1, 5) == 5
    assert A.chain_formula(5, 3, "keine") == 243 and A.chain_formula(4, 2, "Drehungen") == 6 and A.chain_formula(6, 2, "Drehungen und Spiegelungen") == 13
    with pytest.raises(ValueError):
        A.chain_formula(4, 2, "Unsinn")
    with pytest.raises(ValueError):
        A.chain_group(4, "Unsinn")


def test_canonical_form():
    assert A.canonical_form((1, 0, 0, 0), A.cyclic_group(4)) == (0, 0, 0, 1) and A.canonical_form((1, 0, 1, 0), A.cyclic_group(4)) == (0, 1, 0, 1)


def test_square_group_and_formula(hand_board_2):
    assert [len(A.square_group(3, m)) for m in ("keine", "Drehungen", "Drehungen und Spiegelungen")] == [1, 4, 8]
    assert A.square_formula(2, 2, "Drehungen") == hand_board_2["rot"] and A.square_formula(2, 2, "Drehungen und Spiegelungen") == hand_board_2["d4"]
    assert A.square_formula(3, 2, "Drehungen") == 140 and A.square_formula(3, 2, "Drehungen und Spiegelungen") == 102 and A.square_formula(3, 2, "keine") == 512
    assert A.square_formula(1, 5, "Drehungen und Spiegelungen") == 5
    c = A.square_cycle_counts(2)
    assert [c["id"], c["rot90"], c["rot180"]] == [4, 1, 2] == hand_board_2["cycles"][:3]
    with pytest.raises(ValueError):
        A.square_group(3, "Unsinn")


def test_generate_group_limit():
    rot, refl = A.square_generators(3)
    assert len(A.generate_group([rot, refl])) == 8
    with pytest.raises(ValueError):
        A.generate_group([rot, refl], limit=5)


def test_weight_distribution_hand():
    # n = 4: 0000, 0001, 0011, 0101, 0111, 1111 nach Zahl der Einsen: 1, 1, 2, 1, 1
    assert A.weight_distribution(A.cyclic_group(4)) == [1, 1, 2, 1, 1] == A.weight_distribution_brute(A.cyclic_group(4))
    assert sum(A.weight_distribution(A.cyclic_group(8))) == 36 and A.weight_distribution(A.cyclic_group(8)) == [1, 1, 4, 7, 10, 7, 4, 1, 1]


def test_graphs_hand(hand_graphs_3):
    for lam, (z, cycles) in hand_graphs_3["types"].items():
        assert A.z_lambda(lam) == z and A.pair_cycles(lam) == cycles
    assert A.graphs_polya(3) == hand_graphs_3["orbits"] == A.graphs_by_all_elements(3) == len(A.graph_orbit_sizes(3))
    sizes = A.graph_orbit_sizes(3)
    assert sizes == [1, 1, 3, 3] and sum(Fraction(s, 6) for s in sizes) / 4 == hand_graphs_3["mean_inv_aut"] == Fraction(hand_graphs_3["labelled"], 6 * 4)
    assert [A.graphs_polya(n) for n in range(0, 7)] == [1, 1, 2, 4, 11, 34, 156]
    assert A.graph_orbit_sizes(1) == [1]


def test_rooted_trees_euler_and_polya():
    assert A.rooted_trees_euler(10) == [0, 1, 1, 2, 4, 9, 20, 48, 115, 286, 719] and A.rooted_trees_polya(8) == A.rooted_trees_euler(8)


def test_one_factorizations_hand(hand_plans):
    assert len(A.one_factorizations(4)) == hand_plans["k4"] and len(A.one_factorizations(6)) == hand_plans["k6"]
    assert A.plan_orbit_sizes(A.one_factorizations(4), 4) == [1] and A.plan_orbit_sizes(A.one_factorizations(6), 6) == [6]
    plan4, plan6 = A.one_factorizations(4)[0], A.one_factorizations(6)[0]
    assert A.automorphism_count(plan4, 4) == hand_plans["k4_aut"] and A.automorphism_count(plan6, 6) == hand_plans["k6_aut"]
    assert A.plan_text(plan4) == "1-2 3-4 | 1-3 2-4 | 1-4 2-3"
    with pytest.raises(ValueError):
        A.one_factorizations(5)
    assert len(A.plan_orbit_representatives(A.one_factorizations(6), 6)) == 1
