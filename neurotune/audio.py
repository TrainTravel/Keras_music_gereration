"""Offline WAV synthesis — no soundfont required.

Renders the same note events used for MIDI into a playable mono WAV using a
small additive synth written with numpy and the stdlib `wave` module. Every
note gets a soft attack and release so there are no clicks or startling
transients (sensory sensitivity, docs/SURVEY.md §3.4), and overall gain is
kept conservative.
"""

import wave

import numpy as np

from . import midi_io
from .presets import MoodPreset

SAMPLE_RATE = 44_100


def _freq(pitch: int) -> float:
    return 440.0 * 2.0 ** ((pitch - 69) / 12.0)


def _envelope(n: int, sr: int, attack=0.02, release=0.08) -> np.ndarray:
    """Soft linear attack/release envelope; clipped to the note length."""
    env = np.ones(n, dtype="float32")
    a = min(int(attack * sr), n // 2)
    r = min(int(release * sr), n - a)
    if a:
        env[:a] = np.linspace(0.0, 1.0, a, dtype="float32")
    if r:
        env[n - r:] = np.linspace(1.0, 0.0, r, dtype="float32")
    return env


def _add_tone(buf, sr, freq, start_s, dur_s, gain, harmonics):
    n = int(dur_s * sr)
    if n <= 0:
        return
    t = np.arange(n, dtype="float32") / sr
    wave_sig = np.zeros(n, dtype="float32")
    for mult, amp in harmonics:
        wave_sig += amp * np.sin(2.0 * np.pi * freq * mult * t)
    wave_sig *= _envelope(n, sr) * gain
    i = int(start_s * sr)
    buf[i:i + n] += wave_sig[:len(buf) - i]


def _add_kick(buf, sr, start_s, gain):
    n = int(0.18 * sr)
    t = np.arange(n, dtype="float32") / sr
    freq = 110.0 * np.exp(-25.0 * t) + 45.0          # pitch drop = thump
    sig = np.sin(2.0 * np.pi * np.cumsum(freq) / sr) * np.exp(-18.0 * t) * gain
    i = int(start_s * sr)
    buf[i:i + n] += sig[:len(buf) - i].astype("float32")


def _add_hat(buf, sr, start_s, gain, rng):
    n = int(0.05 * sr)
    sig = rng.standard_normal(n).astype("float32") * np.exp(-60.0 * np.arange(n) / sr)
    i = int(start_s * sr)
    buf[i:i + n] += (sig * gain)[:len(buf) - i]


# Gentle, low-harmonic timbre — mostly fundamental, soft overtones.
_MELODY_HARMONICS = ((1.0, 0.6), (2.0, 0.18), (3.0, 0.06))
_DRONE_HARMONICS = ((1.0, 0.5), (2.0, 0.12))


def synthesize(melody_events, preset: MoodPreset, out_path: str,
               sample_rate: int = SAMPLE_RATE, seed: int | None = None) -> str:
    """Render melody (+ preset drone/percussion) to a mono 16-bit WAV file."""
    rng = np.random.default_rng(seed)
    spb = 60.0 / preset.tempo_bpm                    # seconds per beat
    total_beats = max((s + d) for _, s, d, _ in melody_events)
    n_samples = int((total_beats * spb + 1.0) * sample_rate)
    buf = np.zeros(n_samples, dtype="float32")

    for pitch, start, dur, vel in melody_events:
        _add_tone(buf, sample_rate, _freq(pitch), start * spb, dur * spb,
                  vel / 127.0, _MELODY_HARMONICS)

    if preset.drone:
        for pitch, start, dur, vel in midi_io.drone_events(preset, total_beats):
            _add_tone(buf, sample_rate, _freq(pitch), start * spb, dur * spb,
                      vel / 127.0, _DRONE_HARMONICS)

    if preset.percussion:
        for pitch, start, _, vel in midi_io.percussion_events(preset, total_beats):
            if pitch == midi_io.KICK:
                _add_kick(buf, sample_rate, start * spb, vel / 127.0)
            else:
                _add_hat(buf, sample_rate, start * spb, vel / 127.0, rng)

    peak = float(np.max(np.abs(buf))) or 1.0
    samples = np.int16(buf / peak * 0.89 * 32767)

    with wave.open(out_path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())
    return out_path
