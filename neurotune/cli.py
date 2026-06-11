"""Command line interface: python -m neurotune --mood steady_focus --minutes 5"""

import argparse
import dataclasses
import glob
import os
import sys

from . import generator, midi_io
from .presets import PRESETS
from .theory import build_scale, parse_note

DEFAULT_CORPUS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Samples")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="neurotune",
        description="Generate instrumental MIDI tuned for neurodivergent calm, "
                    "focus, or energy (see docs/SURVEY.md for the evidence base).")
    parser.add_argument("--mood", choices=sorted(PRESETS), default="steady_focus")
    parser.add_argument("--minutes", type=float, default=3.0,
                        help="approximate length of the piece (default: 3)")
    parser.add_argument("--out", default=None,
                        help="output .mid path (default: <mood>.mid)")
    parser.add_argument("--wav", default=None,
                        help="also render a playable WAV to this path "
                             "(offline synth, no soundfont needed)")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for reproducible output")
    parser.add_argument("--tempo", type=int, default=None,
                        help="override preset tempo (BPM) — personalization matters")
    parser.add_argument("--root", default=None,
                        help="override scale root, e.g. C3 or F#2")
    parser.add_argument("--engine", choices=["markov", "lstm"], default="markov",
                        help="melody engine (lstm requires tensorflow)")
    parser.add_argument("--corpus", default=DEFAULT_CORPUS,
                        help="directory of MIDI files to learn melodic style from")
    parser.add_argument("--list-moods", action="store_true",
                        help="describe available mood presets and exit")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_moods:
        for preset in PRESETS.values():
            print(f"{preset.name:14s} {preset.tempo_bpm:3d} BPM  {preset.description}")
        return 0

    preset = PRESETS[args.mood]
    overrides = {}
    if args.tempo:
        overrides["tempo_bpm"] = args.tempo
    if args.root:
        parse_note(args.root)  # validate early
        overrides["root"] = args.root
    if overrides:
        preset = dataclasses.replace(preset, **overrides)

    corpus = sorted(glob.glob(os.path.join(args.corpus, "*.mid")))
    out_path = args.out or f"{preset.name}.mid"

    if args.engine == "lstm":
        from . import lstm
        events = lstm.generate_events(preset, corpus, args.minutes, seed=args.seed)
    else:
        scale_pitches = build_scale(parse_note(preset.root), preset.scale,
                                    preset.octaves)
        model = generator.load_corpus_model(corpus, scale_pitches)
        events = generator.generate_piece(preset, model, args.minutes,
                                          seed=args.seed)

    midi_io.render(events, preset, out_path)
    print(f"wrote {out_path}: mood={preset.name}, {preset.tempo_bpm} BPM, "
          f"~{args.minutes:g} min, {len(events)} melody notes")

    if args.wav:
        from . import audio
        audio.synthesize(events, preset, args.wav, seed=args.seed)
        print(f"wrote {args.wav}: playable WAV ({preset.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
