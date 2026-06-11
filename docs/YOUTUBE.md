# Launching a focus-music YouTube channel with NeuroTune

This is the realistic, honest version. NeuroTune can mass-produce the *content*
(long-form audio + video). It cannot create the channel, log into your Google
account, or "switch on" revenue — YouTube controls monetization and you have to
qualify for and enable it yourself. Below is the part software can do, and the
part only you can.

## What this repo gives you

Generate an uploadable video in one command:

```bash
# a 1-hour steady-focus video, 720p gradient + audio, ready to upload
python -m neurotune --mood steady_focus --minutes 60 --seed 7 \
    --out tracks/focus_07.mid --video uploads/focus_07.mp4
```

Batch a week of unique videos by varying `--seed` (and `--mood`, `--tempo`,
`--root`). Each seed is a different, reproducible track.

## What only you can do

1. **Create the channel** in your own YouTube/Google account.
2. **Apply to the YouTube Partner Program.** As of 2025 the bar is 1,000
   subscribers plus 4,000 valid public watch hours in 12 months (or 10M Shorts
   views), then AdSense review. Verify current thresholds on YouTube's own help
   pages — they change.
3. **Enable monetization** once accepted. There is no API or script that skips
   this; it is a manual, policy-gated step.

## Content & rights checklist

- **Originality / copyright:** melodies here are generated, but they are *trained
  on* the MIDI in `Samples/` (e.g. a Pokémon cover). Train on music you have the
  rights to before publishing, or the output may carry recognizable material and
  draw Content ID claims. Swap in public-domain or your own MIDI for the corpus.
- **Health claims — important:** do **not** market videos as treatment or as
  clinically proven to help ADHD/autism. The evidence (see `docs/SURVEY.md`) is
  supportive, not a medical claim, and platforms penalize health misinformation.
  Safe framing: "calm/focus background music," "instrumental study music."
- **Accessibility (on-brand for this project):** keep dynamics gentle, avoid
  flashing visuals, write clear descriptions.

## Suggested workflow

1. Replace the training corpus with rights-clear MIDI.
2. Batch-render 10–20 long videos across moods/seeds into `uploads/`.
3. Title plainly (e.g. "Steady Focus — 1 Hour Lo-Fi Study Music"), add a
   description that links the mood to its use case, no medical claims.
4. Upload, build watch time, then apply to the Partner Program.

A `make_batch` helper or thumbnail generator can be added next if you want — ask.
