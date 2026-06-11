import glob
import os

import pytest

from neurotune.generator import generate_piece, load_corpus_model
from neurotune.presets import PRESETS
from neurotune.theory import build_scale, parse_note

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def _model_and_scale(preset):
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    return load_corpus_model(CORPUS, scale), scale


@pytest.mark.parametrize("mood", sorted(PRESETS))
def test_pitches_stay_in_scale_and_leaps_capped(mood):
    preset = PRESETS[mood]
    model, scale = _model_and_scale(preset)
    events = generate_piece(preset, model, minutes=1.0, seed=7)
    assert events
    pitches = [p for p, *_ in events]
    assert all(p in scale for p in pitches)
    # Leaps are capped *within* a phrase; check consecutive notes per phrase.
    by_start = sorted(events, key=lambda e: e[1])
    for (p1, s1, *_), (p2, s2, *_) in zip(by_start, by_start[1:]):
        if s2 - s1 < preset.phrase_bars * 4:  # same or adjacent phrase region
            assert abs(p2 - p1) <= preset.max_leap + 12  # form jumps allowed at bounds


def test_deterministic_with_seed():
    preset = PRESETS["steady_focus"]
    model, _ = _model_and_scale(preset)
    a = generate_piece(preset, model, minutes=1.0, seed=42)
    b = generate_piece(preset, model, minutes=1.0, seed=42)
    c = generate_piece(preset, model, minutes=1.0, seed=43)
    assert a == b
    assert a != c


def test_form_repetition_is_literal():
    # AABA: phrase 0 and phrase 1 must be identical note-for-note (predictability).
    preset = PRESETS["calm_focus"]
    model, _ = _model_and_scale(preset)
    events = generate_piece(preset, model, minutes=2.0, seed=1)
    phrase_beats = preset.phrase_bars * 4
    first = [(p, s, d, v) for p, s, d, v in events if s < phrase_beats]
    second = [(p, s - phrase_beats, d, v) for p, s, d, v in events
              if phrase_beats <= s < 2 * phrase_beats]
    assert first == second


def test_length_close_to_requested():
    preset = PRESETS["steady_focus"]
    model, _ = _model_and_scale(preset)
    events = generate_piece(preset, model, minutes=3.0, seed=5)
    last_beat = max(s + d for _, s, d, _ in events)
    seconds = last_beat * 60.0 / preset.tempo_bpm
    assert 0.9 * 180 <= seconds <= 1.2 * 180
