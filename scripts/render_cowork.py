"""Restart-proof renderer for the flagship 2-hour cowork video.

Synthesizes the session audio ONCE to Generated/cowork_session.wav (kept on
disk), then encodes the timer video from it. If the encode is interrupted,
re-running skips straight to encoding instead of re-synthesizing ~100 minutes
of audio. Usage:  python scripts/render_cowork.py
"""

import glob
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neurotune import audio, session, timer, video  # noqa: E402
from neurotune.presets import PRESETS  # noqa: E402

SPEC = "25x5x4"
SEED = 20260611
WORK, BREAK = "steady_focus", "deep_calm"
WAV = "Generated/cowork_session.wav"
OUT = "Generated/cowork_25x5x4.mp4"


def main():
    os.makedirs("Generated", exist_ok=True)
    corpus = sorted(glob.glob("Samples/*.mid"))
    work_min, break_min, rounds = session.parse_session(SPEC)
    session._CORPUS = corpus
    sr = audio.SAMPLE_RATE

    # Segment schedule is deterministic; rebuild it cheaply every run.
    segments = []
    if not os.path.exists(WAV):
        buffers = []
        for r in range(rounds):
            buf = session._synth_segment(WORK, work_min, SEED + r, sr)
            buffers.append(buf)
            segments.append((session.WORK_LABEL, len(buf) / sr))
            buf = session._synth_segment(BREAK, break_min, SEED + 100 + r, sr)
            buffers.append(buf)
            segments.append((session.BREAK_LABEL, len(buf) / sr))
            print(f"synthesized round {r + 1}/{rounds}", flush=True)
        full = np.concatenate(buffers)
        samples = np.int16(np.clip(full, -1, 1) * 0.95 * 32767)
        with wave.open(WAV, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(samples.tobytes())
        print(f"cached audio -> {WAV}", flush=True)
    else:
        # Reconstruct the schedule from the spec (segment lengths are nominal).
        for _ in range(rounds):
            segments.append((session.WORK_LABEL, work_min * 60))
            segments.append((session.BREAK_LABEL, break_min * 60))
        print(f"reusing cached audio {WAV}", flush=True)

    palettes = {
        session.WORK_LABEL: video._PALETTES[WORK],
        session.BREAK_LABEL: video._PALETTES[BREAK],
    }
    timer.render_timer_video(WAV, PRESETS[WORK], OUT, fps=1,
                             segments=segments, palettes=palettes)
    print(f"RENDER_DONE {OUT}", flush=True)


if __name__ == "__main__":
    main()
