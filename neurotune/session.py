"""M10 — Pomodoro focus sessions: structured work/break coworking videos.

Composes the audio engine (audio.synthesize) and the countdown overlay (timer)
into the channel's "Cowork With Me" / focus-timer format: N rounds of W minutes
work + B minutes break, each round counting down on screen with the background
palette switching between the work mood and the calmer break mood.
"""

import os
import tempfile
import wave

import numpy as np

from . import audio, generator, timer, video
from .presets import PRESETS
from .theory import build_scale, parse_note

WORK_LABEL = "FOCUS"
BREAK_LABEL = "BREAK"


def parse_session(spec: str) -> tuple[float, float, int]:
    """Parse 'WxBxN' -> (work_minutes, break_minutes, rounds). W/B may be fractional."""
    parts = spec.lower().split("x")
    if len(parts) != 3:
        raise ValueError(f"session must be WxBxN, e.g. 25x5x4 (got {spec!r})")
    work, brk, rounds = float(parts[0]), float(parts[1]), int(parts[2])
    if work <= 0 or brk < 0 or rounds < 1:
        raise ValueError(f"invalid session values in {spec!r}")
    return work, brk, rounds


def _synth_segment(mood: str, minutes: float, seed: int, sample_rate: int):
    """Return a float32 mono buffer of the generated audio for one segment."""
    preset = PRESETS[mood]
    scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
    model = generator.load_corpus_model(_CORPUS, scale)
    events = generator.generate_piece(preset, model, minutes, seed=seed)
    # Render with the synth, then read frames back into a buffer for concatenation.
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        audio.synthesize(events, preset, tmp, sample_rate=sample_rate, seed=seed)
        with wave.open(tmp, "rb") as w:
            frames = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
    finally:
        os.remove(tmp)
    return frames.astype("float32") / 32767.0


# Resolved lazily so importing this module doesn't require the corpus.
_CORPUS = None


def render_session(spec: str, out_path: str, *, work_mood="steady_focus",
                   break_mood="deep_calm", seed: int | None = None,
                   corpus_paths=None, sample_rate=None, fps=10,
                   width=1280, height=720) -> str:
    """Render a Pomodoro session video to out_path. Returns out_path."""
    global _CORPUS
    _CORPUS = corpus_paths if corpus_paths is not None else _CORPUS
    if _CORPUS is None:
        raise ValueError("corpus_paths is required")
    sr = sample_rate or audio.SAMPLE_RATE
    work_min, break_min, rounds = parse_session(spec)

    buffers = []
    segments = []          # (label, seconds) for the countdown
    base_seed = seed if seed is not None else 0
    for r in range(rounds):
        work_buf = _synth_segment(work_mood, work_min, base_seed + r, sr)
        buffers.append(work_buf)
        segments.append((WORK_LABEL, len(work_buf) / sr))
        if break_min > 0:
            brk_buf = _synth_segment(break_mood, break_min, base_seed + 100 + r, sr)
            buffers.append(brk_buf)
            segments.append((BREAK_LABEL, len(brk_buf) / sr))

    full = np.concatenate(buffers)
    samples = np.int16(np.clip(full, -1, 1) * 0.95 * 32767)

    fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(samples.tobytes())

        palettes = {
            WORK_LABEL: video._PALETTES.get(work_mood, ((20, 24, 40), (50, 40, 64))),
            BREAK_LABEL: video._PALETTES.get(break_mood, ((18, 22, 40), (40, 30, 60))),
        }
        timer.render_timer_video(
            wav_path, PRESETS[work_mood], out_path, fps=fps,
            segments=segments, palettes=palettes, width=width, height=height,
        )
    finally:
        os.remove(wav_path)
    return out_path
