# Survey: How Music Helps Autistic and ADHD People Calm Down or Reach a Productive Mood

*Compiled 2026-06-11 from PubMed-indexed literature and practitioner sources. This survey
drives the design of the `neurotune` generator in this repository — every preset parameter
maps back to a finding below.*

## 1. ADHD: music as external stimulation for focus

The core account in the literature is **optimal stimulation / moderate arousal**: ADHD brains
are chronically under-aroused, and a steady, non-demanding stream of auditory stimulation
"fills the gap" so attention doesn't wander off-task in search of stimulation.

Key findings:

- A systematic review of music and ADHD (Behavioral Sciences, 2025) concluded that
  individuals with ADHD frequently use **music listening as a means of increasing stimulation
  and self-regulation**, and that background music can support attention in some task contexts.
  DOI: [10.3390/bs15010065](https://doi.org/10.3390/bs15010065)
- A systematic review in the Journal of Medical Internet Research (2023) found evidence that
  **passive music listening can reduce ADHD symptomatology** and improve performance on some
  attention tasks, and proposed structured musical parameters (steady tempo, clear rhythm) as
  therapeutic levers. DOI: [10.2196/37742](https://doi.org/10.2196/37742)
- A randomized trial (BMC Complementary Medicine and Therapies, 2023) found 3 months of music
  therapy **increased serotonin and improved stress-coping ability** in children/adolescents
  with ADHD versus standard care. DOI: [10.1186/s12906-022-03832-6](https://doi.org/10.1186/s12906-022-03832-6)
- Practitioner consensus ([Healthline](https://www.healthline.com/health/adhd-music),
  [Brain.fm research guide](https://www.brain.fm/blog/does-music-help-adhd-research-guide),
  [Inflow](https://www.getinflow.io/post/adhd-and-music-helps-focus)):
  **steady rhythm, moderate tempo, instrumental** (lyrics compete for verbal working memory).
  Lo-fi hip-hop's popularity for ADHD focus sits in the **60–80 BPM** band. Slower tempos
  reduced hyperactive behavior in classic studies; brown/steady noise textures help some
  listeners by providing constant low-level stimulation. Binaural-beat evidence is
  **inconsistent** — we do not rely on it.

## 2. Autism: music as predictable sensory input for regulation

The dominant cognitive account is **intolerance of uncertainty**: unpredictable input is a
major driver of anxiety in autistic people, so *predictable* auditory structure is calming.

Key findings:

- "Autistic Cognition: Charting Routes to Anxiety" (Trends in Cognitive Sciences, 2021) models
  how **attenuated predictions and intolerance of uncertainty produce anxiety** in autism —
  the strongest theoretical justification for highly repetitive, low-surprise music.
  DOI: [10.1016/j.tics.2021.03.014](https://doi.org/10.1016/j.tics.2021.03.014)
- A systematic review of music therapy for ASD and other neurodevelopmental disorders
  (Frontiers in Psychiatry, 2021; 39 studies, n=1,774) reports benefits for **emotional
  regulation, anxiety and social engagement**, while noting heterogeneous study quality.
  DOI: [10.3389/fpsyt.2021.643234](https://doi.org/10.3389/fpsyt.2021.643234)
- An update of Cochrane-based systematic reviews (European Journal of Public Health, 2021)
  finds music therapy effective enough to recommend for ASD among other conditions.
  DOI: [10.1093/eurpub/ckab042](https://doi.org/10.1093/eurpub/ckab042)
- **Honest caveat:** the large TIME-A RCT (JAMA, 2017, n=364) found improvisational music
  therapy did **not** significantly beat enhanced standard care on ASD symptom severity —
  music is a support tool, not a treatment claim.
  DOI: [10.1001/jama.2017.9478](https://doi.org/10.1001/jama.2017.9478)
- Practitioner sources ([NeuroLaunch](https://neurolaunch.com/calming-music-for-autism/),
  [HeyASD](https://www.heyasd.com/blogs/autism/music-and-sound-based-sensory-activities),
  [Autistic Nick](https://autisticnick.com/music-for-autistic-adults)): autistic listeners often
  have **enhanced pitch/timbre processing**; instrumental music with **predictable structure**
  reduces distress more than silence or lyrical music; familiar, *chosen* music lowers cortisol.
  Music can buffer sensory overload by masking unpredictable environmental noise.

## 3. Shared themes across both groups

1. **Instrumental beats lyrical** — words compete with verbal working memory.
2. **Predictability is the active ingredient** — repetition, simple form, no sudden changes.
3. **Tempo sets arousal** — slow (≈50–60 BPM) calms; moderate (≈60–85 BPM) sustains focus;
   brighter (≈95–115 BPM) lifts mood/energy without tipping into overload.
4. **Narrow dynamics** — no startling jumps in loudness (sensory sensitivity).
5. **Consonance** — pentatonic/diatonic material avoids harsh dissonance.
6. **Personalization is non-negotiable** — individual variation is large in every study;
   parameters must be user-adjustable.

## 4. Evidence → design mapping for `neurotune`

| Finding | Generator parameter |
|---|---|
| Predictability reduces autistic anxiety | AABA phrase form, phrase repetition, order-1 Markov with low sampling temperature, capped melodic leaps |
| Moderate steady stimulation aids ADHD focus | `steady_focus` preset: 60–80 BPM, constant soft percussion pulse |
| Slow tempo calms | `deep_calm` preset: ~54 BPM, long note durations, sustained drone |
| Narrow dynamics / sensory sensitivity | Velocity confined to a small per-preset band |
| Consonance preference | All melodies snapped to pentatonic/diatonic scales |
| Brown-noise-like constant texture | Sustained low pad/drone track under the melody |
| No lyrics | Purely instrumental MIDI |
| Individual variation | Every parameter overridable from the CLI (`--tempo`, `--root`, `--minutes`, …) |

## 5. Limitations

Most cited studies concern children; effect sizes vary; "music therapy" (with a therapist)
differs from ambient music listening. This project generates *supportive listening material*
and makes no clinical claims.

*Literature search performed via PubMed (citations above include DOIs) and general web search.*
