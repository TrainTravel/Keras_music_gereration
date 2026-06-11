"""Music-theory helpers: note names, scales, and snapping pitches to a scale."""

NOTE_NAMES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
              "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10,
              "Bb": 10, "B": 11}

# Consonant scales only — survey §3.5: pentatonic/diatonic material avoids
# the harsh dissonance that sensory-sensitive listeners report as aversive.
SCALES = {
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "major": (0, 2, 4, 5, 7, 9, 11),
    "natural_minor": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
}


def parse_note(name: str) -> int:
    """Convert a note name like 'C3' or 'F#2' to a MIDI pitch (C-1 = 0)."""
    for prefix in sorted(NOTE_NAMES, key=len, reverse=True):
        if name.startswith(prefix):
            octave = int(name[len(prefix):])
            return NOTE_NAMES[prefix] + (octave + 1) * 12
    raise ValueError(f"unparseable note name: {name!r}")


def build_scale(root: int, scale_name: str, octaves: int) -> list[int]:
    """Ascending MIDI pitches of `scale_name` starting at `root`, spanning `octaves`."""
    intervals = SCALES[scale_name]
    pitches = [root + 12 * o + i for o in range(octaves) for i in intervals]
    pitches.append(root + 12 * octaves)  # close on the upper root
    return [p for p in pitches if 0 <= p <= 127]


def snap_to_scale(pitch: int, scale_pitches: list[int]) -> int:
    """Map an arbitrary MIDI pitch to the nearest pitch in the scale."""
    return min(scale_pitches, key=lambda s: (abs(s - pitch), s))
