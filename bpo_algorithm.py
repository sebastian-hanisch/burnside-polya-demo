"""Rechenkern: Zählen bis auf Symmetrie. Burnside (Mittel der Fixpunkte), Pólya (Zyklenindex, Gewicht), Aufzählen der Bahnen, Graphen über Zyklentypen, Spielpläne als 1-Faktorisierungen.

Alles mit `int` und `fractions.Fraction`. Eine Permutation ist ein Tupel p mit p[i] = Bild von i."""

import itertools
import math
from fractions import Fraction


# ----------------------------------------------------------------------------- Zahlen

def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def ln(x) -> float:
    """Natürlicher Logarithmus einer beliebig großen ganzen oder gebrochenen positiven Zahl."""
    if isinstance(x, Fraction):
        return ln(x.numerator) - ln(x.denominator)
    if x <= 0:
        raise ValueError("Logarithmus verlangt eine positive Zahl")
    if x.bit_length() < 1000:
        return math.log(x)
    shift = x.bit_length() - 900
    return math.log(x >> shift) + shift * math.log(2)


def ratio_minus_one(a, b) -> float:
    """a/b − 1 als Gleitkommazahl für beliebig große ganze Zahlen oder Brüche (über Brüche gerechnet, ohne Überlauf)."""
    return float(Fraction(a) / Fraction(b) - 1)


def divisors(n: int) -> list:
    return [d for d in range(1, n + 1) if n % d == 0]


def phi(n: int) -> int:
    return sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)


def partitions(n: int, maximum: int | None = None):
    """Alle Partitionen von n als absteigende Tupel."""
    if maximum is None:
        maximum = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, maximum), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def partition_count(n: int) -> int:
    p = [1] + [0] * n
    for part in range(1, n + 1):
        for total in range(part, n + 1):
            p[total] += p[total - part]
    return p[n]


def z_lambda(lam: tuple) -> int:
    """Ordnung des Zentralisators einer Permutation vom Zyklentyp lam: Π i^m_i · m_i! (n!/z = Zahl der Permutationen dieses Typs)."""
    out = 1
    for i in set(lam):
        m = lam.count(i)
        out *= i ** m * math.factorial(m)
    return out


# ----------------------------------------------------------------------------- Gruppen aus Permutationen

def compose(p: tuple, q: tuple) -> tuple:
    """(p nach q): i → p[q[i]]."""
    return tuple(p[i] for i in q)


def generate_group(gens: list, limit: int | None = None) -> list:
    """Alle Elemente der von den Permutationen erzeugten Gruppe (Abschluss); mit `limit` Abbruch durch ValueError, wenn sie größer ist."""
    ident = tuple(range(len(gens[0])))
    group = {ident}
    frontier = [ident]
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                x = compose(h, g)
                if x not in group:
                    group.add(x)
                    new.append(x)
                    if limit is not None and len(group) > limit:
                        raise ValueError("Gruppe zu groß")
        frontier = new
    return sorted(group)


def cyclic_group(n: int) -> list:
    """Drehungen der Perlenkette (n Positionen)."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein")
    return [tuple((i + j) % n for i in range(n)) for j in range(n)]


def dihedral_group(n: int) -> list:
    """Drehungen und Spiegelungen: 2n Elemente für n >= 3, für n = 1, 2 entfallen doppelte Elemente."""
    elems = set(cyclic_group(n))
    for j in range(n):
        elems.add(tuple((j - i) % n for i in range(n)))
    return sorted(elems)


def square_generators(size: int) -> tuple:
    """Drehung um 90° und Spiegelung an der senkrechten Achse als Permutationen der s² Zellen (Zeile mal s plus Spalte)."""
    cells = [(r, c) for r in range(size) for c in range(size)]
    idx = {cell: i for i, cell in enumerate(cells)}
    rot = tuple(idx[(c, size - 1 - r)] for r, c in cells)
    refl = tuple(idx[(r, size - 1 - c)] for r, c in cells)
    return rot, refl


def square_group(size: int, mode: str) -> list:
    """Gruppe des Bretts: 'keine' (nur die Identität), 'Drehungen' (4) oder 'Drehungen und Spiegelungen' (8; bei 1×1 nur 1)."""
    rot, refl = square_generators(size)
    if mode == "keine":
        return [tuple(range(size * size))]
    if mode == "Drehungen":
        return generate_group([rot])
    if mode == "Drehungen und Spiegelungen":
        return generate_group([rot, refl])
    raise ValueError(f"unbekannte Symmetrie {mode!r}")


def cycle_lengths(g: tuple) -> list:
    seen = [False] * len(g)
    out = []
    for i in range(len(g)):
        if not seen[i]:
            length, j = 0, i
            while not seen[j]:
                seen[j] = True
                j = g[j]
                length += 1
            out.append(length)
    return out


def cycle_count(g: tuple) -> int:
    return len(cycle_lengths(g))


def burnside_terms(group: list, k: int) -> list:
    """Fixpunkte der k-Färbungen je Gruppenelement: k^(Zahl der Zyklen)."""
    return [k ** cycle_count(g) for g in group]


def burnside_count(group: list, k: int) -> int:
    terms = burnside_terms(group, k)
    total = sum(terms)
    if total % len(group):
        raise ValueError("Summe der Fixpunkte nicht durch |G| teilbar")
    return total // len(group)


def canonical_form(t: tuple, group: list) -> tuple:
    return min(tuple(t[g[i]] for i in range(len(t))) for g in group)


def orbit_representatives(group: list, k: int, cells: int) -> list:
    """Alle Bahnen der k-Färbungen von `cells` Positionen als kleinste Form (lexikografisch), in aufsteigender Reihenfolge."""
    seen = set()
    reps = []
    for t in itertools.product(range(k), repeat=cells):
        if t in seen:
            continue
        reps.append(t)
        for g in group:
            seen.add(tuple(t[g[i]] for i in range(cells)))
    return reps


# ----------------------------------------------------------------------------- Halsketten und Armbänder (geschlossene Formeln)

def necklaces_formula(n: int, k: int) -> int:
    """(1/n) Σ_{d|n} φ(d)·k^(n/d): Bahnen unter den Drehungen."""
    return sum(phi(d) * k ** (n // d) for d in divisors(n)) // n


def bracelets_formula(n: int, k: int) -> int:
    """Bahnen unter Drehungen und Spiegelungen (Gruppe D_n; für n = 1, 2 gleich den Halsketten)."""
    if n <= 2:
        return necklaces_formula(n, k)
    nk = necklaces_formula(n, k)
    if n % 2:
        return (nk + k ** ((n + 1) // 2)) // 2
    return (2 * nk + (k + 1) * k ** (n // 2)) // 4


def chain_formula(n: int, k: int, mode: str) -> int:
    if mode == "keine":
        return k ** n
    if mode == "Drehungen":
        return necklaces_formula(n, k)
    if mode == "Drehungen und Spiegelungen":
        return bracelets_formula(n, k)
    raise ValueError(f"unbekannte Symmetrie {mode!r}")


def chain_group(n: int, mode: str) -> list:
    if mode == "keine":
        return [tuple(range(n))]
    if mode == "Drehungen":
        return cyclic_group(n)
    if mode == "Drehungen und Spiegelungen":
        return dihedral_group(n)
    raise ValueError(f"unbekannte Symmetrie {mode!r}")


def square_cycle_counts(size: int) -> dict:
    """Zyklen der Brett-Symmetrien auf den Zellen, aus der Geometrie (nicht aus den Permutationen): Identität, Drehung 90°, Drehung 180°, Achsenspiegelung, Diagonalspiegelung."""
    cells = size * size
    odd = size % 2
    return {"id": cells, "rot90": (cells - odd) // 4 + odd, "rot180": (cells - odd) // 2 + odd,
            "achse": (cells + size) // 2 if odd else cells // 2, "diagonale": (cells + size) // 2}


def square_formula(size: int, k: int, mode: str) -> int:
    c = square_cycle_counts(size)
    if mode == "keine":
        return k ** c["id"]
    rot = k ** c["id"] + 2 * k ** c["rot90"] + k ** c["rot180"]
    if mode == "Drehungen" or size == 1:
        return rot // 4
    return (rot + 2 * k ** c["achse"] + 2 * k ** c["diagonale"]) // 8


# ----------------------------------------------------------------------------- Pólya mit Gewicht

def poly_mul(a: list, b: list) -> list:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def poly_pow(a: list, e: int) -> list:
    out = [1]
    for _ in range(e):
        out = poly_mul(out, a)
    return out


def weight_distribution(group: list) -> list:
    """Bahnen der Zweifärbungen nach Zahl der Einsen: Pólya mit x_l → 1 + y^l, für jedes Gruppenelement Π (1 + y^l) über seine Zyklen; Liste c[j]."""
    cells = len(group[0])
    total = [0] * (cells + 1)
    for g in group:
        poly = [1]
        for length in cycle_lengths(g):
            poly = poly_mul(poly, [1] + [0] * (length - 1) + [1])
        for i, c in enumerate(poly):
            total[i] += c
    if any(c % len(group) for c in total):
        raise ValueError("Summe nicht durch |G| teilbar")
    return [c // len(group) for c in total]


def weight_distribution_brute(group: list) -> list:
    cells = len(group[0])
    counts = [0] * (cells + 1)
    for t in orbit_representatives(group, 2, cells):
        counts[sum(t)] += 1
    return counts


# ----------------------------------------------------------------------------- Graphen

def pair_cycles(lam: tuple) -> int:
    """Zahl der Zyklen eines Elements vom Typ lam auf den Knotenpaaren: Σ ⌊l/2⌋ + Σ_{i<j} ggT(l_i, l_j)."""
    c = sum(l // 2 for l in lam)
    for i in range(len(lam)):
        for j in range(i + 1, len(lam)):
            c += math.gcd(lam[i], lam[j])
    return c


def graph_terms(n: int) -> list:
    """Für jeden Zyklentyp: (Typ, Zahl der Elemente n!/z, Fixpunkte 2^c) mit c = Zyklen auf den Paaren."""
    return [(lam, math.factorial(n) // z_lambda(lam), 2 ** pair_cycles(lam)) for lam in partitions(n)]


def graphs_polya(n: int) -> int:
    """Zahl der Graphen auf n Knoten bis auf Umbenennen: Σ über Zyklentypen von 2^c/z."""
    total = Fraction(0)
    for lam in partitions(n):
        total += Fraction(2 ** pair_cycles(lam), z_lambda(lam))
    if total.denominator != 1:
        raise ValueError("Summe nicht ganzzahlig")
    return int(total)


def graphs_by_all_elements(n: int) -> int:
    """Dasselbe als Burnside-Summe über alle n! Permutationen (nur für kleine n): Zyklen der Paare jeder einzelnen Permutation."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pidx = {p: i for i, p in enumerate(pairs)}
    total = 0
    for sigma in itertools.permutations(range(n)):
        perm = tuple(pidx[(min(sigma[a], sigma[b]), max(sigma[a], sigma[b]))] for a, b in pairs)
        total += 2 ** cycle_count(perm)
    f = math.factorial(n)
    if total % f:
        raise ValueError("Summe nicht durch n! teilbar")
    return total // f


def graph_orbit_sizes(n: int) -> list:
    """Größen der Bahnen aller 2^C(n,2) beschrifteten Graphen unter S_n (Union-Find über Transposition und n-Zyklus)."""
    if n < 2:
        return [1]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pidx = {p: i for i, p in enumerate(pairs)}
    m = len(pairs)

    def on_pairs(sigma):
        return [pidx[(min(sigma[a], sigma[b]), max(sigma[a], sigma[b]))] for a, b in pairs]

    gens = [on_pairs([1, 0] + list(range(2, n))), on_pairs(list(range(1, n)) + [0])]
    parent = list(range(1 << m))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def apply(g, mask):
        out = 0
        for i in range(m):
            if mask >> i & 1:
                out |= 1 << g[i]
        return out

    for mask in range(1 << m):
        for g in gens:
            a, b = find(mask), find(apply(g, mask))
            if a != b:
                parent[a] = b
    sizes = {}
    for mask in range(1 << m):
        r = find(mask)
        sizes[r] = sizes.get(r, 0) + 1
    return sorted(sizes.values())


# ----------------------------------------------------------------------------- Wurzelbäume ohne Reihenfolge (Stück 3 und 5)

def rooted_trees_euler(nmax: int) -> list:
    """a(n) aus der Euler-Transformation (Stück 5): a(n+1) = (1/n) Σ_{k=1..n} (Σ_{d|k} d·a(d))·a(n−k+1)."""
    a = [0, 1]
    for n in range(1, nmax):
        s = 0
        for k in range(1, n + 1):
            s += sum(d * a[d] for d in divisors(k)) * a[n - k + 1]
        a.append(s // n)
    return a[: nmax + 1]


def rooted_trees_polya(nmax: int) -> list:
    """Dieselben Zahlen über Pólya: ein Wurzelbaum ist die Wurzel mit einer Multimenge von Teilbäumen, der Zyklenindex von S_k wirkt auf die k Kinder, x_i → T(z^i)."""
    a = [0, 1]
    for n in range(1, nmax):
        total = Fraction(0)
        for k in range(1, n + 1):
            for lam in partitions(k):
                poly = [1] + [0] * n
                for i in set(lam):
                    ti = [0] * (n + 1)
                    for s in range(1, len(a)):
                        if s * i <= n:
                            ti[s * i] = a[s]
                    for _ in range(lam.count(i)):
                        new = [0] * (n + 1)
                        for x, cx in enumerate(poly):
                            if cx:
                                for y, cy in enumerate(ti):
                                    if cy and x + y <= n:
                                        new[x + y] += cx * cy
                        poly = new
                total += Fraction(poly[n], z_lambda(lam))
        if total.denominator != 1:
            raise ValueError("Summe nicht ganzzahlig")
        a.append(int(total))
    return a[: nmax + 1]


# ----------------------------------------------------------------------------- Spielpläne = 1-Faktorisierungen von K_n

def one_factorizations(nv: int) -> list:
    """Alle Spielpläne eines Rundenturniers mit nv Teams (nv gerade): Mengen von nv−1 Runden, jede Runde eine perfekte Paarung; Rückverfolgung, jeder Plan genau einmal
    (die Runden werden nach dem Gegner von Team 0 aufsteigend geordnet)."""
    if nv < 2 or nv % 2:
        raise ValueError("Spielpläne nur für gerade nv >= 2")
    edges = frozenset((i, j) for i in range(nv) for j in range(i + 1, nv))
    result = []

    def matchings(avail, nodes):
        if not nodes:
            yield ()
            return
        a = nodes[0]
        for b in nodes[1:]:
            if (a, b) in avail:
                rest = [x for x in nodes if x != a and x != b]
                for m in matchings(avail, rest):
                    yield ((a, b),) + m

    def rec(avail, rounds, last):
        if not avail:
            result.append(frozenset(frozenset(r) for r in rounds))
            return
        for m in matchings(avail, list(range(nv))):
            opponent = [b for a, b in m if a == 0][0]
            if opponent <= last:
                continue
            rec(avail - frozenset(m), rounds + [m], opponent)

    rec(edges, [], 0)
    return result


def relabel(plan, sigma) -> frozenset:
    return frozenset(frozenset(tuple(sorted((sigma[a], sigma[b]))) for a, b in rnd) for rnd in plan)


def plan_orbit_sizes(plans: list, nv: int) -> list:
    """Bahnen der Pläne unter Umbenennen der Teams (S_nv), über zwei Erzeuger mit Union-Find; Rückgabe: Bahngrößen, aufsteigend."""
    index = {p: i for i, p in enumerate(plans)}
    parent = list(range(len(plans)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    gens = [[1, 0] + list(range(2, nv)), list(range(1, nv)) + [0]]
    for p in plans:
        for g in gens:
            a, b = find(index[p]), find(index[relabel(p, g)])
            if a != b:
                parent[a] = b
    sizes = {}
    for i in range(len(plans)):
        r = find(i)
        sizes[r] = sizes.get(r, 0) + 1
    return sorted(sizes.values())


def plan_orbit_representatives(plans: list, nv: int) -> list:
    """Ein Plan je Bahn (der erste in der Reihenfolge von `plans`), passend zu `plan_orbit_sizes`."""
    index = {p: i for i, p in enumerate(plans)}
    parent = list(range(len(plans)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    gens = [[1, 0] + list(range(2, nv)), list(range(1, nv)) + [0]]
    for p in plans:
        for g in gens:
            a, b = find(index[p]), find(index[relabel(p, g)])
            if a != b:
                parent[a] = b
    first = {}
    for i, p in enumerate(plans):
        first.setdefault(find(i), p)
    return list(first.values())


def automorphism_count(plan, nv: int) -> int:
    """|Aut| des Plans: Zahl der Permutationen der Teams, die den Plan in sich überführen (direkt durch Durchprobieren aller nv! Permutationen)."""
    return sum(1 for sigma in itertools.permutations(range(nv)) if relabel(plan, sigma) == plan)


def plan_text(plan) -> str:
    """Plan als Text: Runden nach dem Gegner von Team 1 geordnet (Teams 1 bis nv)."""
    rounds = sorted(sorted(tuple(sorted(e)) for e in rnd) for rnd in plan)
    return " | ".join(" ".join(f"{a + 1}-{b + 1}" for a, b in rnd) for rnd in rounds)
