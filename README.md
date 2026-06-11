# NeuroTune — music generation for neurodivergent calm, focus & energy

Generates instrumental MIDI tracks whose musical parameters (tempo, repetition,
dynamics, consonance, texture) follow what published research says helps
**autistic and ADHD listeners** calm down, sustain focus, or lift their energy.

- **The evidence base:** [docs/SURVEY.md](docs/SURVEY.md) — a survey of PubMed-indexed
  studies and practitioner sources, with every finding mapped to a generator parameter.
- **The plan & milestones:** [docs/PLAN.md](docs/PLAN.md)

This grew out of the original *Music generation with Keras and LSTM* experiment
([notebook](Music%20gerenation%20with%20Keras%20and%20TF.ipynb)), which survives as the
optional `lstm` engine, modernized to tf.keras.

## Quick start

```bash
pip install mido numpy           # the default engine + WAV synth need nothing else
python -m neurotune --list-moods
python -m neurotune --mood steady_focus --minutes 5 --seed 42 --out focus.mid

# also render a playable WAV (offline synth, no soundfont required):
python -m neurotune --mood deep_calm --minutes 10 --wav calm.wav

# render an uploadable MP4 (gradient + audio); needs `pip install imageio-ffmpeg`:
python -m neurotune --mood steady_focus --minutes 60 --video focus.mp4
```

Want to publish? See [docs/YOUTUBE.md](docs/YOUTUBE.md) for a channel-launch
guide, and [docs/CHANNEL_PLAN.md](docs/CHANNEL_PLAN.md) for *Present* — a
body-doubling channel concept (cowork / meal-companion / build-with-me /
get-ready-with-me) that uses NeuroTune for its background beds.

## Moods

| Preset | Use case | Tempo |
|---|---|---|
| `deep_calm` | wind-down, recovery from sensory overload | 54 BPM |
| `calm_focus` | anxious-but-need-to-work | 66 BPM |
| `steady_focus` | default ADHD work mode (lo-fi-style pulse) | 76 BPM |
| `energize` | task initiation, mood lift | 104 BPM |

Research is unanimous that individual variation is large, so everything is
overridable: `--tempo 70 --root E3 --minutes 25` (a pomodoro), etc.
Pre-rendered 3-minute examples for each mood are in [`Generated/`](Generated/).

## How the evidence shapes the music

- **Predictability** (reduces anxiety driven by intolerance of uncertainty in autism):
  AABA form with literal phrase repetition, low-temperature Markov sampling, capped
  melodic leaps.
- **Steady moderate stimulation** (supports ADHD attention): constant soft kick/hat
  pulse in the focus presets, 60–80 BPM.
- **Narrow dynamics & consonance** (sensory sensitivity): velocities confined to a
  small band; all pitches snapped to pentatonic/diatonic scales; sustained drone pad
  as a constant texture.
- **No lyrics**: purely instrumental.

## Engines

- `--engine markov` (default): order-1 Markov chain over scale degrees, learned from
  the MIDI corpus in `Samples/`. Deterministic with `--seed`, instant, no heavy deps.
- `--engine lstm`: trains the modernized Keras LSTM on the corpus first
  (requires `tensorflow`); predictions are snapped to the preset's scale.

## Development

```bash
pip install -r requirements.txt
python -m pytest tests/
```

*This project generates supportive listening material and makes no clinical claims —
see the limitations section of the survey.*
