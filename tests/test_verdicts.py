"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für alle Voreinstellungen und Experimente, damit jede Zahl darin geprüft ist."""

import bpo_constants as C
import bpo_evaluation as ev

S = ev.Settings


def answer(name):
    return ev.verdict_answers(ev.analyse(S(**C.PRESETS[name])))


def test_answer_necklaces_exact():
    kind, text = answer("Standardfall: Halsketten, n = 6, 2 Farben")
    assert kind == "success"
    assert text == "6 Perlen im Kreis, 2 Farben: 64 Färbungen, 14 Bahnen bis auf Drehungen (|G| = 6; 3 Wege geben dieselbe Zahl). Die Näherung Gesamtzahl/|G| = 10,67 liegt 23,81 % daneben (zu klein); sie ist nur eine untere Schranke."


def test_answer_bracelets_board_and_twelve_exact():
    assert answer("Armbänder: mit Spiegelungen, n = 6")[1] == ("6 Perlen im Kreis, 2 Farben: 64 Färbungen, 13 Bahnen bis auf Drehungen und Spiegelungen (|G| = 12; 3 Wege geben dieselbe Zahl). "
                                                                "Die Näherung Gesamtzahl/|G| = 5,33 liegt 58,97 % daneben (zu klein); sie ist nur eine untere Schranke.")
    assert answer("Brett 3×3 mit Drehungen und Spiegelungen")[1] == ("3×3 Felder, 2 Farben: 512 Färbungen, 102 Bahnen bis auf Drehungen und Spiegelungen (|G| = 8; 3 Wege geben dieselbe Zahl). "
                                                                     "Die Näherung Gesamtzahl/|G| = 64 liegt 37,25 % daneben (zu klein); sie ist nur eine untere Schranke.")
    assert answer("Halsketten n = 12 (viele Teiler)")[1] == ("12 Perlen im Kreis, 2 Farben: 4.096 Färbungen, 352 Bahnen bis auf Drehungen (|G| = 12; 3 Wege geben dieselbe Zahl). "
                                                             "Die Näherung Gesamtzahl/|G| = 341,33 liegt 3,03 % daneben (zu klein); sie ist nur eine untere Schranke.")


def test_answer_graphs_exact():
    kind, text = answer("Graphen auf 10 Knoten")
    assert kind == "success"
    assert text == ("10 Knoten: 12.005.168 Graphen bis auf Umbenennen der Knoten, gerechnet in 42 Summanden statt über 3.628.800 Permutationen (ein Weg). Beschriftet sind es 3,51·10¹³ (14 Stellen). "
                    "Die Näherung Gesamtzahl/|G| = 9,70·10⁶ liegt 19,24 % daneben (zu klein); sie ist nur eine untere Schranke.")


def test_answer_schedules_exact():
    kind, text = answer("Spielpläne mit 8 Teams")
    assert kind == "success"
    assert text == ("8 Teams: 6.240 Spielpläne (Mengen von 7 Runden), bis auf Umbenennen der Teams 6 Bahnen mit |Aut| = 1344, 96, 64, 42, 24, 16 (3 Wege geben dieselbe Zahl). "
                    "Die Näherung Gesamtzahl/|G| = 0,155 liegt 97,42 % daneben (zu klein); sie ist nur eine untere Schranke. Die Näherung ist hier nutzlos, weil jeder Plan Symmetrien hat.")


def test_answer_error_when_the_ways_disagree():
    a = ev.analyse(S(**C.PRESETS["Standardfall: Halsketten, n = 6, 2 Farben"]))
    a.problems.append("zwei Wege weichen ab")
    assert ev.verdict_answers(a) == ("error", "Die Rechenwege widersprechen sich: zwei Wege weichen ab")


def test_way_rows_of_the_standard_case():
    rows = ev.way_rows(ev.analyse(S(**C.PRESETS["Standardfall: Halsketten, n = 6, 2 Farben"])))
    assert [(r["Weg"], r["Ergebnis"], r["Prüfung"]) for r in rows] == [("Zyklenindex (geschlossene Formel)", "14", "gleich"), ("Burnside über alle 6 Gruppenelemente", "14", "gleich"), ("Aufzählen der Bahnen (kleinste Form)", "14", "gleich")]


def test_ways_verdict_exact():
    assert ev.verdict_ways(ev.ways_rows()) == ("success", "In allen 8 Aufgaben geben die Rechenwege dieselbe Bahnenzahl (2 bis 3 Wege je Aufgabe): die Formel aus dem Zyklenindex, die Summe über alle Gruppenelemente und das Aufzählen der Bahnen.")


def test_approx_verdict_exact():
    kind, text = ev.verdict_approx(ev.approx_rows())
    assert kind == "warning"
    assert text == ("Die Näherung Gesamtzahl/|G| ist nur eine untere Schranke (für alle geprüften n und k): bei Halsketten mit 2 Farben liegt sie 23,8 % daneben bei n = 6, 0,11 % bei n = 20 und 0,0033 % bei n = 30. "
                    "Der Fehler fällt nicht gleichmäßig: n = 11 hat 0,97 %, n = 12 aber 3,03 %, weil n = 12 viele Teiler hat; unter 1 % liegt der Fehler erst ab n = 11 (nicht für alle größeren n), unter 0,1 % ab n = 17. "
                    "Bei den Graphen ist die exakte Zahl 1,238-mal so groß wie die Näherung bei n = 10, 1,013-mal bei n = 15 und 1,0007-mal bei n = 20.")


def test_weights_verdict_exact():
    kind, text = ev.verdict_weights(ev.weight_rows())
    assert kind == "success"
    assert text == ("Mit dem Gewicht (Zahl der Einsen) zählt derselbe Satz die Bahnen nach Gewicht: binäre Halsketten mit n = 8 Perlen 1, 1, 4, 7, 10, 7, 4, 1, 1 (Summe 36), "
                    "das 3×3-Brett unter allen acht Symmetrien nach Zahl der schwarzen Felder 1, 3, 8, 16, 23, 23, 16, 8, 3, 1 (Summe 102); beides gleich dem Aufzählen, die Halsketten für alle n von 1 bis 12.")


def test_graphs_verdict_exact():
    kind, text = ev.verdict_graphs(ev.graph_rows())
    assert kind == "success"
    assert text == ("Bei Graphen rechnet Pólya über Zyklentypen: n = 30 hat 2,65·10³² (33 Stellen) Permutationen, aber nur 5.604 Typen. Beschriftet geteilt durch n! mal unbeschriftet ist genau das Mittel von 1/|Aut| "
                    "(exakt in Brüchen, n = 2 bis 6; n = 4 bis 6: 8/33, 64/255, 512/1755); die Zahl der Bahnen aus dem Aufzählen aller beschrifteten Graphen gleicht der Pólya-Summe. "
                    "Die Wurzelbäume ohne Reihenfolge aus Stück 5 (1, 1, 2, 4, 9, 20, 48, 115, 286, …) kommen über den Zyklenindex der symmetrischen Gruppen heraus: Euler-Transformation und Pólya sind gleich bis n = 12.")


def test_schedules_verdict_exact():
    kind, text = ev.verdict_schedules(ev.schedule_rows())
    assert kind == "success"
    assert text == ("Spielpläne eines Rundenturniers sind die 1-Faktorisierungen von Kₙ: 1, 6, 6240 Pläne für 4, 6, 8 Teams, bis auf Umbenennen der Teams 1, 1, 6 Bahnen. Für 8 Teams haben die Bahnen |Aut| = 1344, 96, 64, 42, 24, 16; "
                    "die Summe über n!/|Aut| ergibt wieder 6.240. Die Näherung Gesamtzahl/n! = 0,155 ist eine gültige, aber nutzlose untere Schranke, weil jeder Plan Symmetrien hat. Mit geordneten Runden sind es 31.449.600 Pläne.")


def test_play_verdicts_exact():
    kind, text = ev.verdict_play(ev.play_board(3, 2, "Drehungen und Spiegelungen"))
    assert kind == "success"
    assert text == ("3×3-Brett mit 2 Farben: 512 Färbungen, 102 Bahnen bis auf Drehungen und Spiegelungen (|G| = 8); das Aufzählen der Bahnen ergibt dieselbe Zahl. "
                    "Gezeigt werden die kleinsten Vertreter der ersten Bahnen.")
    kind, text = ev.verdict_play(ev.play_board(4, 3, "Drehungen"))
    assert kind == "info" and "das Aufzählen der Bahnen entfällt (mehr als 300.000 Färbungen)" in text
