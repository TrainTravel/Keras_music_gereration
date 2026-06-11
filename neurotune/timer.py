"""M9 — countdown timer overlay drawn with pure numpy (no fonts, no PIL).

Digits 0-9 and ':' are rendered as a classic 7-segment display using array
slicing, then composited onto a per-segment gradient background. Frames are
streamed straight into the bundled ffmpeg as raw video (no temp files, so
hours-long renders are disk-cheap) and muxed with the audio bed.
Visuals are kept gentle (soft contrast, no flashing) per the accessibility goals
in docs/SURVEY.md and docs/CHANNEL_PLAN.md. Work/break state is conveyed by the
background palette rather than small hard-to-read text.
"""

import subprocess

import numpy as np

from . import video
from .presets import MoodPreset

# seg order: a(top) b(top-right) c(bottom-right) d(bottom) e(bottom-left)
#            f(top-left) g(middle)
_SEGMENTS = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg",
    "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}
_DIGIT_ON = (235, 238, 245)      # soft off-white, not harsh pure white


def _draw_segment(canvas, seg, x, y, w, h, t):
    mid = y + h // 2
    if seg == "a":      canvas[y:y + t, x:x + w] = _DIGIT_ON
    elif seg == "g":    canvas[mid - t // 2:mid - t // 2 + t, x:x + w] = _DIGIT_ON
    elif seg == "d":    canvas[y + h - t:y + h, x:x + w] = _DIGIT_ON
    elif seg == "f":    canvas[y:mid, x:x + t] = _DIGIT_ON
    elif seg == "b":    canvas[y:mid, x + w - t:x + w] = _DIGIT_ON
    elif seg == "e":    canvas[mid:y + h, x:x + t] = _DIGIT_ON
    elif seg == "c":    canvas[mid:y + h, x + w - t:x + w] = _DIGIT_ON


def render_seven_segment(text: str, height: int) -> np.ndarray:
    """Render `text` (digits and ':') as an (height, width, 3) uint8 array.
    Unlit pixels are zero — use the nonzero mask to composite."""
    dh = height
    dw = int(dh * 0.55)
    t = max(2, dh // 9)
    colon_w = max(t * 2, dw // 3)
    gap = max(t, dw // 8)

    widths = [colon_w if ch == ":" else dw for ch in text]
    total_w = sum(widths) + gap * (len(text) - 1)
    canvas = np.zeros((dh, total_w, 3), dtype="uint8")

    x = 0
    for ch, w in zip(text, widths):
        if ch == ":":
            r = max(2, t)
            for cy in (dh // 3, 2 * dh // 3):
                canvas[cy - r:cy + r, x + w // 2 - r:x + w // 2 + r] = _DIGIT_ON
        elif ch in _SEGMENTS:
            for seg in _SEGMENTS[ch]:
                _draw_segment(canvas, seg, x, 0, w, dh, t)
        x += w + gap
    return canvas


def _composite_centered(bg: np.ndarray, glyphs: np.ndarray, dy: int = 0):
    """Composite nonzero glyph pixels centered on bg (returns a copy)."""
    out = bg.copy()
    H, W = out.shape[:2]
    gh, gw = glyphs.shape[:2]
    y0, x0 = (H - gh) // 2 + dy, (W - gw) // 2
    region = out[y0:y0 + gh, x0:x0 + gw]
    mask = glyphs.any(axis=2)
    region[mask] = glyphs[mask]
    out[y0:y0 + gh, x0:x0 + gw] = region
    return out


def _fmt_mmss(seconds: int) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def gradient_array(top, bottom, width, height) -> np.ndarray:
    """Soft vertical gradient with a faint centre glow, as a uint8 RGB array."""
    ramp = np.linspace(0.0, 1.0, height, dtype="float32")[:, None]
    rgb = np.empty((height, width, 3), dtype="float32")
    for c in range(3):
        rgb[:, :, c] = top[c] * (1 - ramp) + bottom[c] * ramp
    yy, xx = np.mgrid[0:height, 0:width].astype("float32")
    glow = np.exp(-(((xx - width / 2) / (width * 0.6)) ** 2
                    + ((yy - height / 2) / (height * 0.6)) ** 2))
    rgb += glow[:, :, None] * 14.0
    return np.clip(rgb, 0, 255).astype("uint8")


def _remaining_at(segments, t_sec):
    """Return (seconds_remaining_in_current_segment, label) at absolute time t_sec."""
    acc = 0.0
    for seg_label, seg_seconds in segments:
        if t_sec < acc + seg_seconds:
            return int(np.ceil(acc + seg_seconds - t_sec)), seg_label
        acc += seg_seconds
    return 0, segments[-1][0]


def render_timer_video(wav_path: str, preset: MoodPreset, out_path: str, *,
                       fps: int = 10, count_from: int | None = None,
                       label: str | None = None, segments=None,
                       palettes: dict | None = None,
                       width: int = 1280, height: int = 720) -> str:
    """Render a countdown video over `wav_path`.

    segments: optional list of (label, seconds); the clock counts down within each
      in turn. Defaults to one segment for the whole audio (from `count_from`).
    palettes: optional {label: (top_rgb, bottom_rgb)} so work/break states show a
      different background. Falls back to the preset's gradient palette."""
    duration = video._wav_seconds(wav_path)
    if segments is None:
        total = int(round(count_from if count_from is not None else duration))
        segments = [(label, total)]

    default_pal = video._PALETTES.get(preset.name, ((20, 24, 40), (50, 40, 64)))
    palettes = palettes or {}
    # Cache one background array per distinct palette.
    bg_cache = {}

    def bg_for(lbl):
        top, bottom = palettes.get(lbl, default_pal)
        key = (top, bottom)
        if key not in bg_cache:
            bg_cache[key] = gradient_array(top, bottom, width, height)
        return bg_cache[key]

    digit_h = height // 4
    # Stream raw frames straight into ffmpeg — no temp frame files, so hours-long
    # renders need no extra disk space.
    cmd = [
        video._ffmpeg_exe(), "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
        "-framerate", str(fps), "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-r", "24", "-c:a", "aac", "-b:a", "192k", "-shortest",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    n_frames = max(1, int(round(duration * fps)))
    last_key, frame_bytes = None, None
    try:
        for i in range(n_frames):
            remaining, seg_label = _remaining_at(segments, i / fps)
            key = (remaining, seg_label)
            if key != last_key:  # clock changes once per second; reuse otherwise
                glyphs = render_seven_segment(_fmt_mmss(remaining), digit_h)
                frame_bytes = _composite_centered(bg_for(seg_label),
                                                  glyphs).tobytes()
                last_key = key
            proc.stdin.write(frame_bytes)
    finally:
        proc.stdin.close()
        stderr = proc.stderr.read()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed: {stderr.decode(errors='replace')[-500:]}")
    return out_path
