"""Render a generated track into an uploadable YouTube video (audio + still image).

Focus/ambient channels publish long static-visual videos, so this loops a soft
per-mood gradient under the WAV and muxes them into an H.264 MP4. ffmpeg is
provided by the optional `imageio-ffmpeg` package — no system install needed.
"""

import os
import subprocess
import tempfile
import wave

import numpy as np

from .presets import MoodPreset

# Calm, low-saturation gradient palette per mood (top RGB, bottom RGB).
_PALETTES = {
    "deep_calm":    ((18, 22, 40), (40, 30, 60)),
    "calm_focus":   ((20, 34, 44), (32, 60, 70)),
    "steady_focus": ((26, 26, 36), (60, 48, 70)),
    "energize":     ((30, 28, 50), (90, 60, 70)),
}


def _ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _wav_seconds(wav_path: str) -> float:
    with wave.open(wav_path, "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def _write_gradient_ppm(preset: MoodPreset, path: str, width=1280, height=720):
    top, bottom = _PALETTES.get(preset.name, ((20, 24, 40), (50, 40, 64)))
    ramp = np.linspace(0.0, 1.0, height, dtype="float32")[:, None]
    rgb = np.empty((height, width, 3), dtype="float32")
    for c in range(3):
        rgb[:, :, c] = (top[c] * (1 - ramp) + bottom[c] * ramp)
    # faint centre vignette glow so it isn't a flat field
    yy, xx = np.mgrid[0:height, 0:width].astype("float32")
    glow = np.exp(-(((xx - width / 2) / (width * 0.6)) ** 2
                    + ((yy - height / 2) / (height * 0.6)) ** 2))
    rgb += glow[:, :, None] * 14.0
    frame = np.clip(rgb, 0, 255).astype("uint8")
    with open(path, "wb") as fh:
        fh.write(f"P6\n{width} {height}\n255\n".encode())
        fh.write(frame.tobytes())


def render_video(wav_path: str, preset: MoodPreset, out_path: str,
                 width: int = 1280, height: int = 720) -> str:
    """Mux `wav_path` with a looping per-mood gradient into an MP4 at `out_path`."""
    duration = _wav_seconds(wav_path)
    with tempfile.TemporaryDirectory() as tmp:
        ppm = os.path.join(tmp, "bg.ppm")
        _write_gradient_ppm(preset, ppm, width, height)
        cmd = [
            _ffmpeg_exe(), "-y",
            "-loop", "1", "-framerate", "2", "-i", ppm,
            "-i", wav_path,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-r", "24", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-t", f"{duration:.3f}",
            out_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    return out_path
