"""Unabhängige Orakel: jede Bahnenzahl über einen zweiten Weg, der die Formeln des Rechenkerns nicht benutzt."""

import itertools
import math
from fractions import Fraction

import bpo_algorithm as A


def brute_necklaces(n, k):
    return len({min(t[i:] + t[:i] for i in range(n)) for t in itertools.product(range(k), repeat=n)})


def brute_bracelets(n, k):
    seen = set()
    for t in itertools.product(range(k), repeat=n):
        forms = [t[i:] + t[:i] for i in range(n)] + [t[::-1][i:] + t[::-1][:i] for i in range(n)]
        seen.add(min(forms))
    return len(seen)


def test_necklace_and_bracelet_formulas_against_brute_force():
    for k in (1, 2, 3, 4):
        for n in range(1, 9):
            assert A.necklaces_formula(n, k) == brute_necklaces(n, k), (n, k)
            assert A.bracelets_formula(n, k) == brute_bracelets(n, k), (n, k)
    for n in range(9, 15):
        assert A.necklaces_formula(n, 2) == brute_necklaces(n, 2) and A.bracelets_formula(n, 2) == brute_bracelets(n, 2)


def test_burnside_over_explicit_groups_against_brute_force():
    for n in range(1, 8):
        assert A.burnside_count(A.cyclic_group(n), 3) == brute_necklaces(n, 3)
        assert A.burnside_count(A.dihedral_group(n), 3) == brute_bracelets(n, 3)


def test_fixed_points_counted_by_brute_force_equal_k_to_the_cycles():
    for n in (4, 5, 6):
        for g in A.dihedral_group(n):
            for k in (2, 3):
                fixed = sum(1 for t in itertools.product(range(k), repeat=n) if all(t[g[i]] == t[i] for i in range(n)))
                assert fixed == k ** A.cycle_count(g)


def test_orbit_stabilizer_the_orbit_sizes_add_up_to_the_total():
    n, k = 6, 2
    group = A.dihedral_group(n)
    seen, sizes = set(), []
    for t in itertools.product(range(k), repeat=n):
        if t in seen:
            continue
        orbit = {tuple(t[g[i]] for i in range(n)) for g in group}
        stab = sum(1 for g in group if tuple(t[g[i]] for i in range(n)) == t)
        assert len(orbit) * stab == len(group)
        seen |= orbit
        sizes.append(len(orbit))
    assert sum(sizes) == k ** n and len(sizes) == A.bracelets_formula(n, k)


def test_square_cycle_counts_from_geometry_equal_the_permutation_cycles():
    for size in range(1, 9):
        rot, refl = A.square_generators(size)
        c = A.square_cycle_counts(size)
        assert A.cycle_count(tuple(range(size * size))) == c["id"] and A.cycle_count(rot) == c["rot90"]
        assert A.cycle_count(A.compose(rot, rot)) == c["rot180"] and A.cycle_count(refl) == c["achse"]
        assert A.cycle_count(A.compose(rot, refl)) == c["diagonale"]


def test_square_formula_against_group_elements_and_brute_force():
    for size in range(1, 9):
        for mode in ("keine", "Drehungen", "Drehungen und Spiegelungen"):
            assert A.square_formula(size, 3, mode) == A.burnside_count(A.square_group(size, mode), 3), (size, mode)
    for size, k in ((2, 2), (2, 3), (3, 2), (3, 3), (4, 2)):
        for mode in ("Drehungen", "Drehungen und Spiegelungen"):
            assert A.square_formula(size, k, mode) == len(A.orbit_representatives(A.square_group(size, mode), k, size * size)), (size, k, mode)


def test_weight_distribution_against_brute_force():
    for n in range(1, 13):
        assert A.weight_distribution(A.cyclic_group(n)) == A.weight_distribution_brute(A.cyclic_group(n))
    for n in range(3, 8):
        assert A.weight_distribution(A.dihedral_group(n)) == A.weight_distribution_brute(A.dihedral_group(n))
    for size in (2, 3, 4):
        group = A.square_group(size, "Drehungen und Spiegelungen")
        assert A.weight_distribution(group) == A.weight_distribution_brute(group)


def test_pair_cycles_against_the_action_on_pairs():
    for n in range(2, 8):
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        pidx = {p: i for i, p in enumerate(pairs)}
        for sigma in itertools.islice(itertools.permutations(range(n)), 0, None, max(1, math.factorial(n) // 60)):
            perm = tuple(pidx[(min(sigma[a], sigma[b]), max(sigma[a], sigma[b]))] for a, b in pairs)
            lam = tuple(sorted(A.cycle_lengths(sigma), reverse=True))
            assert A.cycle_count(perm) == A.pair_cycles(lam)


def test_graph_counts_against_all_elements_orbits_and_known_sequence():
    known = [1, 1, 2, 4, 11, 34, 156, 1044, 12346, 274668, 12005168]        # aus dem Gedächtnis (A000088)
    assert [A.graphs_polya(n) for n in range(0, 11)] == known
    for n in range(0, 8):
        assert A.graphs_by_all_elements(n) == A.graphs_polya(n)
    for n in range(1, 7):
        assert len(A.graph_orbit_sizes(n)) == A.graphs_polya(n)


def test_class_sizes_of_the_symmetric_group_add_up_to_n_factorial():
    for n in range(1, 13):
        assert sum(math.factorial(n) // A.z_lambda(lam) for lam in A.partitions(n)) == math.factorial(n)
        assert sum(Fraction(1, A.z_lambda(lam)) for lam in A.partitions(n)) == 1


def test_mean_inverse_automorphism_equals_labelled_over_n_factorial_times_orbits():
    for n in range(2, 7):
        sizes = A.graph_orbit_sizes(n)
        fact = math.factorial(n)
        assert sum(sizes) == 2 ** (n * (n - 1) // 2) and all(fact % s == 0 for s in sizes)
        assert sum(Fraction(1, fact // s) for s in sizes) / len(sizes) == Fraction(2 ** (n * (n - 1) // 2), fact * len(sizes))


def canon_tree_count(n):
    """Wurzelbäume mit n Knoten als verschachtelte sortierte Tupel (eigene Rekursion über Multimengen von Teilbäumen)."""
    memo = {1: [()]}

    def trees(m):
        if m in memo:
            return memo[m]
        found = set()

        def split(rest, smallest, chosen):
            if rest == 0:
                found.add(tuple(sorted(chosen)))
                return
            for size in range(smallest, rest + 1):
                for t in trees(size):
                    split(rest - size, size, chosen + [t])

        split(m - 1, 1, [])
        memo[m] = sorted(found)
        return memo[m]

    return len(trees(n))


def test_rooted_trees_against_euler_and_a_direct_count():
    euler = A.rooted_trees_euler(12)
    assert euler == A.rooted_trees_polya(12) and euler[1:11] == [1, 1, 2, 4, 9, 20, 48, 115, 286, 719]
    assert [canon_tree_count(n) for n in range(1, 9)] == euler[1:9]


def valid_plan(plan, nv):
    pairs = [tuple(sorted(e)) for rnd in plan for e in rnd]
    return (len(plan) == nv - 1 and len(set(pairs)) == nv * (nv - 1) // 2 == len(pairs)
            and all(len(rnd) == nv // 2 and len({x for e in rnd for x in e}) == nv for rnd in plan))


def test_one_factorizations_are_valid_distinct_and_have_the_known_counts():
    for nv, count in ((4, 1), (6, 6), (8, 6240)):
        plans = A.one_factorizations(nv)
        assert len(plans) == len(set(plans)) == count and all(valid_plan(p, nv) for p in plans)
    sizes = A.plan_orbit_sizes(A.one_factorizations(8), 8)
    assert sizes == [30, 420, 630, 960, 1680, 2520] and sum(sizes) == 6240
    reps = A.plan_orbit_representatives(A.one_factorizations(8), 8)
    assert sorted(math.factorial(8) // A.automorphism_count(r, 8) for r in reps) == sizes


def test_the_circle_method_builds_a_valid_plan_inside_the_counted_set():
    """Die Zirkelmethode (round-robin-demo) baut einen der Pläne: ein Orakel dafür, dass die Aufzählung vollständig genug ist."""
    nv = 6
    teams = list(range(nv))
    rounds = []
    for r in range(nv - 1):
        circle = [teams[0]] + [teams[1 + (i + r) % (nv - 1)] for i in range(nv - 1)]
        rounds.append(frozenset(tuple(sorted((circle[i], circle[nv - 1 - i]))) for i in range(nv // 2)))
    plan = frozenset(rounds)
    assert valid_plan(plan, nv) and plan in set(A.one_factorizations(nv))
