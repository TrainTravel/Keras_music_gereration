from neurotune.presets import PRESETS
from neurotune.theory import SCALES, parse_note


def test_expected_presets_exist():
    assert {"deep_calm", "calm_focus", "steady_focus", "energize"} <= set(PRESETS)


def test_preset_parameters_are_sane():
    for preset in PRESETS.values():
        assert 40 <= preset.tempo_bpm <= 140
        assert preset.scale in SCALES
        parse_note(preset.root)  # must not raise
        assert 0 <= preset.rest_prob < 1
        assert 1 <= preset.velocity - preset.velocity_spread
        assert preset.velocity + preset.velocity_spread <= 127
        assert preset.duration_weights
        assert set(preset.form) and preset.phrase_bars > 0


def test_arousal_ordering_matches_survey():
    # Survey §3.3: tempo sets arousal — calm < focus < energize.
    assert (PRESETS["deep_calm"].tempo_bpm
            < PRESETS["calm_focus"].tempo_bpm
            < PRESETS["steady_focus"].tempo_bpm
            < PRESETS["energize"].tempo_bpm)
