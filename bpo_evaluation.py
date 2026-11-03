"""Auswertung: die eingestellte Aufgabe auf mehreren Rechenwegen, fünf Experimente, die Spielwiese und die Urteilstexte. Alles deterministisch (keine Zufallszahlen)."""

import functools
import math
from dataclasses import dataclass, field
from fractions import Fraction

import bpo_algorithm as A
import bpo_constants as C

_SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


@dataclass(frozen=True)
class Settings:
    family: str
    n: int
    k: int
    symmetry: str


@dataclass
class Analysis:
    settings: Settings
    n_eff: int
    k_eff: int
    symmetry_eff: str
    group_order: int
    total: int                    # Zahl der Objekte ohne Symmetrie
    orbits: int                   # Bahnenzahl
    approx: Fraction              # Gesamtzahl/|G|
    ways: list                    # {"Gruppe", "Weg", "Wert", "Text", "Grund"}
    terms: list                   # (Beschriftung, Wert, Anteil) für das Diagramm
    problems: list
    notes: list
    extras: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def sci_text(x: float, digits: int = 2) -> str:
    """Gleitkommazahl als Mantisse mal Zehnerpotenz oder ohne Potenz, wenn sie klein genug ist."""
    if x == 0:
        return "0"
    if 0.01 <= abs(x) < 10000:
        return de(x, digits)
    mant, exp = f"{x:.{digits - 1}e}".split("e")
    return f"{mant.replace('.', ',').replace('-', '−')}·10{str(int(exp)).translate(_SUPER)}"


def percent(x: float, digits: int = 2) -> str:
    return de(100 * x, digits) + " %"


def percent_fine(x: float, digits: int = 2) -> str:
    """Prozent mit Nachkommastellen, bei winzigen Werten (unter 0,001 %) als Mantisse mal Zehnerpotenz, damit nicht „0,00 %“ dasteht."""
    return percent(x, digits) if x == 0 or round(abs(100 * x), digits) > 0 else sci_text(100 * x, 3) + " %"


def fraction_text(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def approx_text(x: Fraction) -> str:
    """Gesamtzahl/|G| als Zahl: ganz, wenn ganzzahlig, sonst mit Nachkommastellen oder als Zehnerpotenz."""
    if x.denominator == 1:
        return big_text(x.numerator)
    value = float(x) if x.numerator.bit_length() < 1000 and x.denominator.bit_length() < 1000 else float(Fraction(x.numerator // x.denominator))
    return sci_text(value, 3) if value >= 1000 else de(value, 3 if value < 1 else 2)


# ----------------------------------------------------------------------------- Grenzen

def effective_n(family: str, n: int) -> int:
    if family not in C.FAMILIES:
        raise ValueError(f"unbekannte Familie {family!r}")
    n = max(C.N_MIN, min(n, C.N_CAP[family], C.N_MAX))
    if family == "Spielpläne eines Rundenturniers":
        n = max(C.SCHEDULE_SIZES[0], n + n % 2)           # nur gerade Teamzahlen
        n = min(n, C.SCHEDULE_SIZES[-1])
    return n


def effective_k(k: int) -> int:
    return max(C.K_MIN, min(k, C.K_MAX))


def effective_symmetry(family: str, symmetry: str) -> str:
    if symmetry not in C.SYMMETRIES:
        raise ValueError(f"unbekannte Symmetrie {symmetry!r}")
    return symmetry if family in ("Perlenketten", "Brett s×s") else "Drehungen"


# ----------------------------------------------------------------------------- Spielpläne (zwischengespeichert: Aufzählen und Union-Find sind deterministisch)

@functools.cache
def schedule_data(nv: int) -> dict:
    """Alle Pläne, Bahngrößen und je Bahn |Aut| (direkt durch Durchprobieren aller Permutationen); die Rückgabe darf nicht verändert werden."""
    plans = A.one_factorizations(nv)
    sizes = A.plan_orbit_sizes(plans, nv)
    reps = A.plan_orbit_representatives(plans, nv)
    fact = math.factorial(nv)
    auts = sorted((A.automorphism_count(r, nv) for r in reps), reverse=True)
    return {"plans": len(plans), "sizes": sizes, "auts": auts, "orbits": len(sizes), "sum_aut": sum(fact // a for a in auts), "reps": reps, "n_fact": fact}


# ----------------------------------------------------------------------------- die eingestellte Aufgabe

def _way(group, name, value, text, reason=""):
    return {"Gruppe": group, "Weg": name, "Wert": value, "Text": text, "Grund": reason}


def _terms_for_group(group: list, k: int, labels) -> list:
    """Fixpunkte und Anteil an der Bahnenzahl je Gruppenelement (Anteil = Fixpunkte/|G|)."""
    return [(labels(i, g), k ** A.cycle_count(g), Fraction(k ** A.cycle_count(g), len(group))) for i, g in enumerate(group)]


def analyse(s: Settings) -> Analysis:
    n = effective_n(s.family, s.n)
    k = effective_k(s.k)
    sym = effective_symmetry(s.family, s.symmetry)
    notes, problems, ways = [], [], []
    if n != s.n:
        notes.append(f"Für diese Familie rechnet die App nur n von {C.N_MIN} bis {C.N_CAP[s.family]}" + (" und nur gerade Teamzahlen von 4 bis 8" if s.family == "Spielpläne eines Rundenturniers" else "") + f": gerechnet wird mit n = {n}.")
    if k != s.k:
        notes.append(f"Die Zahl der Farben liegt zwischen {C.K_MIN} und {C.K_MAX}: gerechnet wird mit k = {k}.")
    if s.family in ("Graphen", "Spielpläne eines Rundenturniers") and s.symmetry != "Drehungen":
        notes.append("Bei dieser Familie ist die Symmetrie fest (Umbenennen der Knoten beziehungsweise Teams); die Auswahl gilt nur für Perlenketten und Bretter.")
    extras = {}
    if s.family in ("Perlenketten", "Brett s×s"):
        if s.family == "Perlenketten":
            group = A.chain_group(n, sym)
            cells, formula = n, A.chain_formula(n, k, sym)
            label = lambda i, g: f"Element {i + 1}"
            extras["geometry"] = f"{n} Perlen im Kreis"
        else:
            group = A.square_group(n, sym)
            cells, formula = n * n, A.square_formula(n, k, sym)
            label = lambda i, g: f"Element {i + 1}"
            extras["geometry"] = f"{n}×{n} Felder"
        total = k ** cells
        order = len(group)
        if sym == "keine":
            ways.append(_way("Bahnenzahl", "Gesamtzahl (keine Symmetrie)", formula, big_text(formula)))
        else:
            ways.append(_way("Bahnenzahl", "Zyklenindex (geschlossene Formel)", formula, big_text(formula)))
        by_elements = A.burnside_count(group, k)
        ways.append(_way("Bahnenzahl", f"Burnside über alle {order} Gruppenelemente", by_elements, big_text(by_elements)))
        if total <= C.ENUM_LIMIT:
            enumerated = len(A.orbit_representatives(group, k, cells))
            ways.append(_way("Bahnenzahl", "Aufzählen der Bahnen (kleinste Form)", enumerated, big_text(enumerated)))
        else:
            ways.append(_way("Bahnenzahl", "Aufzählen der Bahnen (kleinste Form)", None, "", f"nur bis {big_text(C.ENUM_LIMIT)} Färbungen"))
        orbits = formula
        terms = _terms_for_group(group, k, label)
        extras["fixed_per_element"] = [t[1] for t in terms]
    elif s.family == "Graphen":
        total = 2 ** (n * (n - 1) // 2)
        order = math.factorial(n)
        polya = A.graphs_polya(n)
        ways.append(_way("Bahnenzahl", f"Pólya über {A.partition_count(n)} Zyklentypen", polya, big_text(polya)))
        if n <= C.GRAPH_ALL_ELEMENTS_MAX:
            v = A.graphs_by_all_elements(n)
            ways.append(_way("Bahnenzahl", f"Burnside über alle {big_text(order)} Permutationen", v, big_text(v)))
        else:
            ways.append(_way("Bahnenzahl", f"Burnside über alle {big_text(order)} Permutationen", None, "", f"nur bis n = {C.GRAPH_ALL_ELEMENTS_MAX}"))
        if n <= C.GRAPH_ENUM_MAX:
            v = len(A.graph_orbit_sizes(n))
            ways.append(_way("Bahnenzahl", "Aufzählen aller beschrifteten Graphen (Union-Find)", v, big_text(v)))
        else:
            ways.append(_way("Bahnenzahl", "Aufzählen aller beschrifteten Graphen (Union-Find)", None, "", f"nur bis n = {C.GRAPH_ENUM_MAX}"))
        orbits = polya
        types = A.graph_terms(n)
        shares = sorted(((lam, cnt, fix, Fraction(cnt * fix, order)) for lam, cnt, fix in types), key=lambda t: -t[3])
        terms = [("+".join(map(str, lam)), fix, share) for lam, cnt, fix, share in shares[: C.GRAPH_TOP_TYPES]]
        extras.update(geometry=f"{n} Knoten, {n * (n - 1) // 2} mögliche Kanten", types=len(types), elements=order)
    else:
        data = schedule_data(n)
        order = data["n_fact"]
        total = data["plans"]
        orbits = data["orbits"]
        ways.append(_way("Zahl der Pläne", "Rückverfolgung (alle 1-Faktorisierungen)", data["plans"], big_text(data["plans"])))
        ways.append(_way("Zahl der Pläne", "Summe über die Bahnen von n!/|Aut|", data["sum_aut"], big_text(data["sum_aut"])))
        ways.append(_way("Bahnenzahl", "Union-Find über zwei Erzeuger der Umbenennungen", data["orbits"], big_text(data["orbits"])))
        terms = [(f"|Aut| = {a}", Fraction(data["n_fact"], a), Fraction(1)) for a in data["auts"]]
        extras.update(geometry=f"{n} Teams, {n - 1} Runden", sizes=data["sizes"], auts=data["auts"])
    for group_name in dict.fromkeys(w["Gruppe"] for w in ways):
        done = [w for w in ways if w["Gruppe"] == group_name and w["Wert"] is not None]
        if any(w["Wert"] != done[0]["Wert"] for w in done):
            problems.append(f"{group_name}: " + ", ".join(w["Weg"] for w in done) + " weichen ab")
    approx = Fraction(total, order)
    return Analysis(s, n, k, sym, order, total, orbits, approx, ways, terms, problems, notes, extras)


def way_rows(a: Analysis) -> list[dict]:
    """Tabelle der Rechenwege: Frage, Weg, Ergebnis, Prüfung."""
    rows = []
    reference = {}
    for w in a.ways:
        if w["Wert"] is not None and w["Gruppe"] not in reference:
            reference[w["Gruppe"]] = w["Wert"]
    for w in a.ways:
        if w["Wert"] is None:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": "–", "Prüfung": w["Grund"]})
        else:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": w["Text"], "Prüfung": "gleich" if w["Wert"] == reference[w["Gruppe"]] else "weicht ab"})
    return rows


def approx_error(a: Analysis) -> float:
    """Näherung Gesamtzahl/|G| geteilt durch die exakte Bahnenzahl minus 1 (negativ: die Näherung liegt zu klein)."""
    return A.ratio_minus_one(a.approx, a.orbits)


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    s = a.settings
    checked = [w for w in a.ways if w["Wert"] is not None]
    agree = f"{len(checked)} Wege geben dieselbe Zahl" if len(checked) > 1 else "ein Weg"
    err = approx_error(a)
    near = (f" Die Näherung Gesamtzahl/|G| = {approx_text(a.approx)} liegt {percent_fine(abs(err))} {'daneben (zu klein)' if err < 0 else 'daneben (zu groß)'}; sie ist nur eine untere Schranke."
            if a.orbits != a.total else " Ohne Symmetrie ist jedes Objekt eine eigene Bahn.")
    if s.family == "Spielpläne eines Rundenturniers":
        return "success", (f"{a.n_eff} Teams: {big_text(a.total)} Spielpläne (Mengen von {a.n_eff - 1} Runden), bis auf Umbenennen der Teams {a.orbits} Bahnen mit |Aut| = {', '.join(map(str, a.extras['auts']))} (die Planzahl auf zwei Wegen gleich, die Bahnenzahl durch Union-Find).{near} "
                           f"Die Näherung ist hier nutzlos, weil jeder Plan Symmetrien hat.")
    if s.family == "Graphen":
        return "success", (f"{a.n_eff} Knoten: {big_text(a.orbits)} Graphen bis auf Umbenennen der Knoten, gerechnet in {a.extras['types']} Summanden statt über {big_text(a.extras['elements'])} Permutationen ({agree}). "
                           f"Beschriftet sind es {big_text(a.total)}.{near}")
    sym = {"keine": "ohne Symmetrie", "Drehungen": "bis auf Drehungen", "Drehungen und Spiegelungen": "bis auf Drehungen und Spiegelungen"}[a.symmetry_eff]
    return "success", (f"{a.extras['geometry']}, {a.k_eff} Farben: {big_text(a.total)} Färbungen, {big_text(a.orbits)} Bahnen {sym} (|G| = {a.group_order}; {agree}).{near}")


# ----------------------------------------------------------------------------- Experiment 1: dieselbe Zahl auf mehreren Wegen

@functools.cache
def ways_rows() -> list[dict]:
    rows = []
    for fam, n, k, sym in C.EXP_WAYS:
        a = analyse(Settings(fam, n, k, sym))
        values = [w for w in a.ways if w["Wert"] is not None]
        rows.append({"Familie": fam, "n": a.n_eff, "k": a.k_eff if fam in ("Perlenketten", "Brett s×s") else None, "Symmetrie": a.symmetry_eff, "Gesamtzahl": a.total, "Bahnen": a.orbits, "|G|": a.group_order,
                     "Wege": len(values), "gleich": not a.problems})
    return rows


def verdict_ways(rows: list[dict]):
    ok = all(r["gleich"] for r in rows)
    mn, mx = min(r["Wege"] for r in rows), max(r["Wege"] for r in rows)
    count = f"jede Aufgabe auf {mx} Wegen" if mn == mx else f"{mn} bis {mx} Wege je Aufgabe"
    return ("success" if ok else "error"), (f"In allen {len(rows)} Aufgaben geben die Rechenwege dieselbe Bahnenzahl ({count}; bei den Spielplänen zwei Wege für die Planzahl, einer für die Bahnenzahl): die Formel aus dem Zyklenindex, die Summe über alle Gruppenelemente und das Aufzählen der Bahnen.")


# ----------------------------------------------------------------------------- Experiment 2: die Näherung Gesamtzahl/|G|

@functools.cache
def approx_rows() -> dict:
    series = {}
    for k in C.EXP_APPROX_KS:
        series[k] = {n: A.ratio_minus_one(Fraction(k ** n, n), A.necklaces_formula(n, k)) for n in C.EXP_APPROX_NS}
    bracelets = {n: A.ratio_minus_one(Fraction(2 ** n, 2 * n), A.bracelets_formula(n, 2)) for n in C.EXP_APPROX_NS if n >= 3}
    graphs = {}
    for n in C.EXP_GRAPH_RATIO_NS:
        graphs[n] = Fraction(A.graphs_polya(n)) / (Fraction(2 ** (n * (n - 1) // 2), math.factorial(n)))
    table = [{"n": n, "exakt": A.necklaces_formula(n, 2), "Näherung": Fraction(2 ** n, n), "Fehler": series[2][n]} for n in C.EXP_APPROX_TABLE_NS]
    first1 = next(n for n in range(2, 200) if abs(A.ratio_minus_one(Fraction(2 ** n, n), A.necklaces_formula(n, 2))) < 0.01)
    first01 = next(n for n in range(2, 200) if abs(A.ratio_minus_one(Fraction(2 ** n, n), A.necklaces_formula(n, 2))) < 0.001)
    lower_bound = all(n * A.necklaces_formula(n, k) >= k ** n for n in range(1, 40) for k in (2, 3, 5))
    return {"series": series, "bracelets": bracelets, "graphs": graphs, "table": table, "first_below_1": first1, "first_below_01": first01, "lower_bound": lower_bound}


def verdict_approx(res: dict):
    s2 = res["series"][2]
    g = res["graphs"]
    return "warning", (f"Die Näherung Gesamtzahl/|G| ist nur eine untere Schranke ({'für alle geprüften n und k' if res['lower_bound'] else 'nicht immer'}): bei Halsketten mit 2 Farben liegt sie {percent(abs(s2[6]), 1)} daneben bei n = 6, {percent(abs(s2[20]), 2)} bei n = 20 und {percent_fine(abs(s2[30]), 4)} bei n = 30. "
                       f"Der Fehler fällt nicht gleichmäßig: n = 11 hat {percent(abs(s2[11]), 2)}, n = 12 aber {percent(abs(s2[12]), 2)}, weil n = 12 viele Teiler hat; unter 1 % liegt der Fehler erstmals bei n = {res['first_below_1']}, unter 0,1 % erstmals bei n = {res['first_below_01']} (beide nicht für alle größeren n). "
                       f"Bei den Graphen ist die exakte Zahl {de(float(g[10]), 3)}-mal so groß wie die Näherung bei n = 10, {de(float(g[15]), 3)}-mal bei n = 15 und {de(float(g[20]), 4)}-mal bei n = 20.")


# ----------------------------------------------------------------------------- Experiment 3: Pólya mit Gewicht

@functools.cache
def weight_rows() -> dict:
    n = C.EXP_WEIGHT_N
    chain = A.weight_distribution(A.cyclic_group(n))
    chain_brute = A.weight_distribution_brute(A.cyclic_group(n))
    equal = all(A.weight_distribution(A.cyclic_group(m)) == A.weight_distribution_brute(A.cyclic_group(m)) for m in C.EXP_WEIGHT_CHECK_NS)
    board_group = A.square_group(3, "Drehungen und Spiegelungen")
    board = A.weight_distribution(board_group)
    board_brute = A.weight_distribution_brute(board_group)
    return {"n": n, "chain": chain, "chain_brute": chain_brute, "chain_equal_all": equal, "board": board, "board_brute": board_brute, "chain_sum": sum(chain), "board_sum": sum(board)}


def verdict_weights(res: dict):
    ok = res["chain"] == res["chain_brute"] and res["board"] == res["board_brute"] and res["chain_equal_all"]
    return ("success" if ok else "error"), (f"Mit dem Gewicht (Zahl der Einsen) zählt derselbe Satz die Bahnen nach Gewicht: binäre Halsketten mit n = {res['n']} Perlen {', '.join(map(str, res['chain']))} (Summe {res['chain_sum']}), "
                                            f"das 3×3-Brett unter allen acht Symmetrien nach Zahl der schwarzen Felder {', '.join(map(str, res['board']))} (Summe {res['board_sum']}); beides gleich dem Aufzählen, die Halsketten für alle n von 1 bis 12.")


# ----------------------------------------------------------------------------- Experiment 4: Graphen über Zyklentypen

@functools.cache
def graph_rows() -> dict:
    rows = []
    for n in C.EXP_GRAPH_TABLE_NS:
        types = A.partition_count(n)
        orbits = A.graphs_polya(n)
        approx = Fraction(2 ** (n * (n - 1) // 2), math.factorial(n))
        rows.append({"n": n, "Permutationen": math.factorial(n), "Zyklentypen": types, "Graphen": orbits, "Verhältnis": float(Fraction(orbits) / approx)})
    mean_rows = []
    for n in C.EXP_MEAN_AUT_NS:
        sizes = A.graph_orbit_sizes(n)
        fact = math.factorial(n)
        mean_inv = sum(Fraction(sz, fact) for sz in sizes) / len(sizes)
        ratio = Fraction(2 ** (n * (n - 1) // 2), fact * len(sizes))
        mean_rows.append({"n": n, "Bahnen": len(sizes), "Pólya": A.graphs_polya(n), "Mittel 1/|Aut|": mean_inv, "beschriftet/(n!·Bahnen)": ratio, "gleich": mean_inv == ratio})
    euler = A.rooted_trees_euler(C.EXP_TREES_N)
    polya = A.rooted_trees_polya(C.EXP_TREES_N)
    return {"rows": rows, "mean": mean_rows, "euler": euler, "polya": polya}


def verdict_graphs(res: dict):
    last = res["rows"][-1]
    ok = all(r["gleich"] for r in res["mean"]) and res["euler"] == res["polya"] and all(r["Bahnen"] == r["Pólya"] for r in res["mean"])
    fr = ", ".join(fraction_text(r["Mittel 1/|Aut|"]) for r in res["mean"][2:])
    return ("success" if ok else "error"), (f"Bei Graphen rechnet Pólya über Zyklentypen: n = {last['n']} hat {big_text(last['Permutationen'])} Permutationen, aber nur {big_text(last['Zyklentypen'])} Typen. Beschriftet geteilt durch n! mal unbeschriftet ist genau das Mittel von 1/|Aut| "
                                            f"(exakt in Brüchen, n = 2 bis {res['mean'][-1]['n']}; n = 4 bis {res['mean'][-1]['n']}: {fr}); die Zahl der Bahnen aus dem Aufzählen aller beschrifteten Graphen gleicht der Pólya-Summe. "
                                            f"Die Wurzelbäume ohne Reihenfolge aus Stück 5 ({', '.join(map(str, res['euler'][1:10]))}, …) kommen über den Zyklenindex der symmetrischen Gruppen heraus: Euler-Transformation und Pólya sind gleich bis n = {C.EXP_TREES_N}.")


# ----------------------------------------------------------------------------- Experiment 5: Spielpläne

@functools.cache
def schedule_rows() -> list[dict]:
    rows = []
    for nv in C.SCHEDULE_SIZES:
        d = schedule_data(nv)
        rows.append({"Teams": nv, "Runden": nv - 1, "Pläne": d["plans"], "Bahnen": d["orbits"], "Bahngrößen": d["sizes"], "|Aut|": d["auts"], "Σ n!/|Aut|": d["sum_aut"], "n!": d["n_fact"],
                     "Gesamtzahl/n!": Fraction(d["plans"], d["n_fact"]), "mit Reihenfolge der Runden": d["plans"] * math.factorial(nv - 1)})
    return rows


def verdict_schedules(rows: list[dict]):
    r8 = rows[-1]
    ok = all(r["Σ n!/|Aut|"] == r["Pläne"] for r in rows)
    return ("success" if ok else "error"), (f"Spielpläne eines Rundenturniers sind die 1-Faktorisierungen von Kₙ: {', '.join(str(r['Pläne']) for r in rows)} Pläne für {', '.join(str(r['Teams']) for r in rows)} Teams, bis auf Umbenennen der Teams "
                                            f"{', '.join(str(r['Bahnen']) for r in rows)} Bahnen. Für {r8['Teams']} Teams haben die Bahnen |Aut| = {', '.join(map(str, r8['|Aut|']))}; die Summe über n!/|Aut| ergibt wieder {big_text(r8['Σ n!/|Aut|'])}. "
                                            f"Die Näherung Gesamtzahl/n! = {de(float(r8['Gesamtzahl/n!']), 3)} ist eine gültige, aber nutzlose untere Schranke, weil jeder Plan Symmetrien hat. Mit geordneten Runden sind es {big_text(r8['mit Reihenfolge der Runden'])} Pläne.")


# ----------------------------------------------------------------------------- Spielwiese: Brett mit Vertretern

def play_board(size: int, k: int, symmetry: str) -> dict:
    size = max(C.PLAY_SIDE_MIN, min(size, C.PLAY_SIDE_MAX))
    k = max(C.PLAY_K_MIN, min(k, C.PLAY_K_MAX))
    if symmetry not in C.SYMMETRIES:
        raise ValueError(f"unbekannte Symmetrie {symmetry!r}")
    cells = size * size
    group = A.square_group(size, symmetry)
    formula = A.square_formula(size, k, symmetry)
    res = {"size": size, "k": k, "symmetry": symmetry, "cells": cells, "total": k ** cells, "order": len(group), "orbits": formula}
    if k ** cells <= C.ENUM_LIMIT:
        reps = A.orbit_representatives(group, k, cells)
        res["enumerated"] = len(reps)
        res["reps"] = [rep for rep in reps[: C.SHOW_REPRESENTATIVES]]
        res["boards"] = [["".join(str(v) for v in rep[r * size:(r + 1) * size]) for r in range(size)] for rep in res["reps"]]
    else:
        res["enumerated"] = None
        res["reps"] = []
        res["boards"] = []
    return res


def verdict_play(res: dict):
    sym = {"keine": "ohne Symmetrie", "Drehungen": "bis auf Drehungen", "Drehungen und Spiegelungen": "bis auf Drehungen und Spiegelungen"}[res["symmetry"]]
    text = f"{res['size']}×{res['size']}-Brett mit {res['k']} Farben: {big_text(res['total'])} Färbungen, {big_text(res['orbits'])} Bahnen {sym} (|G| = {res['order']})"
    if res["enumerated"] is None:
        return "info", text + f"; das Aufzählen der Bahnen entfällt (mehr als {big_text(C.ENUM_LIMIT)} Färbungen), die Zahl kommt aus dem Zyklenindex."
    if res["enumerated"] != res["orbits"]:
        return "error", text + f"; das Aufzählen ergibt {res['enumerated']}: die Rechenwege widersprechen sich."
    return "success", text + "; das Aufzählen der Bahnen ergibt dieselbe Zahl. Gezeigt werden die kleinsten Vertreter der ersten Bahnen."
