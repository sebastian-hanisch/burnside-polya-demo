"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_necklaces():
    """Halsketten n = 4, k = 2: Fixpunkte der Drehungen um 0 bis 3: 2^4, 2^1, 2^2, 2^1 = 16, 2, 4, 2; Summe 24; 24/4 = 6 (0000, 0001, 0011, 0101, 0111, 1111).
    n = 6, k = 2: 64, 2, 4, 8, 4, 2; 84/6 = 14. Armbänder n = 6: Spiegelungen drei mit 2^4 = 16 und drei mit 2^3 = 8: (84 + 48 + 24)/12 = 13."""
    return {"fix4": [16, 2, 4, 2], "n4": 6, "classes4": [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 1), (1, 1, 1, 1)],
            "fix6": [64, 2, 4, 8, 4, 2], "n6": 14, "bracelets6": 13}


@pytest.fixture
def hand_graphs_3():
    """Graphen n = 3: Zyklentypen (1,1,1), (2,1), (3) mit z = 6, 2, 3 und 3, 2, 1 Zyklen auf den drei Paaren: 2³/6 + 2²/2 + 2¹/3 = 4/3 + 2 + 2/3 = 4.
    Beschriftet 8; Aut der vier Bahnen (leer, Kante, Pfad, Dreieck): 6, 2, 2, 6; Mittel von 1/|Aut| = 1/3 = 8/(3!·4)."""
    return {"types": {(1, 1, 1): (6, 3), (2, 1): (2, 2), (3,): (3, 1)}, "orbits": 4, "labelled": 8, "mean_inv_aut": Fraction(1, 3)}


@pytest.fixture
def hand_board_2():
    """Brett 2×2, 2 Farben: Drehungen um 0°, 90°, 180°, 270° haben 4, 1, 2, 1 Zyklen: (16 + 2 + 4 + 2)/4 = 6; dazu zwei Achsenspiegelungen (je 2 Zyklen: 2² = 4) und zwei Diagonalspiegelungen (je 3 Zyklen: 2³ = 8): 24; (24 + 24)/8 = 6."""
    return {"rot": 6, "d4": 6, "cycles": [4, 1, 2, 1]}


@pytest.fixture
def hand_plans():
    """K4 hat drei perfekte Paarungen und genau einen Spielplan (alle drei Runden); |Aut| = 24. K6: 6 Pläne in einer Bahn, |Aut| = 720/6 = 120."""
    return {"k4": 1, "k6": 6, "k6_aut": 120, "k4_aut": 24}
