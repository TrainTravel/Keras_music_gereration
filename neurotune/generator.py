"""Markov melody generation constrained for predictability.

Order-1 Markov chain over scale degrees, learned from a MIDI corpus, sampled
with low temperature and a per-preset leap cap. Pieces are assembled from
repeated phrases (AABA by default) so most of the output is literal repetition —
predictability is the active ingredient identified in docs/SURVEY.md.
"""

import math
import random

from .midi_io import extract_pitches
from .presets import MoodPreset
from .theory import build_scale, parse_note, snap_to_scale

BEATS_PER_BAR = 4


class MarkovMelodyModel:
    """Transition counts between scale degrees (indices into a scale)."""

    def __init__(self, n_degrees: int):
        self.n = n_degrees
        self.counts = [[1.0] * n_degrees for _ in range(n_degrees)]  # add-one smoothing

    def fit_pitches(self, pitches: list[int], scale_pitches: list[int]) -> None:
        degrees = [scale_pitches.index(snap_to_scale(p, scale_pitches)) for p in pitches]
        for a, b in zip(degrees, degrees[1:]):
            self.counts[a][b] += 1.0

    def sample_next(self, current: int, rng: random.Random,
                    temperature: float, max_step: int) -> int:
        lo, hi = max(0, current - max_step), min(self.n - 1, current + max_step)
        candidates = range(lo, hi + 1)
        weights = [self.counts[current][c] ** (1.0 / max(temperature, 1e-3))
                   for c in candidates]
        return rng.choices(list(candidates), weights=weights)[0]


def load_corpus_model(corpus_paths: list[str], scale_pitches: list[int]) -> MarkovMelodyModel:
    model = MarkovMelodyModel(len(scale_pitches))
    for path in corpus_paths:
        model.fit_pitches(extract_pitches(path), scale_pitches)
    return model


def _max_degree_step(preset: MoodPreset, scale_pitches: list[int]) -> int:
    """Largest degree step whose semitone distance stays within preset.max_leap."""
    step = 1
    while step + 1 < len(scale_pitches) and all(
            abs(scale_pitches[i + step + 1] - scale_pitches[i]) <= preset.max_leap
            for i in range(len(scale_pitches) - step - 1)):
        step += 1
    return step


def generate_phrase(preset: MoodPreset, model: MarkovMelodyModel,
                    scale_pitches: list[int], rng: random.Random,
                    start_degree: int | None = None):
    """One phrase of preset.phrase_bars bars: list of (pitch, start, dur, velocity)."""
    total_beats = preset.phrase_bars * BEATS_PER_BAR
    durations = list(preset.duration_weights)
    weights = list(preset.duration_weights.values())
    max_step = _max_degree_step(preset, scale_pitches)
    degree = start_degree if start_degree is not None else len(scale_pitches) // 2

    events = []
    beat = 0.0
    while beat < total_beats:
        dur = min(rng.choices(durations, weights=weights)[0], total_beats - beat)
        if rng.random() >= preset.rest_prob:
            vel = preset.velocity + rng.randint(-preset.velocity_spread,
                                                preset.velocity_spread)
            events.append((scale_pitches[degree], beat, dur * 0.95,
                           max(1, min(127, vel))))
            degree = model.sample_next(degree, rng, preset.temperature, max_step)
        beat += dur
    return events


def generate_piece(preset: MoodPreset, model: MarkovMelodyModel, minutes: float,
                   seed: int | None = None):
    """Assemble phrases in the preset's form until the piece reaches `minutes`."""
    rng = random.Random(seed)
    scale_pitches = build_scale(parse_note(preset.root), preset.scale, preset.octaves)

    phrase_beats = preset.phrase_bars * BEATS_PER_BAR
    total_beats = minutes * 60.0 / (60.0 / preset.tempo_bpm)
    n_phrases = max(len(preset.form), math.ceil(total_beats / phrase_beats))

    # One pre-generated phrase per distinct form letter; 'B' starts higher for
    # gentle contrast, everything else is literal repetition.
    letters = {}
    for letter in preset.form:
        if letter not in letters:
            start = (len(scale_pitches) * 2 // 3 if letter == "B"
                     else len(scale_pitches) // 2)
            letters[letter] = generate_phrase(preset, model, scale_pitches, rng, start)

    events = []
    for i in range(n_phrases):
        offset = i * phrase_beats
        phrase = letters[preset.form[i % len(preset.form)]]
        events.extend((p, s + offset, d, v) for p, s, d, v in phrase)
    return events
