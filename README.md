# Mock Lab Practical 2 — BIOL 40B (Cardiovascular & Respiratory)

An interactive, self-contained mock lab practical for **BIOL 40B Lab Exam 2** (Labs 5–8).
A structure is pinned on each image — you identify it, give one function, and (where blood is
present) say whether it's oxygenated or deoxygenated. Just like the real bench.

**19 stations · 121 structures** across the cardiovascular and respiratory systems.

## Modes
- **Exam** — timed 2:00 per station, auto-advances at the bell, full scored review. Pick 20 / 40 / all.
- **Study** — untimed; check each answer as you go, with the model function revealed.
- **Multiple choice** — untimed warm-up: pick the pinned structure from four options, instant feedback.

## Spot something wrong?
Hit **⚑ Flag** on any station (add a note if you like), then **Copy list** on the start or results
screen and send it over — that's how this gets fixed.

## Build it yourself
The page is generated from data, so it's easy to edit:
- `build.py` — image metadata + question list → emits the self-contained HTML (images inlined as data-URIs).
- `app_template.html` — the quiz engine (CSS + JS).
- `verify.py` — emits a pin contact-sheet for calibration.

```bash
pip install pillow
python3 build.py     # writes practical.html and index.html
```

## Image credits
See the **Image credits & sources** panel on the start screen. In short: respiratory diagrams from
OpenStax *Anatomy & Physiology* (CC BY 4.0); heart-wall diagram OpenStax (CC BY 3.0); cardiac-muscle
histology by RWhitwam via Wikimedia Commons (CC BY-SA 4.0). Diagrams are used for non-commercial
educational study.

---
*A student-made study aid. Not affiliated with or endorsed by the course.*
