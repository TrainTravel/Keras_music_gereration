# Production Guide: making great body-doubling videos (with scripts)

A practical companion to `docs/CHANNEL_PLAN.md`: what's already out there, the
quality tips that actually move retention, ready-to-fill **script templates** for
each content pillar, and the **workflow + skills** to use when building this with
Claude.

---

## 1. What's already out there (so you can be different)

**Live body-doubling platforms** — the paid, real-time end of the market:
- **[Focusmate](https://www.focusmate.com/)** — 1:1 matching, 25/50/75-min timed
  sessions: greet → declare goal → work silently → check in. Free (3/wk) or ~$8/mo.
- **[Flow Club](https://flown.com/blog/deep-work/virtual-coworking-focusmate-review)** —
  host-led check-in/check-out turning "I should" into "done."
- **Caveday** — facilitator-led 1–3 hr deep-work sprints + a 24/7 Focus Lounge.
- **Study Together / Study Spaces** — live focus rooms plus a "study OS"
  (Pomodoro, tasks, streaks).

**YouTube "Study/Work With Me"** — the free, async, parasocial end:
aesthetic desk, on-screen Pomodoro timer, ambient layer (rain, café, keyboard),
soft or no talking. **Tooling creators use:** OBS + a
[Pomodoro Lua timer](https://obsproject.com/forum/resources/pomodoro-pro-timer-for-obs.1859/),
task-list widgets, ambient mixers.

**The gap NeuroTune fills:** most are *either* live-and-paid *or* study-only async
video. Few are **neurodivergent-first across daily life** (meals, build-with-me,
get-ready, chores) with **generated, rights-clean audio beds** and accessibility
baked in. That's your wedge.

Sources: [Flexclip](https://www.flexclip.com/learn/study-with-me-video.html),
[YouTube Creators](https://www.youtube.com/creators/how-things-work/content-creation-strategy/),
[Coworking Streamers Guide](https://coworking-stream-guide.com/guide/general-tips),
[FLOWN body-doubling apps](https://flown.com/blog/adhd/best-body-doubling-apps),
[Evolving Digital](https://evolving-digital.com/resources/build-a-successful-youtube-channel/).

---

## 2. Ten quality tips that move the needle

1. **Win the first 15 seconds.** Most quitters leave in <15s. Open with the
   *payoff* ("Let's get the thing you've been avoiding done together — 25 minutes,
   I'm right here"), a small visual change in the first 3–4s, and a promise of
   exactly what the session is.
2. **An on-screen timer is non-negotiable.** It's the single most-requested
   feature of the genre. NeuroTune renders one for you (`--session`).
3. **Pick one repeatable aesthetic.** Consistent desk/lighting/color = a brand
   viewers recognize in the feed. Warm, dim, low-contrast suits the calm promise.
4. **Layer ambience under the music**, low. Rain, distant café, soft keyboard.
   Keep it *predictable* and quiet (survey §3) — it should disappear, not grab.
5. **Decide your mic strategy and state it.** Either mute during focus blocks
   (most coworking streamers do) *or* leave a gentle keyboard/ASMR layer. Tell
   viewers which, so silence never feels like a malfunction.
6. **Design the breaks.** Breaks are where personality lives: a stretch, a sip,
   one affirmation, a breath. Keep them short and same-shaped every time.
7. **Consistency beats volume.** One reliable session at a fixed time outperforms
   sporadic uploads — the whole point is a *routine viewers can set a clock by*.
8. **Caption everything, never flash.** On-brand accessibility and it widens reach.
9. **Make the thumbnail/title do one job.** Plain and honest:
   "Steady Focus — 1 Hour Body Doubling (Lo-Fi, Timer)". No clickbait, no claims.
10. **Reply in comments early.** The genre runs on *felt presence*; a few real
    replies in the first hour convert watchers into a returning community.

---

## 3. Script templates (fill in the brackets)

> **Full shootable episode scripts now live in [`docs/scripts/`](scripts/)** —
> word-for-word lines, timing, cues, alt takes, and the exact NeuroTune command
> for each episode's audio bed. The templates below are the quick-reference
> skeletons.

Scripts here are *light* — body-doubling is presence, not performance. The point
is a predictable shape, not a monologue. Timestamps assume a 25-min block.

### A. Cowork With Me (the flagship)
```
[0:00] COLD OPEN (15s): "Hi, I'm [name]. If you've been putting something off,
        let's just start it together. One 25-minute focus block, then a break.
        I'm working too — you're not doing this alone."
[0:15] SET INTENTION (20s): "Type your one task in the chat/comments. Mine is
        [your task]. Timer starts... now."
[0:35] WORK BLOCK (24 min): mic muted OR soft keyboard. NeuroTune steady_focus
        bed. On-screen countdown. No talking.
[24:35] BREAK CUE (60–90s): soft chime, stand/stretch line, one sip, "Halfway.
        How did that go? Next block in 60 seconds."
[REPEAT] for N rounds.
[OUTRO] (20s): "That's our session. You showed up — that counts. Same time
        tomorrow?"
```

### B. Meal Companion
```
[0:00] (15s): "Pull up a chair — let's eat together. No rush, no phone-doom,
        just company for the next [15] minutes."
[0:15] light, low-key narration of what you're eating OR silent w/ gentle ASMR.
        deep_calm or calm_focus bed, kept very low.
[end] (15s): "Thanks for eating with me. Drink some water. See you next meal."
GUARDRAILS: a *normal* portion shown kindly; no extreme mukbang, no chewing
        close-mic that fetishizes; many viewers struggle with food.
```

### C. Build With Me (AI apps) — pairs with THIS repo
```
[0:00] (20s): "Today we ship one small thing: [tiny AI app idea]. Cowork pace —
        I narrate lightly, captions on, no rushing. Build alongside me."
[0:20] PLAN (1 min): state the one outcome ("a CLI that does X").
[work blocks w/ Pomodoro] calm narration of each step; pause-points where the
        viewer catches up. steady_focus bed, low.
[break] "Stretch. We're [n] steps in."
[OUTRO] "It runs. We shipped something. Your turn — what did you build?"
TIP: this repo (NeuroTune) is itself a great recurring 'Ship Something Small'.
```

### D. Get Ready With Me / Routine
```
[0:00] (15s): "Morning. Let's get ready together and ease into the day."
[body] hair/skincare/tidy in real time, warm conversational tone, calm_focus or
        energize bed. Model the routine, don't perform it.
[OUTRO] "Okay — we're ready. Go be a person today."
```

### E. Play Quietly With Me (cozy gameplay)
```
[0:00] (15s): "Cozy [game] tonight. Low stakes, soft commentary — wind down with
        me, or keep me on in the background while you do your thing."
[body] relaxed play, long comfortable silences allowed. deep_calm/calm_focus bed.
GUARDRAILS: license-clear game + music (see docs/YOUTUBE.md).
```

---

## 4. The workflow with Claude — and which skills to use

A repeatable loop. Skills/tools in **bold** are ones you can invoke when we work
together (slash-commands or the NeuroTune CLI we've built).

1. **Research a topic or format** → use the **`deep-research`** skill for a
   fact-checked, cited survey (e.g. "what break activities retain ADHD viewers?").
   This whole guide came from that kind of survey.
2. **Generate the audio + timer assets** → the NeuroTune CLI we built:
   - a 1-hr focus bed: `python -m neurotune --mood steady_focus --minutes 60 --wav bed.wav`
   - a full Pomodoro cowork video: `python -m neurotune --session 25x5x4 --out cowork.mp4`
   - a week of variants at once: `python -m neurotune --batch --seeds 1-7 --minutes 60 --formats mp4`
3. **Draft the script** → ask me to fill a template from §3 for your specific task
   and length; I'll keep it claim-free and on-brand.
4. **Generate metadata** → once M11 lands, every render emits a `.meta.json`
   (title/description/tags/chapters) + thumbnail, so uploading is copy-paste.
5. **Plan the calendar** → `python -m neurotune.calendar_plan --weeks 4` (M12)
   gives a dated schedule where each row is a runnable render command.
6. **Verify before publishing** → the **`verify`** / **`run`** skills to confirm a
   render actually plays and looks right; **`code-review`** / **`simplify`** when we
   extend the tooling itself.
7. **Iterate from data** → bring back retention/comments; we adjust presets,
   pacing, and script hooks.

**Recording stack (your side, outside this repo):** OBS for screen/cam capture,
a decent USB mic, soft key light, and the NeuroTune MP4 as either the full video
(timer channels) or a background layer you talk over. An OBS Pomodoro Lua timer is
a fine live alternative to the rendered timer for streams.

---

## 5. One-line summary

Presence over polish, a visible timer, a fixed aesthetic and schedule, kind
breaks, captions, and zero medical claims — then let NeuroTune mass-produce the
rights-clean audio/timer assets so you can focus on *showing up*.
