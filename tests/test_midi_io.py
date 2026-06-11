import glob
import os

from mido import MidiFile, tempo2bpm

from neurotune.generator import generate_piece, load_corpus_model
from neurotune.midi_io import extract_pitches, render
from neurotune.presets import PRESETS
from neurotune.theory import build_scale, parse_note

CORPUS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..",
                                       "Samples", "*.mid")))


def test_extract_pitches_from_sample_corpus():
    assert CORPUS, "Samples/ corpus missing"
    pitches = extract_pitches(CORPUS[0])
    assert len(pitches) > 100
    assert all(0 <= p <= 127 for p in pitches)


def test_render_roundtrip(tmp_path):
    preset = PRESETS["steady_focus"]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = load_corpus_model(CORPUS, scale)
    events = generate_piece(preset, model, minutes=0.5, seed=3)

    out = tmp_path / "out.mid"
    render(events, preset, str(out))

    midi = MidiFile(str(out))
    # meta + melody + drone + percussion for steady_focus
    assert len(midi.tracks) == 4
    tempos = [msg for track in midi.tracks for msg in track if msg.type == "set_tempo"]
    assert round(tempo2bpm(tempos[0].tempo)) == preset.tempo_bpm

    ons = [msg for track in midi.tracks for msg in track
           if msg.type == "note_on" and msg.velocity > 0]
    offs = [msg for track in midi.tracks for msg in track if msg.type == "note_off"]
    assert len(ons) == len(offs) > 0
    # Narrow dynamics: melody velocities stay within the preset band (survey §3.4).
    melody_ons = [msg for msg in ons if msg.channel == 0]
    assert all(abs(m.velocity - preset.velocity) <= preset.velocity_spread
               for m in melody_ons)


def test_render_no_percussion_for_calm(tmp_path):
    preset = PRESETS["deep_calm"]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = load_corpus_model(CORPUS, scale)
    events = generate_piece(preset, model, minutes=0.5, seed=3)
    out = tmp_path / "calm.mid"
    render(events, preset, str(out))
    midi = MidiFile(str(out))
    channels = {msg.channel for track in midi.tracks for msg in track
                if msg.type == "note_on"}
    assert 9 not in channels
