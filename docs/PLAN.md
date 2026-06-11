# Project Plan: NeuroTune — evidence-based focus/calm music generation

Goal: turn this LSTM music-generation experiment into a usable tool that generates
instrumental MIDI tracks tuned to what the research says helps autistic and ADHD
listeners calm down, focus, or lift their energy (see `docs/SURVEY.md`).

## Architecture

```
neurotune/
  theory.py      # scales, note-name parsing, snapping pitches to scale
  presets.py     # MoodPreset dataclass + 4 evidence-based presets
  midi_io.py     # corpus note extraction, multi-track MIDI rendering
  generator.py   # order-1 Markov melody model + phrase/form assembly
  lstm.py        # optional modernized tf.keras LSTM engine (original notebook, updated)
  cli.py         # argparse CLI (python -m neurotune)
tests/           # pytest suite
Generated/       # committed example outputs, one per mood
```

Two engines share one renderer:

- **markov** (default): order-1 Markov chain over scale degrees, learned from the MIDI
  corpus in `Samples/`, sampled with low temperature and a leap cap so output stays
  predictable. No heavy dependencies, deterministic with `--seed`, instant.
- **lstm** (optional): the original notebook's approach modernized to tf.keras,
  with predictions snapped to the preset's scale before rendering.

Predictability (the key active ingredient from the survey) is enforced structurally:
generate a 4-bar phrase, then lay phrases out in AABA form so 75% of the piece is
literal repetition; melody, drone and percussion all follow the preset's narrow
velocity band.

## Milestones

- [x] **M1 — Research survey** (`docs/SURVEY.md`): PubMed + web evidence, design mapping
- [x] **M2 — Plan & architecture** (this file)
- [x] **M3 — Core engine**: theory, presets, Markov generator, MIDI renderer
- [x] **M4 — CLI + example outputs**: `python -m neurotune --mood steady_focus --minutes 5`
- [x] **M5 — Tests**: determinism, scale conformance, leap cap, MIDI round-trip
- [x] **M6 — Optional LSTM engine + docs**: modernized Keras path, README rewrite
- [ ] **M7 (future)**: audio rendering (soundfont), more corpus MIDI, adaptive
      session lengths, user feedback loop for per-person preset tuning

## Presets (from survey §4)

| Preset | Use case | Tempo | Character |
|---|---|---|---|
| `deep_calm` | wind-down, sensory overload recovery | 54 BPM | low register, drone, long notes, very sparse |
| `calm_focus` | anxious-but-need-to-work | 66 BPM | gentle pulse, mid register, pentatonic |
| `steady_focus` | default ADHD work mode | 76 BPM | lo-fi-style steady percussion, repetitive |
| `energize` | task initiation / mood lift | 104 BPM | brighter major key, denser, still no surprises |
