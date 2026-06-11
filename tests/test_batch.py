import glob
import json
import os

import pytest

from neurotune import batch
from neurotune.cli import main

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def test_parse_seeds_ranges_and_lists():
    assert batch.parse_seeds("1-3,7") == [1, 2, 3, 7]
    assert batch.parse_seeds("5") == [5]
    assert batch.parse_seeds("3,1,2") == [1, 2, 3]  # sorted, unique
    assert batch.parse_seeds("1-2,2-3") == [1, 2, 3]


def test_parse_seeds_rejects_bad_input():
    with pytest.raises(ValueError):
        batch.parse_seeds("")
    with pytest.raises(ValueError):
        batch.parse_seeds("5-1")


def test_parse_moods_and_formats():
    assert batch.parse_moods(None) == sorted(batch.PRESETS)
    assert batch.parse_moods("deep_calm,energize") == ["deep_calm", "energize"]
    with pytest.raises(ValueError):
        batch.parse_moods("nope")
    assert batch.parse_formats(None) == ["midi", "wav"]
    with pytest.raises(ValueError):
        batch.parse_formats("midi,flac")


def test_run_batch_creates_matrix_and_manifest(tmp_path):
    out = tmp_path / "uploads"
    manifest = batch.run_batch(
        moods=["deep_calm", "steady_focus"], seeds=[1, 2], minutes=0.2,
        outdir=str(out), formats=["midi", "wav"], corpus_paths=CORPUS,
        progress=lambda *_: None,
    )
    # 2 moods x 2 seeds = 4 records, each with a .mid and .wav
    assert manifest["count"] == 4
    mids = sorted(glob.glob(str(out / "*.mid")))
    wavs = sorted(glob.glob(str(out / "*.wav")))
    assert len(mids) == 4 and len(wavs) == 4

    on_disk = json.loads((out / "manifest.json").read_text())
    assert on_disk["count"] == 4
    for item in on_disk["items"]:
        assert os.path.exists(item["files"]["midi"])
        assert os.path.exists(item["files"]["wav"])
        assert item["mood"] in ("deep_calm", "steady_focus")


def test_cli_batch_requires_seeds(capsys):
    assert main(["--batch"]) == 2
    assert "requires --seeds" in capsys.readouterr().err


def test_cli_batch_end_to_end(tmp_path):
    out = tmp_path / "up"
    rc = main(["--batch", "--moods", "calm_focus", "--seeds", "1-2",
               "--minutes", "0.2", "--outdir", str(out), "--formats", "midi"])
    assert rc == 0
    assert len(glob.glob(str(out / "*.mid"))) == 2
