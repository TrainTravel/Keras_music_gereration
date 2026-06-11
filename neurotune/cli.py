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
    parser.add_argument("--video", default=None,
                        help="also render an uploadable MP4 (gradient + audio); "
                             "requires imageio-ffmpeg")
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

    session = parser.add_argument_group("session mode (Pomodoro cowork video)")
    session.add_argument("--session", default=None,
                         help="render a WxBxN Pomodoro video, e.g. 25x5x4 "
                              "(25 min work + 5 min break, 4 rounds)")
    session.add_argument("--work-mood", default="steady_focus",
                         choices=sorted(PRESETS), help="mood during work segments")
    session.add_argument("--break-mood", default="deep_calm",
                         choices=sorted(PRESETS), help="mood during break segments")

    batch = parser.add_argument_group("batch mode (render a moods x seeds matrix)")
    batch.add_argument("--batch", action="store_true",
                       help="render many tracks at once into --outdir")
    batch.add_argument("--moods", default=None,
                       help="comma list of moods (default: all presets)")
    batch.add_argument("--seeds", default=None,
                       help="seed spec, e.g. '1-5' or '1,4,9' (required with --batch)")
    batch.add_argument("--outdir", default="uploads",
                       help="batch output directory (default: uploads)")
    batch.add_argument("--formats", default=None,
                       help="comma subset of midi,wav,mp4 (default: midi,wav)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_moods:
        for preset in PRESETS.values():
            print(f"{preset.name:14s} {preset.tempo_bpm:3d} BPM  {preset.description}")
        return 0

    if args.session:
        from . import session
        corpus = sorted(glob.glob(os.path.join(args.corpus, "*.mid")))
        out_path = args.out or f"session_{args.session}.mp4"
        session.render_session(
            args.session, out_path, work_mood=args.work_mood,
            break_mood=args.break_mood, seed=args.seed, corpus_paths=corpus,
        )
        print(f"wrote {out_path}: Pomodoro session {args.session} "
              f"(work={args.work_mood}, break={args.break_mood})")
        return 0

    if args.batch:
        from . import batch
        if not args.seeds:
            print("error: --batch requires --seeds (e.g. --seeds 1-5)", file=sys.stderr)
            return 2
        corpus = sorted(glob.glob(os.path.join(args.corpus, "*.mid")))
        batch.run_batch(
            moods=batch.parse_moods(args.moods),
            seeds=batch.parse_seeds(args.seeds),
            minutes=args.minutes,
            outdir=args.outdir,
            formats=batch.parse_formats(args.formats),
            corpus_paths=corpus,
        )
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

    wav_path = args.wav
    if args.video and not wav_path:
        wav_path = os.path.splitext(args.video)[0] + ".wav"
    if wav_path:
        from . import audio
        audio.synthesize(events, preset, wav_path, seed=args.seed)
        print(f"wrote {wav_path}: playable WAV ({preset.name})")
    if args.video:
        from . import video
        video.render_video(wav_path, preset, args.video)
        print(f"wrote {args.video}: uploadable MP4 ({preset.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
