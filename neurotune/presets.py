"""Evidence-based mood presets.

Each parameter traces to a finding in docs/SURVEY.md §4:
tempo sets arousal; narrow velocity bands respect sensory sensitivity; low
sampling temperature, capped leaps and AABA form keep the output predictable
(the active ingredient for autistic listeners); the steady percussion pulse in
`steady_focus` provides the constant moderate stimulation that helps ADHD focus.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MoodPreset:
    name: str
    description: str
    tempo_bpm: int
    root: str                      # melody scale root, e.g. "C3"
    scale: str                     # key into theory.SCALES
    octaves: int                   # melodic register span
    melody_program: int            # General MIDI program for melody
    pad_program: int               # General MIDI program for drone/pad
    drone: bool                    # sustained root+fifth pad under melody
    percussion: bool               # soft steady pulse on channel 9
    rest_prob: float               # probability a slot is silence
    velocity: int                  # centre of the velocity band
    velocity_spread: int           # max deviation from centre (narrow = calm)
    max_leap: int                  # melodic leap cap, in semitones
    temperature: float             # Markov sampling temperature (low = predictable)
    duration_weights: dict[float, float] = field(default_factory=dict)  # beats -> weight
    phrase_bars: int = 4
    form: str = "AABA"


PRESETS: dict[str, MoodPreset] = {p.name: p for p in [
    MoodPreset(
        name="deep_calm",
        description="Wind-down / recovery from sensory overload: very slow, low "
                    "register, long sustained notes over a drone.",
        tempo_bpm=54, root="C3", scale="major_pentatonic", octaves=1,
        melody_program=4, pad_program=89, drone=True, percussion=False,
        rest_prob=0.30, velocity=48, velocity_spread=6, max_leap=5,
        temperature=0.5, duration_weights={2.0: 3, 4.0: 2, 1.0: 1},
    ),
    MoodPreset(
        name="calm_focus",
        description="Anxious-but-need-to-work: gentle pulse, mid register, "
                    "soft pentatonic melody.",
        tempo_bpm=66, root="D3", scale="major_pentatonic", octaves=2,
        melody_program=4, pad_program=89, drone=True, percussion=False,
        rest_prob=0.20, velocity=54, velocity_spread=8, max_leap=7,
        temperature=0.6, duration_weights={1.0: 3, 2.0: 2, 0.5: 1},
    ),
    MoodPreset(
        name="steady_focus",
        description="Default ADHD work mode: lo-fi-style steady percussion, "
                    "repetitive minor-pentatonic melody at 76 BPM.",
        tempo_bpm=76, root="A2", scale="minor_pentatonic", octaves=2,
        melody_program=4, pad_program=89, drone=True, percussion=True,
        rest_prob=0.15, velocity=58, velocity_spread=8, max_leap=7,
        temperature=0.7, duration_weights={0.5: 2, 1.0: 3, 2.0: 1},
    ),
    MoodPreset(
        name="energize",
        description="Task initiation / mood lift: brighter major key, denser "
                    "and faster, but still repetitive and surprise-free.",
        tempo_bpm=104, root="G3", scale="major", octaves=2,
        melody_program=0, pad_program=89, drone=True, percussion=True,
        rest_prob=0.10, velocity=68, velocity_spread=12, max_leap=9,
        temperature=0.8, duration_weights={0.5: 3, 1.0: 2, 0.25: 1},
    ),
]}
