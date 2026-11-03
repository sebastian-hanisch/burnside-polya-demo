# Zählen bis auf Symmetrie – Burnside und Pólya – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-burnside-polya-demo.streamlit.app/)** -->

Stück 11 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7), `zaehlen-nach-parameter-demo` (Stück 8), `asymptotik-demo` (Stück 9) und `gleichverteilt-ziehen-demo` (Stück 10); sie haben Objekte gezählt, **als wären alle verschieden**. Diese Demo zählt **bis auf Symmetrie**: eine Kette, die man dreht, ein Brett, das man wendet, ein Graph, dessen Knoten man umbenennt, ein Spielplan, in dem man die Teams umbenennt. Die Antwort ist die Zahl der **Bahnen** einer Gruppe G auf der Menge X der Objekte. **Burnside:** sie ist das **Mittel der Fixpunkte** über alle Gruppenelemente. **Pólya:** bei Färbungen ist die Fixpunktzahl k^(Zahl der Zyklen), das ist der **Zyklenindex**, und mit einem Gewicht statt k zählt derselbe Satz die Bahnen nach Gewicht. Die einfache Näherung **Gesamtzahl/|G|** ist nur eine untere Schranke und trifft erst für große n.

## Warum dieses Problem

Wer Lösungen eines Planungsproblems zählt, zählt oft zu viel: Zwei Spielpläne, die sich nur durch Umbenennen der Teams unterscheiden, sind für den Veranstalter derselbe Plan; wer sie getrennt zählt, überschätzt den Suchraum höchstens um den Faktor der Symmetriegruppe, und wer einfach durch |G| teilt, unterschätzt ihn, sobald Objekte selbst Symmetrien haben. Die Demo zeigt die Rechnung (Burnside über die Gruppe, Pólya über den Zyklenindex), ihre Gegenproben (Aufzählen der Bahnen) und die Grenze der Faustformel.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt und genauer:** Die Näherung Gesamtzahl/|G| trifft bei Halsketten und Graphen erst für große n, und der Fehler ist **nicht monoton**: bei Halsketten mit 2 Farben liegt er bei n = 11 bei 0,97 %, bei n = 12 aber bei 3,03 % und bei n = 13 bei 0,29 %, weil der zweite Summand der Formel von den Teilern von n abhängt. Erstmals unter 1 % liegt er bei n = 11 und erstmals unter 0,1 % bei n = 17; dauerhaft darunter bleibt er erst ab n = 13 beziehungsweise n = 21.
- **Korrektur einer Prozentangabe im Plan:** S2 nannte für die Graphen auf 10 Knoten „Näherung 24 % daneben“. Das ist das Verhältnis **exakt zur Näherung** (1,238): die exakte Zahl ist 24 % größer. Bezogen auf die exakte Zahl liegt die **Näherung 19,2 % zu klein**. Die App und die Texte zeigen den zweiten Wert (Näherung geteilt durch exakt minus 1), das Verhältnis steht in der Tabelle.
- **Vier statt fünf Familien:** Halsketten und Armbänder sind eine Familie „Perlenketten“ mit der Auswahl der Symmetrie (keine, Drehungen, Drehungen und Spiegelungen); dazu Brett s×s, Graphen und Spielpläne. Die Presets nennen weiter Halsketten und Armbänder.
- **Graphen durch Aufzählen nur bis n = 6:** Das Aufzählen aller beschrifteten Graphen für n = 7 braucht in Python etwa 12 Sekunden; die App rechnet die Bahnen dort nur über Pólya und über alle 5.040 Permutationen. Bis n = 6 gibt es drei Wege, bei n = 7 und 8 zwei, ab n = 9 einen.
- **Erklärung aus Stück 6 jetzt exakt:** Beschriftet geteilt durch (n! mal Bahnen) ist **genau** das Mittel von 1/|Aut|, in Brüchen bestätigt (n = 2 bis 6); in Stück 6 war es als Messung („fällt mit n“) und Deutung vermerkt.
- **Spielpläne:** Die Zahl der Pläne und die Bahnen für 4, 6 und 8 Teams sind gerechnet; die Automorphismen werden **direkt** gezählt (alle 40.320 Permutationen je Bahn), nicht aus der Bahngröße abgeleitet, damit die Summe über n!/|Aut| eine echte Gegenprobe ist. Die Zahlen für 10 und 12 Teams stehen nur in der Literatur.
- **Eigene Fehler im Bau (nicht in der Messung):** (1) In der Burnside-Summe über alle Permutationen hatte ich für n = 1 (keine Knotenpaare) 2 statt 1 Fixpunkt gesetzt (eine tote Fallunterscheidung); der Test gegen die Pólya-Summe für n = 0 und 1 hätte es gefunden, ich habe es beim Lesen bemerkt. (2) Die Prozentausgabe zeigte bei winzigen Fehlern „−0,00 %“; sie schaltet jetzt auf die Zehnerpotenz, wenn die Rundung 0 ergäbe. (3) Ein senkrechter Strich in „Gesamtzahl/|G|“ sprengte eine Markdown-Tabellenzeile. (4) Tabellenspalten mit Zahlen und „–“ erzeugten Arrow-Warnungen: jetzt Text.
- **Präfix `bpo_`, Port 9324** wie geplant.

## Modell

Eine **Gruppe** ist eine Menge von Permutationen der Positionen (Tupel, `p[i]` = Bild von i): `cyclic_group` (Drehungen einer Kette), `dihedral_group` (mit Spiegelungen), `square_group` (Drehungen und Spiegelungen des Quadrats, aus Erzeugern durch Abschluss), `generate_group` für beliebige Erzeuger. **Burnside** (`burnside_count`) zählt je Element k^(Zahl der Zyklen) und teilt die Summe durch |G|; die **Zyklen** der Elemente kommen aus den Permutationen, die **Formeln** aus dem Zyklenindex (`necklaces_formula`: (1/n) Σ φ(d)·k^(n/d); `bracelets_formula`; `square_formula` aus den Zyklenzahlen der Quadratsymmetrien) als zweiter Weg. **Aufzählen** (`orbit_representatives`) nimmt je Bahn die kleinste Form. **Pólya mit Gewicht** (`weight_distribution`) ersetzt in jedem Zyklus x_ℓ durch 1 + y^ℓ. **Graphen** (`graphs_polya`) summieren über die Zyklentypen λ: 2^c(λ)/z_λ mit c(λ) = Σ ⌊l/2⌋ + Σ ggT(l_i, l_j) Zyklen auf den Knotenpaaren; `graph_orbit_sizes` zählt die Bahnen aller beschrifteten Graphen mit Union-Find. **Spielpläne** (`one_factorizations`) sind alle 1-Faktorisierungen von K_n durch Rückverfolgung, `plan_orbit_sizes` die Bahnen unter Umbenennen der Teams, `automorphism_count` die Symmetrien eines Plans. **Wurzelbäume** über Pólya (`rooted_trees_polya`) gegen die Euler-Transformation (`rooted_trees_euler`, Stück 5).

## Methodik

- **Rechenwege in der App:** Perlenketten und Bretter: geschlossene Formel, Burnside über alle Gruppenelemente, Aufzählen der Bahnen (bis 300.000 Färbungen); Graphen: Pólya über Zyklentypen, Burnside über alle n! Permutationen (n ≤ 8), Aufzählen aller beschrifteten Graphen (n ≤ 6); Spielpläne: Rückverfolgung, Summe über n!/|Aut|, Union-Find. Bei Abweichung zeigt die App einen Fehler.
- **Eingabe:** Familie, Größe n (Perlenketten bis 60, Bretter bis 8×8, Graphen bis 30, Spielpläne mit 4, 6 oder 8 Teams; ungerade Teamzahlen werden aufgerundet und das gesagt), Zahl der Farben (1 bis 10), Symmetrie (nur Perlenketten und Bretter). Die Adresszeile spiegelt die Einstellung.
- **Fünf Experimente:** (1) dieselbe Zahl auf mehreren Wegen, (2) die Näherung Gesamtzahl/|G|, (3) Pólya mit Gewicht, (4) Graphen über Zyklentypen mit Mittel von 1/|Aut| und Wurzelbäumen, (5) Spielpläne. Dazu eine Spielwiese: ein s×s-Brett (s ≤ 4, 2 oder 3 Farben) mit den kleinsten Vertretern der ersten Bahnen. Alles ist deterministisch (keine Zufallszahlen).

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_bpo.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handinstanzen | Halsketten n = 4, k = 2: Fixpunkte der vier Drehungen 16, 2, 4, 2, Summe 24, **6** Bahnen (0000, 0001, 0011, 0101, 0111, 1111); n = 6: 64, 2, 4, 8, 4, 2, Summe 84, **14** Halsketten, **13** Armbänder; Brett 2×2: 6 (Drehungen) und 6 (mit Spiegelungen); Graphen n = 3: 2³/6 + 2²/2 + 2¹/3 = **4**, Mittel von 1/\|Aut\| = 1/3; K₄: 1 Spielplan mit \|Aut\| = 24, K₆: 6 Pläne in einer Bahn mit \|Aut\| = 120 |
| Standardfall | 64 Färbungen, 14 Bahnen, Näherung 64/6 = 10,67, 23,81 % zu klein; als Armbänder 13 Bahnen und Näherung 5,33 (58,97 % zu klein) |
| Halsketten und Armbänder, Formel gegen Aufzählen | alle (n, k) mit k ≤ 4 und n ≤ 8 sowie k = 2 mit n ≤ 14 gleich; k = 2, n = 1 bis 14: 2, 3, 4, 6, 8, 14, 20, 36, 60, 108, 188, 352, 632, 1.182 (Halsketten) und 2, 3, 4, 6, 8, 13, 18, 30, 46, 78, 126, 224, 380, 687 (Armbänder); k = 3, n = 1 bis 10 Halsketten: 3, 6, 11, 24, 51, 130, 315, 834, 2.195, 5.934 |
| Brett | 2×2: 6 und 6; 3×3: 512 Färbungen, **140** unter Drehungen, **102** mit Spiegelungen (Näherung 512/8 = 64, 37,25 % zu klein); 4×4: 16.456 und 8.548 |
| Näherung k^n/n gegen exakt, Halsketten k = 2, Fehler (Näherung/exakt − 1) | n = 3: −33,3 %; 5: −20,0 %; 6: −23,8 %; 7: −8,6 %; 8: −11,1 %; 10: −5,2 %; 11: −0,97 %; 12: −3,03 %; 13: −0,29 %; 16: −0,49 %; 20: −0,113 %; 24: −0,029 %; 30: −0,0033 % |
| Näherung bei anderen Farbzahlen | k = 3: n = 4: −15,6 %, n = 8: −1,66 %, n = 12: −0,18 %; k = 10: n = 4: −1,19 %, n = 8: −0,010 %, n = 12: −0,0001 % |
| Näherung k^n/(2n), Armbänder k = 2 | n = 6: −59,0 %; 8: −46,7 %; 10: −34,4 %; 12: −23,8 %; 16: −9,0 %; 20: −2,95 %; 30: −0,14 % |
| Untere Schranke | n·Bahnen ≥ k^n für alle n < 40 und k = 2, 3, 5 (ganzzahlig); Gleichheit bei k = 2 nur für n = 1 |
| Pólya mit Gewicht | binäre Halsketten n = 8 nach Zahl der Einsen: 1, 1, 4, 7, 10, 7, 4, 1, 1 (Summe 36); 3×3-Brett mit allen acht Symmetrien nach Zahl der schwarzen Felder: 1, 3, 8, 16, 23, 23, 16, 8, 3, 1 (Summe 102); beides gleich dem Aufzählen, die Halsketten für n = 1 bis 12 |
| Graphen auf n Knoten bis auf Umbenennen | n = 1 bis 10: 1, 2, 4, 11, 34, 156, 1.044, 12.346, 274.668, 12.005.168 (gleich der Folge aus dem Gedächtnis und der Summe über alle Permutationen bis n = 7 und dem Aufzählen bis n = 6); Zyklentypen n = 5, 8, 10, 15, 20, 30: 7, 22, 42, 176, 627, 5.604 gegen 120, 40.320, 3.628.800, 1,3·10¹², 2,4·10¹⁸, 2,7·10³² Permutationen |
| Graphen: exakt / (2^C(n,2)/n!) | n = 2 bis 10: 2,000, 3,000, 4,125, 3,984, 3,428, 2,509, 1,854, 1,450, 1,238; n = 12: 1,0717, 15: 1,0131, 20: 1,0007, 30: 1,000002 |
| Beschriftet gegen unbeschriftet | Mittel von 1/\|Aut\| = 2^C(n,2)/(n!·Bahnen), exakt in Brüchen: n = 2 bis 6: 1/2, 1/3, 8/33, 64/255, 512/1755 |
| Wurzelbäume ohne Reihenfolge | Pólya über den Zyklenindex der symmetrischen Gruppen gleich der Euler-Transformation: 1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1.842, 4.766 (n = 1 bis 12) |
| Spielpläne (1-Faktorisierungen von K_n) | n = 4, 6, 8: 1, 6, 6.240 Pläne; 1, 1, 6 Bahnen; für n = 8 Bahngrößen 30, 420, 630, 960, 1.680, 2.520 und \|Aut\| = 1.344, 96, 64, 42, 24, 16; Σ 8!/\|Aut\| = 6.240; Gesamtzahl/n! = 0,0417, 0,0083, 0,155 (n = 8: untere Schranke 0,155 gegen 6 Bahnen); mit geordneten Runden 6, 720, 31.449.600 |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Die Folge der Graphen (A000088) und die Zahlen von Dinitz u. a. (K₁₀: 396, K₁₂: 526.915.620 Bahnen) wurden nicht an einer Quelle gelesen. Die Graphen-Folge steht bis n = 7 auf zwei Wegen (Summe über alle Permutationen, Aufzählen bis n = 6); die Dinitz-Zahlen kommen nur im Text vor und werden nicht gerechnet oder getestet.
- **Nur diese Gruppen:** zyklisch, dihedral, die Symmetrien des Quadrats und die symmetrische Gruppe (Graphen, Spielpläne); weitere Symmetrien (Tausch von Heim und Auswärts, Zeitspiegelung bei Turnierplänen, Tausch der Farben) ändern die Zahlen und werden nicht gezählt.
- **Die Näherung ist eine Messung bis n = 60 (Ketten) und 30 (Graphen):** die Aussage über den kleinsten Primteiler ist eine Messung und eine Erklärung aus der Formel, kein Satz.
- **Aufzählen als Gegenprobe ist begrenzt** (300.000 Färbungen; Graphen n ≤ 6; Spielpläne bis 8 Teams); darüber stehen nur die Formeln.
- **Spielpläne:** ungeordnete Runden, ohne Heimrecht; mit geordneten Runden (n − 1)!-mal so viele.
- **Aufwand als Schritte und Summanden**, nicht als Zeit; der erste Aufruf braucht etwa eine halbe Minute, weil die Experimente einmal rechnen (danach zwischengespeichert; für 8 Teams allein etwa 13 Sekunden).
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Halsketten n = 4 und 6, Brett 2×2, Graphen n = 3, K₄ und K₆), Aufzählen der Bahnen durch kanonische Formen (kleinste Drehung, kleinste Spiegelung), Fixpunkte je Gruppenelement durch Brute Force gleich k^Zyklen, Bahn-Stabilisator-Satz (Bahngröße mal Stabilisator gleich |G|, Bahngrößen addieren sich zur Gesamtzahl), Zyklenzahlen der Quadratsymmetrien aus der Geometrie gleich denen der Permutationen für s = 1 bis 8, Pólya mit Gewicht gegen Aufzählen, Zyklen auf den Paaren gegen die tatsächliche Wirkung, Graphen gegen alle Permutationen und Union-Find, Spielpläne gegen eine unabhängige Gültigkeitsprüfung und gegen die Zirkelmethode.
- **Eigenschaften:** untere Schranke Bahnen ≥ Gesamtzahl/|G|, Armbänder ≤ Halsketten ≤ alle Färbungen, Bahnen wachsen mit n und k, Gruppenordnungen und Abschluss, Gewichtsverteilung palindromisch, Fehler der Näherung bei Primzahl-n exakt gleich (n − 1)·k/(k^n + (n − 1)·k), Verhältnis bei Graphen fällt gegen 1, Zyklentypen decken S_n ab, alle Rechenwege stimmen auf einem Gitter von Einstellungen überein.
- **Randfälle:** n = 1, eine Farbe, keine Symmetrie, Größen über den Grenzen mit Hinweis, feste Symmetrie bei Graphen und Spielplänen mit Hinweis, ungerade Teamzahlen, Zahlen über der 4300-Stellen-Grenze nur formatiert, Gruppe zu groß, Formatierung.
- **Urteilstexte:** genauer Wortlaut für alle Voreinstellungen und Experimente.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jedes Preset, Permalink mit Müll, Spielwiese, PDF für jede Familie, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

110 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `bpo_algorithm.py` | Kern: Gruppen, Burnside, Zyklenindex-Formeln, Pólya mit Gewicht, Graphen, Wurzelbäume, Spielpläne |
| `bpo_constants.py` | Regler-Grenzen, Experiment-Konstanten, Farben, Presets |
| `bpo_evaluation.py` | Analyse, Experimente, Urteilstexte, Formatierung |
| `bpo_layout.py` | Fester Kopf (Stylesheet) |
| `bpo_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `bpo_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `bpo_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Isomorphieausschluss beim Suchen (Erzeugen bis auf Symmetrie, orderly generation, Symmetriebrechung):** Stück 12 (gelb, wird erst danach entschieden).
- **Zählen der Isomorphieklassen von 1-Faktorisierungen für n ≥ 10:** eine Suche, kein Zyklenindex; nur im Text.
- **Zyklenindex für Spezies (Joyal), Pólya-Redfield-Satz mit Farbgruppen, chemische Isomere, unendliche Gruppen:** nicht Teil der Demo.
- **Gleichverteilt aus den Bahnen ziehen (Pólya-Sampler):** Stück 10 hat das Ziehen ohne Symmetrie behandelt; die Verbindung ist nicht Teil dieses Stücks.
- **Verwandte Demos:** `round-robin-demo` und `double-round-robin-demo` (ein Plan nach der Zirkelmethode), `multimengen-partitionen-demo` (Euler-Transformation), `beschriftete-strukturen-demo` (Zyklen, beschriftet gegen unbeschriftet), `zaehlen-nach-parameter-demo` (Gewicht); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
