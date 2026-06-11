import os

from mido import MidiFile

from neurotune.cli import main


def test_list_moods(capsys):
    assert main(["--list-moods"]) == 0
    out = capsys.readouterr().out
    for mood in ("deep_calm", "calm_focus", "steady_focus", "energize"):
        assert mood in out


def test_generate_via_cli(tmp_path):
    out = tmp_path / "focus.mid"
    assert main(["--mood", "steady_focus", "--minutes", "0.5",
                 "--seed", "1", "--out", str(out)]) == 0
    assert os.path.getsize(out) > 100
    MidiFile(str(out))  # parses cleanly


def test_tempo_and_root_override(tmp_path):
    out = tmp_path / "custom.mid"
    assert main(["--mood", "deep_calm", "--minutes", "0.5", "--seed", "1",
                 "--tempo", "60", "--root", "E3", "--out", str(out)]) == 0
    midi = MidiFile(str(out))
    tempos = [msg for track in midi.tracks for msg in track
              if msg.type == "set_tempo"]
    assert round(60_000_000 / tempos[0].tempo) == 60
