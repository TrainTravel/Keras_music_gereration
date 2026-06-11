import glob
import os
import subprocess

import numpy as np
import pytest

from neurotune import timer
from neurotune.audio import synthesize
from neurotune.generator import generate_piece, load_corpus_model
from neurotune.presets import PRESETS
from neurotune.theory import build_scale, parse_note

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def test_seven_segment_lights_pixels():
    glyphs = timer.render_seven_segment("12:34", 80)
    assert glyphs.shape[0] == 80
    assert glyphs.shape[1] > 80          # several characters wide
    assert glyphs.any()                  # something is lit
    # '1' lights fewer pixels than '8'
    assert timer.render_seven_segment("1", 80).sum() < \
           timer.render_seven_segment("8", 80).sum()


def test_remaining_counts_down_within_segments():
    segs = [("FOCUS", 10), ("BREAK", 5)]
    assert timer._remaining_at(segs, 0.0) == (10, "FOCUS")
    assert timer._remaining_at(segs, 9.5)[1] == "FOCUS"
    assert timer._remaining_at(segs, 10.5)[1] == "BREAK"
    assert timer._remaining_at(segs, 99)[0] == 0


def _short_wav(tmp_path, mood="steady_focus", minutes=0.12):
    preset = PRESETS[mood]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = load_corpus_model(CORPUS, scale)
    events = generate_piece(preset, model, minutes=minutes, seed=3)
    wav = tmp_path / f"{mood}.wav"
    synthesize(events, preset, str(wav), sample_rate=22050, seed=1)
    return str(wav), preset


def test_timer_video_is_moving(tmp_path):
    pytest.importorskip("imageio_ffmpeg")
    from neurotune import video

    wav, preset = _short_wav(tmp_path)
    out = tmp_path / "timer.mp4"
    timer.render_timer_video(wav, preset, str(out), fps=10,
                             width=160, height=90)
    assert out.exists()
    with open(out, "rb") as fh:
        assert b"ftyp" in fh.read(12)

    # Extract two frames a second apart and assert they differ (not a still image).
    exe = video._ffmpeg_exe()
    f0 = tmp_path / "f0.ppm"
    f1 = tmp_path / "f1.ppm"
    subprocess.run([exe, "-y", "-i", str(out), "-vf", "select=eq(n\\,0)",
                    "-frames:v", "1", str(f0)], check=True, capture_output=True)
    subprocess.run([exe, "-y", "-ss", "1.0", "-i", str(out),
                    "-frames:v", "1", str(f1)], check=True, capture_output=True)
    assert f0.read_bytes() != f1.read_bytes()
