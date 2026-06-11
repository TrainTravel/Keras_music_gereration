"""MIDI input (corpus note extraction) and output (multi-track rendering)."""

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .presets import MoodPreset
from .theory import parse_note

TICKS_PER_BEAT = 480

# General MIDI percussion notes (channel 9)
KICK = 36
CLOSED_HAT = 42


def extract_pitches(path: str) -> list[int]:
    """Pitches of all note_on events (velocity > 0) in file order, all channels."""
    midi = MidiFile(path)
    return [msg.note for track in midi.tracks for msg in track
            if msg.type == "note_on" and msg.velocity > 0]


def _events_to_track(events, channel: int, program: int) -> MidiTrack:
    """events: list of (pitch, start_beats, dur_beats, velocity), may overlap."""
    track = MidiTrack()
    track.append(Message("program_change", program=program, channel=channel, time=0))
    timeline = []
    for pitch, start, dur, vel in events:
        timeline.append((round(start * TICKS_PER_BEAT), 1, "note_on", pitch, vel))
        timeline.append((round((start + dur) * TICKS_PER_BEAT), 0, "note_off", pitch, 0))
    timeline.sort()  # note_off (0) before note_on (1) at the same tick
    now = 0
    for tick, _, kind, pitch, vel in timeline:
        track.append(Message(kind, note=pitch, velocity=vel,
                             channel=channel, time=tick - now))
        now = tick
    return track


def _drone_events(preset: MoodPreset, total_beats: float):
    """Sustained root+fifth pad, one bar at a time — the steady 'brown-noise-like'
    texture from the survey, re-attacked gently each bar to avoid decay to silence."""
    root = parse_note(preset.root) - 12  # one octave below the melody register
    vel = max(1, preset.velocity - 18)
    events = []
    beat = 0.0
    while beat < total_beats:
        dur = min(4.0, total_beats - beat)
        events.append((root, beat, dur, vel))
        events.append((root + 7, beat, dur, vel))
        beat += 4.0
    return events


def _percussion_events(preset: MoodPreset, total_beats: float):
    """Soft constant pulse: kick on beats 1 and 3, hats on every offbeat."""
    kick_vel = max(1, preset.velocity - 10)
    hat_vel = max(1, preset.velocity - 24)
    events = []
    bar = 0
    while bar * 4 < total_beats:
        base = bar * 4.0
        events.append((KICK, base, 0.25, kick_vel))
        events.append((KICK, base + 2.0, 0.25, kick_vel))
        for eighth in range(8):
            events.append((CLOSED_HAT, base + eighth * 0.5 + 0.25, 0.2, hat_vel))
        bar += 1
    return [(p, s, d, v) for p, s, d, v in events if s < total_beats]


def render(melody_events, preset: MoodPreset, out_path: str) -> MidiFile:
    """Render melody (+ optional drone and percussion per preset) to a MIDI file."""
    midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    total_beats = max((s + d) for _, s, d, _ in melody_events)

    meta = MidiTrack()
    meta.append(MetaMessage("set_tempo", tempo=bpm2tempo(preset.tempo_bpm), time=0))
    meta.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    midi.tracks.append(meta)

    midi.tracks.append(_events_to_track(melody_events, 0, preset.melody_program))
    if preset.drone:
        midi.tracks.append(_events_to_track(_drone_events(preset, total_beats),
                                            1, preset.pad_program))
    if preset.percussion:
        midi.tracks.append(_events_to_track(_percussion_events(preset, total_beats),
                                            9, 0))
    midi.save(out_path)
    return midi
