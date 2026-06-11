"""M8 — batch renderer: render a moods x seeds matrix to an uploads/ directory.

Drives the existing single-track pipeline (generate_piece -> render -> synthesize
-> render_video) across a cartesian product of moods and seeds, and writes a
manifest.json describing every produced asset. The corpus model is built once per
mood, not per seed.
"""

import json
import os

from . import generator, midi_io
from .presets import PRESETS
from .theory import build_scale, parse_note

VALID_FORMATS = ("midi", "wav", "mp4")


def parse_seeds(spec: str) -> list[int]:
    """Parse a seed spec like '1-3,7,10-11' into a sorted unique list [1,2,3,7,10,11]."""
    seeds: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo, hi = int(lo), int(hi)
            if hi < lo:
                raise ValueError(f"descending seed range: {part!r}")
            seeds.update(range(lo, hi + 1))
        else:
            seeds.add(int(part))
    if not seeds:
        raise ValueError(f"no seeds parsed from {spec!r}")
    return sorted(seeds)


def parse_moods(spec: str | None) -> list[str]:
    if not spec:
        return sorted(PRESETS)
    moods = [m.strip() for m in spec.split(",") if m.strip()]
    unknown = [m for m in moods if m not in PRESETS]
    if unknown:
        raise ValueError(f"unknown moods: {', '.join(unknown)}")
    return moods


def parse_formats(spec: str | None) -> list[str]:
    if not spec:
        return ["midi", "wav"]
    fmts = [f.strip() for f in spec.split(",") if f.strip()]
    unknown = [f for f in fmts if f not in VALID_FORMATS]
    if unknown:
        raise ValueError(f"unknown formats: {', '.join(unknown)} "
                         f"(choose from {', '.join(VALID_FORMATS)})")
    return fmts


def run_batch(moods, seeds, minutes, outdir, formats, corpus_paths,
              progress=print) -> dict:
    """Render the moods x seeds matrix; return the manifest dict (also written to disk)."""
    from . import audio, video  # local imports keep optional deps lazy

    os.makedirs(outdir, exist_ok=True)
    records = []

    for mood in moods:
        preset = PRESETS[mood]
        scale = build_scale(parse_note(preset.root), preset.scale, preset.octaves)
        model = generator.load_corpus_model(corpus_paths, scale)  # once per mood

        for seed in seeds:
            stem = f"{mood}_seed{seed:02d}"
            base = os.path.join(outdir, stem)
            events = generator.generate_piece(preset, model, minutes, seed=seed)

            files = {}
            # WAV is needed as the audio source whenever MIDI-less video is requested.
            wav_path = f"{base}.wav"
            if "midi" in formats:
                midi_io.render(events, preset, f"{base}.mid")
                files["midi"] = f"{base}.mid"
            if "wav" in formats or "mp4" in formats:
                audio.synthesize(events, preset, wav_path, seed=seed)
                if "wav" in formats:
                    files["wav"] = wav_path
            if "mp4" in formats:
                video.render_video(wav_path, preset, f"{base}.mp4")
                files["mp4"] = f"{base}.mp4"
                if "wav" not in formats and os.path.exists(wav_path):
                    os.remove(wav_path)  # was only a render intermediate

            records.append({
                "mood": mood,
                "seed": seed,
                "minutes": minutes,
                "tempo_bpm": preset.tempo_bpm,
                "files": files,
            })
            progress(f"  rendered {stem}: {', '.join(files) or 'nothing'}")

    manifest = {"count": len(records), "minutes": minutes, "items": records}
    manifest_path = os.path.join(outdir, "manifest.json")
    with open(manifest_path, "w") as fh:
        json.dump(manifest, fh, indent=2)
    progress(f"wrote {manifest_path}: {len(records)} items")
    return manifest
