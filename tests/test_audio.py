import glob
import os
import wave

from neurotune.audio import synthesize
from neurotune.generator import generate_piece, load_corpus_model
from neurotune.presets import PRESETS
from neurotune.theory import build_scale, parse_note

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def _events(mood, minutes=0.3):
    preset = PRESETS[mood]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = load_corpus_model(CORPUS, scale)
    return generate_piece(preset, model, minutes=minutes, seed=3), preset


def test_wav_is_valid_and_right_length(tmp_path):
    events, preset = _events("steady_focus", minutes=0.3)
    out = tmp_path / "out.wav"
    synthesize(events, preset, str(out), sample_rate=22050, seed=1)

    with wave.open(str(out), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 22050
        total_beats = max(s + d for _, s, d, _ in events)
        expected = total_beats * 60.0 / preset.tempo_bpm
        seconds = wav.getnframes() / 22050
        assert expected <= seconds <= expected + 1.5  # +1s tail


def test_wav_not_silent(tmp_path):
    events, preset = _events("calm_focus", minutes=0.3)
    out = tmp_path / "calm.wav"
    synthesize(events, preset, str(out), sample_rate=22050, seed=1)
    with wave.open(str(out), "rb") as wav:
        frames = wav.readframes(wav.getnframes())
    assert any(b != 0 for b in frames)
