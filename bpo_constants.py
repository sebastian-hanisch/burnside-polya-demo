"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

FAMILIES = ("Perlenketten", "Brett s×s", "Graphen", "Spielpläne eines Rundenturniers")
DEFAULT_FAMILY = "Perlenketten"
SYMMETRIES = ("keine", "Drehungen", "Drehungen und Spiegelungen")
DEFAULT_SYMMETRY = "Drehungen"
N_MIN, N_MAX, DEFAULT_N = 1, 60, 6
N_CAP = {"Perlenketten": 60, "Brett s×s": 8, "Graphen": 30, "Spielpläne eines Rundenturniers": 8}   # größtes n je Familie
K_MIN, K_MAX, DEFAULT_K = 1, 10, 2
SCHEDULE_SIZES = (4, 6, 8)      # Zahl der Teams, für die die App alle Spielpläne aufzählt (gerade, mindestens 4)

ENUM_LIMIT = 300_000            # bis zu k^Positionen Färbungen wird die Bahnenzahl durch Aufzählen geprüft
GRAPH_ALL_ELEMENTS_MAX = 8      # Burnside über alle n! Permutationen der Knoten bis hierher
GRAPH_ENUM_MAX = 6              # Aufzählen aller beschrifteten Graphen (Union-Find) bis hierher
GRAPH_TOP_TYPES = 12            # so viele Zyklentypen zeigt das Diagramm
SHOW_REPRESENTATIVES = 6

EXP_WAYS = (("Perlenketten", 6, 2, "Drehungen"), ("Perlenketten", 6, 2, "Drehungen und Spiegelungen"), ("Perlenketten", 8, 3, "Drehungen"), ("Brett s×s", 3, 2, "Drehungen und Spiegelungen"),
            ("Brett s×s", 3, 3, "Drehungen"), ("Graphen", 5, 2, "Drehungen"), ("Graphen", 6, 2, "Drehungen"), ("Spielpläne eines Rundenturniers", 6, 2, "Drehungen"))
EXP_APPROX_KS = (2, 3, 10)
EXP_APPROX_NS = tuple(range(2, 41))
EXP_APPROX_TABLE_NS = (3, 5, 6, 7, 8, 10, 11, 12, 13, 16, 20, 24, 30)
EXP_GRAPH_RATIO_NS = tuple(range(2, 31))
EXP_WEIGHT_N = 8
EXP_WEIGHT_CHECK_NS = tuple(range(1, 13))
EXP_GRAPH_TABLE_NS = (5, 8, 10, 15, 20, 30)
EXP_MEAN_AUT_NS = (2, 3, 4, 5, 6)
EXP_TREES_N = 12
PLAY_SIDE_MIN, PLAY_SIDE_MAX = 1, 4
PLAY_K_MIN, PLAY_K_MAX = 2, 3

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Halsketten, n = 6, 2 Farben": {"family": "Perlenketten", "n": 6, "k": 2, "symmetry": "Drehungen"},
    "Armbänder: mit Spiegelungen, n = 6": {"family": "Perlenketten", "n": 6, "k": 2, "symmetry": "Drehungen und Spiegelungen"},
    "Brett 3×3 mit Drehungen und Spiegelungen": {"family": "Brett s×s", "n": 3, "k": 2, "symmetry": "Drehungen und Spiegelungen"},
    "Graphen auf 10 Knoten": {"family": "Graphen", "n": 10, "k": 2, "symmetry": "Drehungen"},
    "Spielpläne mit 8 Teams": {"family": "Spielpläne eines Rundenturniers", "n": 8, "k": 2, "symmetry": "Drehungen"},
    "Halsketten n = 12 (viele Teiler)": {"family": "Perlenketten", "n": 12, "k": 2, "symmetry": "Drehungen"},
}
PRESET_HELP = {
    "Standardfall: Halsketten, n = 6, 2 Farben": "Von 64 Ketten bleiben 14 Halsketten: Burnside rechnet (64 + 2 + 4 + 8 + 4 + 2)/6 = 14, das Mittel der Fixpunkte der sechs Drehungen.",
    "Armbänder: mit Spiegelungen, n = 6": "Mit den sechs Spiegelungen dazu sind es 13 Armbänder: (84 + 3·16 + 3·8)/12.",
    "Brett 3×3 mit Drehungen und Spiegelungen": "512 Färbungen eines 3×3-Bretts bleiben 102 Bahnen unter den acht Symmetrien des Quadrats (nur mit Drehungen: 140); die Näherung 512/8 = 64 liegt 37 % daneben.",
    "Graphen auf 10 Knoten": "12.005.168 Graphen auf 10 Knoten bis auf Umbenennen, gerechnet in 42 Summanden statt über 3.628.800 Permutationen; die Näherung 2^45/10! ist 19 % zu klein.",
    "Spielpläne mit 8 Teams": "6.240 Spielpläne (1-Faktorisierungen von K₈) bleiben 6 Bahnen unter Umbenennen der Teams; die Näherung 6.240/8! = 0,155 ist eine gültige, aber nutzlose untere Schranke.",
    "Halsketten n = 12 (viele Teiler)": "Bei n = 12 weicht die Näherung 2¹²/12 um 3,0 % ab, bei n = 11 nur um 0,97 % und bei n = 13 um 0,29 %: der Fehler hängt von den Teilern von n ab.",
}
