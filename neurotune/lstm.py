"""Optional LSTM melody engine — the original notebook's approach, modernized.

Trains a small tf.keras LSTM on corpus pitch sequences and generates a melody,
then snaps every predicted pitch to the preset's scale and quantizes timing to
the preset's duration grid, so even a noisy model yields consonant, predictable
output. Requires tensorflow; the default Markov engine does not.
"""

import random

import numpy as np

from .midi_io import extract_pitches
from .presets import MoodPreset
from .theory import build_scale, parse_note, snap_to_scale

WINDOW = 30


def _build_model(window: int):
    from tensorflow import keras

    model = keras.Sequential([
        keras.layers.Input(shape=(window, 1)),
        keras.layers.LSTM(64, return_sequences=True),
        keras.layers.Dropout(0.3),
        keras.layers.LSTM(32),
        keras.layers.Dense(1, activation="linear"),
    ])
    model.compile(loss="mse", optimizer=keras.optimizers.Adam(learning_rate=0.001))
    return model


def train(corpus_paths: list[str], epochs: int = 5, window: int = WINDOW, seed=None):
    """Train on min-max-scaled pitch sequences; returns (model, lo, hi, seed_window)."""
    import tensorflow as tf

    if seed is not None:
        tf.keras.utils.set_random_seed(seed)
    pitches = []
    for path in corpus_paths:
        pitches.extend(extract_pitches(path))
    if len(pitches) <= window + 1:
        raise ValueError("corpus too small to train the LSTM engine")

    lo, hi = min(pitches), max(pitches)
    scaled = (np.array(pitches, dtype="float32") - lo) / max(hi - lo, 1)
    X = np.array([scaled[i:i + window] for i in range(len(scaled) - window)])
    y = scaled[window:]
    model = _build_model(window)
    model.fit(X[..., None], y, batch_size=32, epochs=epochs, verbose=0)
    return model, lo, hi, scaled[:window].tolist()


def generate_events(preset: MoodPreset, corpus_paths: list[str], minutes: float,
                    seed: int | None = None, epochs: int = 5):
    """Generate (pitch, start, dur, velocity) events compatible with midi_io.render."""
    model, lo, hi, window_vals = train(corpus_paths, epochs=epochs, seed=seed)
    rng = random.Random(seed)
    scale_pitches = build_scale(parse_note(preset.root), preset.scale, preset.octaves)

    durations = list(preset.duration_weights)
    weights = list(preset.duration_weights.values())
    total_beats = minutes * preset.tempo_bpm

    events = []
    beat = 0.0
    window = list(window_vals)
    while beat < total_beats:
        pred = float(model.predict(np.array(window)[None, :, None], verbose=0)[0, 0])
        window = window[1:] + [pred]
        dur = rng.choices(durations, weights=weights)[0]
        if rng.random() >= preset.rest_prob:
            pitch = snap_to_scale(int(round(pred * (hi - lo) + lo)), scale_pitches)
            vel = preset.velocity + rng.randint(-preset.velocity_spread,
                                                preset.velocity_spread)
            events.append((pitch, beat, dur * 0.95, max(1, min(127, vel))))
        beat += dur
    return events
