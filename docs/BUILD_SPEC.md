# Build Spec: NeuroTune Content Pipeline (v1)

**Audience:** an autonomous Claude Code CLI session picking this up cold.
**Goal:** turn NeuroTune from "generates one track" into "produces a publish-ready
batch of body-doubling / focus videos with metadata," per `docs/CHANNEL_PLAN.md`.

Read this top to bottom, then execute milestones **M8 → M13 in order** (each builds
on the last). Every milestone has a Definition of Done; do not move on until its
tests pass. Commit after each milestone.

---

## 0. Quick orientation

This is a Python project (3.11). The package is `neurotune/`. There are **no
subcommands** — the CLI is flat argparse in `neurotune/cli.py`, run as
`python -m neurotune ...`. Tests are pytest in `tests/`, run with `python -m pytest -q`.

Existing modules (read these first — reuse, don't reinvent):

| File | What it gives you |
|---|---|
| `neurotune/theory.py` | scales, `parse_note`, `build_scale`, `snap_to_scale` |
| `neurotune/presets.py` | `PRESETS` dict + `MoodPreset` dataclass (deep_calm, calm_focus, steady_focus, energize) |
| `neurotune/generator.py` | `load_corpus_model`, `generate_piece(preset, model, minutes, seed)` → list of `(pitch, start_beat, dur_beat, velocity)` |
| `neurotune/midi_io.py` | `render(events, preset, path)`, plus `drone_events`/`percussion_events` |
| `neurotune/audio.py` | `synthesize(events, preset, path, sample_rate, seed)` → mono 16-bit WAV; `SAMPLE_RATE` |
| `neurotune/video.py` | `render_video(wav, preset, mp4, width, height)`; `_ffmpeg_exe()`, `_write_gradient_ppm`, `_PALETTES`, `_wav_seconds` |
| `neurotune/cli.py` | `build_parser()`, `main(argv)`; flags: `--mood --minutes --out --wav --video --seed --tempo --root --engine --corpus --list-moods` |
| `neurotune/lstm.py` | optional tf.keras engine (don't touch unless a milestone says so) |

Docs context: `docs/SURVEY.md` (evidence), `docs/CHANNEL_PLAN.md` (the channel),
`docs/YOUTUBE.md` (publishing reality), `docs/PLAN.md` (milestone log).

**Current test count: 22 passing.** Keep it green at every step.

---

## 1. Guardrails (apply to ALL milestones)

- **Branch:** develop and push to `claude/music-neurodivergent-focus-52yj71`. Do
  not open a PR unless the human asks.
- **Dependencies:** core path needs only `mido` + `numpy`. `imageio-ffmpeg` is
  optional (video), `tensorflow` is optional (lstm). Never add a hard dependency
  to the core path. New optional deps go in `requirements.txt` commented as optional.
- **No network at runtime or in tests.** ffmpeg is the bundled `imageio-ffmpeg`
  binary via `video._ffmpeg_exe()`. Tests that need it use
  `pytest.importorskip("imageio_ffmpeg")` (see `tests/test_video.py`).
- **No PIL.** Generate images as PPM (`P6`) with numpy; convert to JPG/PNG by
  shelling out to the bundled ffmpeg if a raster format is needed.
- **Determinism:** everything seedable must be reproducible — same `--seed` ⇒
  byte-identical MIDI/WAV (video/mp4 need not be byte-identical, but duration must
  match).
- **Artifacts are gitignored.** `Generated/*.wav|*.mp4`, `uploads/` already ignored;
  extend `.gitignore` for any new artifact dirs (`thumbnails/`, `*.ppm`, `*.json`
  render outputs). Never commit large media.
- **No medical claims in any generated copy.** Titles/descriptions say "focus /
  cowork / calm / companion," never "treats/cures ADHD or autism." A disclaimer
  line is mandatory in generated descriptions (see M11).
- **Style:** match existing code — small modules, argparse, type hints, docstrings
  that cite the survey where a parameter is evidence-driven. Add pytest tests for
  every new module.

---

## 2. Milestones

### M8 — Batch renderer
**Goal:** render a whole content matrix (moods × seeds) in one command.

**Files:** new `neurotune/batch.py`; extend `cli.py`.

**CLI contract** (add to existing parser, mutually exclusive group with single-file mode):
```
python -m neurotune --batch \
    --moods steady_focus,deep_calm --seeds 1-5 --minutes 60 \
    --outdir uploads --formats midi,wav,mp4
```
- `--batch` flag switches to batch mode.
- `--moods` comma list (default: all presets). `--seeds` accepts `1-5` ranges
  and/or comma lists (`1,4,9`). `--formats` subset of `midi,wav,mp4` (default
  `midi,wav`). `--outdir` default `uploads`.
- Produces `<outdir>/<mood>_seed<NN>.{mid,wav,mp4}` for the cartesian product.
- Writes `<outdir>/manifest.json`: array of `{mood, seed, minutes, files:{...},
  tempo_bpm}` records. Deterministic ordering (sorted mood, then seed).

**Implementation notes:** loop calling existing `generate_piece` → `render` →
`synthesize` → `render_video`. Build the corpus model **once per mood** (not per
seed). Print a one-line progress per job. Reuse `cli`'s corpus discovery.

**Acceptance / tests (`tests/test_batch.py`):**
- `parse_seeds("1-3,7") == [1,2,3,7]`.
- batch run with 2 moods × 2 seeds, `--minutes 0.2`, formats `midi,wav` creates 8
  files + a valid `manifest.json` with 4 records.
- manifest is valid JSON and records match files on disk.

**DoD:** new tests pass; full suite green; `requirements.txt`/README note the flag.

---

### M9 — Countdown timer overlay (pure-numpy glyphs)
**Goal:** a moving MM:SS countdown burned into video — the core of cowork/Pomodoro
content. No font files.

**Files:** new `neurotune/timer.py`.

**Public API:**
```python
render_seven_segment(text: str, height: int) -> np.ndarray   # (h, w, 3) uint8, transparent->use mask
draw_timer_frame(bg: np.ndarray, seconds_left: int, label: str|None) -> np.ndarray
render_timer_video(wav_path, preset, out_path, *, fps=10, count_from=None,
                   label=None, width=1280, height=720) -> str
```
- Implement digits 0–9 and `:` as a **7-segment bitmap** drawn with numpy array
  slicing (each segment is a filled rectangle). No external font.
- `render_timer_video` builds a per-mood gradient background (reuse
  `video._write_gradient_ppm` logic / `_PALETTES`), overlays a countdown that
  decreases once per second from `count_from` (default = audio duration), writes a
  **PPM frame sequence** to a temp dir, and muxes with the WAV via ffmpeg
  (`-framerate {fps} -i frame_%05d.ppm -i wav ... -pix_fmt yuv420p`).
- Keep visuals gentle (survey §3.4 / accessibility): soft contrast, no flashing,
  digits centered, small label above (e.g. "FOCUS" / "BREAK").

**Acceptance / tests (`tests/test_timer.py`, `importorskip imageio_ffmpeg`):**
- `render_seven_segment("12:34", 80)` returns an array with non-zero "lit" pixels
  and correct aspect.
- a 6-second, fps=10 timer video at 160×90 exists, has `ftyp` signature, duration
  ≈ audio length ±1s, and **has >1 distinct frame** (decode 2 frames via ffmpeg,
  assert they differ) — proves it isn't a still image.

**DoD:** tests pass; suite green.

---

### M10 — Pomodoro focus sessions (evergreen long-form)
**Goal:** compose M9 + the audio engine into structured work/break sessions — the
always-on content from the channel plan ("Cowork With Me", focus timers).

**Files:** new `neurotune/session.py`; extend `cli.py`.

**CLI contract:**
```
python -m neurotune --session 25x5x4 --work-mood steady_focus \
    --break-mood deep_calm --out uploads/cowork_01.mp4 --seed 7
```
- `--session WxBxN` = N rounds of W min work + B min break (e.g. `25x5x4` =
  classic Pomodoro, ~2h). Validate the format.
- Generate the **work** audio with `--work-mood` and **break** audio with
  `--break-mood`, concatenate the WAV segments in order, and render one timer video
  where the countdown resets each segment and the label switches FOCUS/BREAK.
- The countdown counts **down within each segment** (not the whole video).

**Implementation notes:** synthesize each segment to a numpy buffer, concatenate,
write one WAV, then drive `timer.render_timer_video` with a **segment schedule**
(list of `(label, seconds)`), so add a `segments=` param to the timer renderer
(or a thin wrapper). Reuse, don't fork, M9.

**Acceptance / tests (`tests/test_session.py`):**
- `parse_session("25x5x4") == (25,5,4)`; bad input raises.
- a tiny session `1x1x2` (use `--minutes`-scale override or accept fractional for
  tests) builds an mp4 whose duration ≈ total segment seconds ±1s and whose label
  track changes at least once.

**DoD:** tests pass; suite green; README documents `--session`.

---

### M11 — Metadata + thumbnail generator
**Goal:** publish-ready sidecar files so uploading is copy-paste.

**Files:** new `neurotune/metadata.py`; wire into batch (M8) and session (M10) so
each video gets a sibling `.meta.json` + `.thumb.jpg`.

**Public API:**
```python
build_metadata(*, mood, pillar, minutes, seed, segments=None) -> dict
write_metadata(meta: dict, path: str) -> None        # json
render_thumbnail(mood, title_line, out_path) -> str  # gradient PPM -> jpg via ffmpeg
```
- `meta` contains: `title` (≤100 chars), `description` (multi-line, ends with the
  **mandatory disclaimer**: *"Background focus/companion music. Not medical advice
  or treatment for any condition."*), `tags` (list, total ≤450 chars), `chapters`
  (list of `{time, label}` — for sessions, one per work/break segment), and
  `category` ("Music"). Title templates per pillar/mood, e.g.
  `"Steady Focus — 1 Hour Body Doubling Study Session (Lo-Fi)"`.
- `render_thumbnail`: per-mood gradient + large title text (reuse the M9 glyph
  renderer or a simple block-letter approach) → PPM → `ffmpeg -i in.ppm out.jpg`.

**Acceptance / tests (`tests/test_metadata.py`):**
- title ≤100 chars; tags total ≤450; description contains the exact disclaimer
  substring; no banned phrases (assert none of "treat","cure","clinically proven"
  appear, case-insensitive).
- `build_metadata` is deterministic for fixed inputs.
- thumbnail test (`importorskip imageio_ffmpeg`): jpg exists, starts with JPEG
  magic bytes `FF D8`.

**DoD:** tests pass; batch & session runs now emit `.meta.json` + `.thumb.jpg`;
suite green.

---

### M12 — Content calendar generator
**Goal:** turn `docs/CHANNEL_PLAN.md` cadence into an executable schedule.

**Files:** new `neurotune/calendar_plan.py`; CLI `python -m neurotune.calendar_plan`.

**CLI contract:**
```
python -m neurotune.calendar_plan --weeks 4 --start 2026-07-01 --out schedule.csv
```
- Encodes the "survivable cadence": 1 daily anchor cowork + 2–3 long-form/week
  across pillars (Cowork, Meal, Build, Play, GRWM, Reset — pillars listed in
  CHANNEL_PLAN). Round-robin pillars across the week.
- Output CSV columns: `date, pillar, working_title, render_command` where
  `render_command` is a **runnable** `python -m neurotune ...` line that would
  produce that day's asset.

**Acceptance / tests (`tests/test_calendar.py`):**
- 4 weeks ⇒ 28 daily rows; every row has a non-empty pillar and a command that
  starts with `python -m neurotune`; dates are consecutive from `--start`.

**DoD:** tests pass; suite green.

---

### M13 — CI + docs + milestone log
**Goal:** lock it all in.

**Tasks:**
- Add `.github/workflows/ci.yml`: on push/PR, set up Python 3.11, `pip install
  mido numpy pytest`, run `python -m pytest -q`. (ffmpeg/tf tests self-skip via
  `importorskip`, so CI stays light and offline.)
- Update `README.md`: document `--batch`, `--session`, the calendar tool, and the
  `uploads/` workflow; link this spec.
- Update `docs/PLAN.md`: mark M7 done where applicable and append M8–M13 to the
  milestone list with status.
- Final: `python -m pytest -q` green, commit, push.

**DoD:** CI workflow present and passing locally; docs updated; suite green.

---

## 3. Execution order & dependencies

```
M8 (batch) ─┐
M9 (timer) ─┴─► M10 (session) ─► M11 (metadata, wires into M8+M10)
M12 (calendar)  ── independent, can run any time after M8
M13 (CI/docs)   ── last
```

Recommended commit cadence: one commit per milestone, message
`"M8: batch renderer"` etc., body summarizing files + tests, ending with the
session URL footer used elsewhere in this repo's history. Push after each.

## 4. Definition of Done (whole spec)

- [ ] M8–M13 complete, each with passing tests.
- [ ] `python -m pytest -q` green (≥ 22 + new tests).
- [ ] Core path still installs with only `mido` + `numpy`.
- [ ] No medical claims anywhere in generated copy; disclaimer present in all
      generated descriptions.
- [ ] No committed media artifacts; `.gitignore` covers new outputs.
- [ ] README + PLAN updated; CI workflow added and green.
- [ ] All work pushed to `claude/music-neurodivergent-focus-52yj71`.

## 5. If you get stuck / ambiguity

Prefer the simplest thing that satisfies the acceptance test. If a milestone's
approach is genuinely blocked (e.g. ffmpeg unavailable in the environment), still
ship the pure-Python parts and mark the media test with `importorskip`, then note
the gap in the commit body — do not silently skip a milestone.
