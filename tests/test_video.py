import glob
import os

import pytest

from neurotune.audio import synthesize
from neurotune.generator import generate_piece, load_corpus_model
from neurotune.presets import PRESETS
from neurotune.theory import build_scale, parse_note

imageio_ffmpeg = pytest.importorskip("imageio_ffmpeg")

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def test_render_video_produces_playable_mp4(tmp_path):
    from neurotune import video

    preset = PRESETS["steady_focus"]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = load_corpus_model(CORPUS, scale)
    events = generate_piece(preset, model, minutes=0.15, seed=3)

    wav = tmp_path / "a.wav"
    synthesize(events, preset, str(wav), sample_rate=22050, seed=1)
    out = tmp_path / "a.mp4"
    video.render_video(str(wav), preset, str(out), width=320, height=180)

    assert out.exists() and out.stat().st_size > 1000
    with open(out, "rb") as fh:
        head = fh.read(12)
    assert b"ftyp" in head  # MP4 container signature
