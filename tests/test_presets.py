"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import bpo_constants as C
import bpo_evaluation as ev
import bpo_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["family"] in C.FAMILIES and preset["symmetry"] in C.SYMMETRIES, name
        assert C.N_MIN <= preset["n"] <= C.N_CAP[preset["family"]] and C.K_MIN <= preset["k"] <= C.K_MAX, name


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default


def test_every_preset_passes_the_checker_without_notes_or_problems():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [] and a.n_eff == preset["n"] and a.k_eff == preset["k"], name


def test_presets_differ_from_each_other_and_from_the_default_in_the_visible_fields():
    seen = set()
    for name, preset in C.PRESETS.items():
        visible = (preset["family"], preset["n"], preset["k"] if preset["family"] in ("Perlenketten", "Brett s×s") else None, preset["symmetry"] if preset["family"] in ("Perlenketten", "Brett s×s") else None)
        assert visible not in seen, name
        seen.add(visible)


def test_every_family_appears_in_a_preset():
    assert {p["family"] for p in C.PRESETS.values()} == set(C.FAMILIES)


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["family_select"].choices == C.FAMILIES and P.SETTING_SPECS["symmetry_select"].choices == C.SYMMETRIES
