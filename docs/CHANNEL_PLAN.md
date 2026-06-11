# Channel Plan: "Present" — digital body-doubling for ADHD & autistic brains

A YouTube channel built on one idea: **parallel presence**. Not tutorials, not
entertainment you watch *instead* of working — company you keep *while* you live.
Someone is here, quietly doing their thing, so you can do yours. Eat together.
Work together. Get ready together. The cure for "I can't start" and for the
loneliness of the digital age is the same thing: another human in the room.

This is the human-facing companion to the `neurotune` audio engine in this repo —
NeuroTune generates the calm/focus background beds (see `docs/SURVEY.md`), the
channel provides the *person*.

## Why this works (it's not just vibes)

Body doubling — doing a task alongside another present person who isn't helping —
is a core, coach-recommended ADHD strategy, coined by ADHD coach Linda Anderson
in the mid-1990s. The mechanisms are well documented:

- **Social facilitation** — we attend and perform better when someone is present.
- **Externalized executive function** — another person's presence becomes an
  external anchor and light accountability, outsourcing the "just start" hurdle
  that ADHD makes hard.
- **Dopamine / mild social stimulation** — social presence engages reward
  circuitry, which ADHD brains under-stimulate on their own.
- **Reduced isolation** — it directly answers loneliness, which is the emotional
  half of the problem.

Sources: [Athenify](https://athenify.io/blog/body-doubling-study-technique),
[The Mindful Adult ADHD Clinic](https://themindfuladult.ca/body-doubling-adhd/),
[Rational Growth](https://rational-growth.com/body-doubling-virtual-coworking-how-working-alongside-others-online-boosts-adhd-2/),
[Pledgd](https://www.pledgd.com/blog/body-doubling-apps).
Demand is proven: "ASMR for ADHD" and "body doubling work with me" videos already
pull large audiences on YouTube — the lane is real, but most are either pure ASMR
*or* pure coworking. The opening is a **warm, neurodivergent-first brand that does
both, across daily-life activities, not just studying.**

## Brand

- **Working name:** *Present* (alt: *In The Room*, *Alongside*, *Same Boat*).
- **Promise:** "You're not doing it alone." Low-pressure, no toxic productivity,
  explicitly ADHD/autistic-friendly (predictable structure, gentle audio,
  no flashing, captions always).
- **Host persona:** calm, real, a little unpolished on purpose — parasocial
  warmth comes from authenticity, not production gloss.

## Content pillars (your ideas, organized)

| Pillar | Format | Body-double job it does | Length |
|---|---|---|---|
| **Cowork With Me** | Real-time work/study sessions w/ Pomodoro timers, NeuroTune beds, soft check-ins at breaks | Task initiation + sustained focus | 25, 50, 90 min + live |
| **Meal Companion** | Eating together — breakfast/lunch/dinner, gentle ASMR (no aggressive chewing), light or no talking | Counters eating alone; routine anchor for skipped meals (common w/ ADHD) | 15–30 min |
| **Build With Me (AI apps)** | Calm "code-along presence" — building small AI apps in real time, narrating lightly or silent-with-captions | Coworking for makers; niche, high-retention, monetizable | 45–90 min |
| **Play Quietly With Me** | Low-stakes, cozy gameplay (farming/sims/exploration), relaxed commentary | Companionship + downtime that isn't doom-scrolling | 30–60 min |
| **Get Ready With Me** | Hair, skincare, tidying, morning/evening routines | Routine modeling + "getting started on yourself"; warm, intimate | 10–25 min |
| **Reset With Me** | Wind-down, tidy-one-thing, body-double for chores/dishes | Sensory recovery + executive nudge for avoided tasks | 10–20 min |

Every video shares the same scaffolding so it's predictable (autistic-friendly):
soft cold open → "what we're doing this session" → the activity → gentle close.

## Signature recurring series

- **"Same Time Tomorrow"** — a daily 8am cowork that people build a habit around.
- **"Dinner for One (but not really)"** — nightly meal companion.
- **"Ship Something Small"** — weekly Build-With-Me where one tiny AI app gets
  finished on camera (pairs naturally with this very repo).
- **"Sunday Reset"** — chores/hair/routine combo for the week ahead.
- **Monthly 3–4 hr live cowork marathons** with chat as the accountability layer.

## How NeuroTune plugs in

- Background music beds for every video, generated per mood:
  `python -m neurotune --mood steady_focus --minutes 60 --wav bed.wav`
  (`deep_calm` for meals/reset, `steady_focus` for cowork, `energize` for GRWM).
- Intro/outro stings from short generated phrases.
- Eventually: branded "focus timer" videos (pure NeuroTune + countdown) as
  always-on, evergreen long-form content between hosted uploads.

## 30-day launch sprint

1. **Week 1 — identity:** pick name, make channel, banner/avatar, 3 NeuroTune
   beds, write the "no medical claims" + community guidelines.
2. **Week 2 — pilot 5:** one of each top pillar (Cowork, Meal, Build, GRWM, Play).
   Keep it cheap: one camera/screen capture, a mic, good light.
3. **Week 3 — publish + schedule:** release 3, set a fixed cadence
   (e.g. daily Cowork short-form + 2 long-form/week). Consistency > polish.
4. **Week 4 — go live once:** a real-time cowork or build stream; turn the best
   moments into clips. Start a Discord for off-platform body-doubling.

## Cadence that's survivable

Pick ONE daily anchor (the 8am cowork — can be a static/looping NeuroTune timer on
low-energy days) plus **2–3 hosted long-forms per week**. Batch-film GRWM/Meal in
one session. Repurpose every long-form into Shorts (the "I can't start" hook + a
30-sec body-double clip travels well).

## Ethics & accessibility (non-negotiable, on-brand)

- **No medical claims.** "Focus/cowork/companion content," never "treats ADHD."
  See `docs/SURVEY.md` limitations.
- **ASMR & eating done kindly:** gentle triggers, no fetishization, no extreme
  mukbang; model a *normal* meal — many viewers struggle with eating.
- **Accessibility:** captions on everything, no strobing/flashing, gentle dynamics
  (the audio engine already enforces narrow dynamics), content warnings where due.
- **Parasocial care:** be warm but honest that it's a one-to-many relationship;
  point people toward real human body-doubling (Discord, Focusmate) too.
- **Privacy/rights:** game capture and music must be license-clear (see
  `docs/YOUTUBE.md`); use rights-clear MIDI for NeuroTune beds.

## Monetization (the realistic part)

Same gate as any channel — you must reach YouTube's Partner Program thresholds
(~1,000 subs + 4,000 watch hours) and pass review; nothing skips that. But this
format monetizes unusually well *beyond* ads because it builds routine and
community: **memberships** (members-only live coworks), **Discord/Patreon** body-
doubling rooms, and eventually a NeuroTune-powered focus app. The channel is the
funnel; the community and tools are the business. Details in `docs/YOUTUBE.md`.
