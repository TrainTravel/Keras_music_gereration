import glob
import os
import subprocess

import pytest

from neurotune import session

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def test_parse_session():
    assert session.parse_session("25x5x4") == (25.0, 5.0, 4)
    assert session.parse_session("0.2x0.1x2") == (0.2, 0.1, 2)


@pytest.mark.parametrize("bad", ["25x5", "25x5x0", "axbxc", "-1x5x2", ""])
def test_parse_session_rejects_bad(bad):
    with pytest.raises(ValueError):
        session.parse_session(bad)


def test_render_session_duration_and_state_change(tmp_path):
    pytest.importorskip("imageio_ffmpeg")
    from neurotune import video

    out = tmp_path / "s.mp4"
    # 2 rounds of tiny work+break segments.
    session.render_session("0.1x0.1x2", str(out), work_mood="steady_focus",
                           break_mood="deep_calm", seed=1, corpus_paths=CORPUS,
                           sample_rate=22050, fps=8, width=160, height=90)
    assert out.exists()
    with open(out, "rb") as fh:
        assert b"ftyp" in fh.read(12)

    exe = video._ffmpeg_exe()
    info = subprocess.run([exe, "-i", str(out)], capture_output=True, text=True)
    dur_line = next(l for l in info.stderr.splitlines() if "Duration" in l)
    hh, mm, ss = dur_line.split("Duration:")[1].split(",")[0].strip().split(":")
    seconds = int(hh) * 3600 + int(mm) * 60 + float(ss)
    # 2 work + 2 break tiny segments — at least a couple of seconds of audio.
    assert seconds > 1.0

    # The work (steady_focus) and break (deep_calm) palettes differ, so a frame
    # from the first segment should differ from one well into the video.
    f0, f1 = tmp_path / "f0.ppm", tmp_path / "f1.ppm"
    subprocess.run([exe, "-y", "-i", str(out), "-frames:v", "1", str(f0)],
                   check=True, capture_output=True)
    subprocess.run([exe, "-y", "-sseof", "-0.5", "-i", str(out),
                    "-frames:v", "1", str(f1)], check=True, capture_output=True)
    assert f0.read_bytes() != f1.read_bytes()


def test_render_session_requires_corpus(tmp_path):
    session._CORPUS = None
    with pytest.raises(ValueError):
        session.render_session("1x1x1", str(tmp_path / "x.mp4"))
