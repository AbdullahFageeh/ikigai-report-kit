# Ikigai Report Kit

Build a personal, multi-system Ikigai report as a clean PDF — from free online tests plus your birth data.

This is the toolkit, not a finished report. You supply your own results; it does the calculation, layout and PDF export.

## What you get

- A **54-lens report template** grouped by evidence quality, so you always know which rows are measured and which are inferred.
- **Chart maths done properly** — Swiss Ephemeris, not lookup tables: natal positions, lunar nodes, the Vedic D10 career chart, your solar return, and astrocartography lines.
- **Numerology calculators** for Life Path, Expression / Soul Urge / Personality, and Arabic Abjad values.
- A **print-quality PDF** via pandoc plus any Chromium-based browser you already have.

## Why group by evidence quality

Most reports of this kind mix a validated personality inventory with a tarot spread and present both in the same confident voice. This template does not. Every row sits in one of three groups:

| Group | Meaning | How much to trust it |
|---|---|---|
| **A. Measured** | You sat the test. Real instrument, real score. | Strongest |
| **B. Charted** | Calculated from your birth data or name. Internally consistent; not scientifically validated. | Symbolic mirror |
| **C. Inferred** | Not separately tested — derived from A and B. | Working hypothesis |

Keep the labels. They are the difference between a useful document and a horoscope.

## Step 1 — Take the tests

All free, all online. Start with the seven priority ones; the rest are optional depth.

### Priority

| Test | What it gives you | Time | Link |
|---|---|---|---|
| 16Personalities | MBTI-style type (e.g. INFP-T) | 12 min | https://www.16personalities.com/free-personality-test |
| VIA Character Strengths | Ranked 24 character strengths | 15 min | https://www.viacharacter.org/survey/account/register |
| Big Five (IPIP-BFFM) | Five factors **with facet scores** | 15 min | https://openpsychometrics.org/tests/IPIP-BFFM/ |
| Enneagram | Type, and ideally wing | 10 min | https://www.truity.com/test/enneagram-personality-test |
| HEXACO-60 | Adds Honesty–Humility, which Big Five omits | 10 min | https://hexaco.org/hexaco-online |
| Grit Scale (Duckworth, official) | Perseverance and consistency of interest | 2 min | https://www.angeladuckworth.com/grit |
| ECR-R | Attachment style, measured rather than guessed | 10 min | https://openpsychometrics.org/tests/ECR.php |

### Recommended

| Test | What it gives you | Time | Link |
|---|---|---|---|
| ADHD self-report (ASRS v1.1) | Executive-function baseline | 5 min | https://add.org/adhd-test/ |
| MEQ chronotype | Your real deep-work window | 5 min | https://chronotype-self-test.info/ |
| Burnout self-check | A number you can re-measure each quarter | 5 min | https://www.mindtools.com/ap5f8ab/burnout-self-test |
| Enneagram, second opinion | Cross-check your type | 10 min | https://similarminds.com/embj.html |

### Backup links

If any of the above is unreachable:

| Test | Alternative |
|---|---|
| ADHD ASRS | https://psychology-tools.com/test/adult-adhd-self-report-scale |
| Attachment (Fraley's original ECR) | http://www.web-research-design.net/cgi-bin/crq/crq.pl |
| Grit Scale | https://psytests.org/emvol/griten.html |
| IPIP item bank (build your own) | https://ipip.ori.org/ |

### Reading, not tests

- Enneagram instinctual variants — https://www.enneagraminstitute.com/enneagram-instinctual-variants/

### Chart systems you do not need to pay for

Human Design, Gene Keys and BaZi charts are free to generate online, and `scripts/chart.py` in this repo computes the Western, Vedic, D10, solar-return and astrocartography data directly.

## Step 2 — Gather your inputs

You need:

- **Birth date, time and place.** Time matters. An hour of error moves your Ascendant a whole sign; `chart.py` prints the exact minute your Ascendant changes sign so you can see how sensitive your chart is.
- **Your full legal name**, in English and — if applicable — in Arabic script.
- **Your test results** from Step 1.

## Step 3 — Install the tools

```bash
brew install pandoc poppler          # macOS; poppler is optional, for PDF checks
python3 -m venv .venv
.venv/bin/pip install ephem          # required for scripts/extended_systems.py
.venv/bin/pip install pyswisseph     # optional; needed for scripts/chart.py
```

### Method choices used in `extended_systems.py`

To keep outputs stable and reproducible, the script uses explicit fixed methods:

- **Chinese Zodiac / BaZi**: Li Chun year boundary (fixed Feb 4 local), fixed solar-month boundaries, 1900-01-31 as Jia-Zi day reference.
- **Human Design**: PyEphem geocentric longitudes, 88° solar arc for Design timestamp, fixed Rave Mandala sequence for gate/line mapping, mean lunar-node model.
- **Gene Keys**: direct mapping from Human Design activations (Gene Key number = gate number), Activation Sequence from Sun/Earth in personality/design.
- **Destiny Matrix**: deterministic Matrix of Destiny 22 digit-reduction model (core + derived points).

You also need one Chromium-based browser. The build script auto-detects Chrome, Chromium, Brave, Edge, Opera and Opera GX.

## Step 4 — Run the calculators

```bash
# Chart: natal, nodes, D10 career chart, solar return, astrocartography
.venv/bin/python scripts/chart.py \
  --date 1990-01-15 --time 14:30 --tz +3 \
  --lat 21.4858 --lon 39.1925 --solar-year 2026

# Numerology: Life Path, Expression / Soul / Personality, Abjad
python3 scripts/numerology.py \
  --dob 1990-01-15 \
  --name-en "Your Full Name" \
  --name-ar "اسمك الكامل"

# Extended systems: Chinese Zodiac / BaZi, Human Design, Gene Keys, Destiny Matrix
.venv/bin/python scripts/extended_systems.py \
  --date 1990-01-15 --time 14:30 --tz +3 \
  --lat 21.4858 --lon 39.1925
```

## Step 5 — Write and build

```bash
cp template/report-template.md my-report.md
# fill in your results, delete what does not apply
./build.sh my-report.md
open my-report.pdf
```

## Layout conventions

The template uses a few small conventions the stylesheet understands:

- `> A bold one-line takeaway` — renders as the teal callout box. One per section, at the top.
- `# 4. Section title {.newpage}` — starts the section on a fresh page.
- `<p class="lede">Italic intro line.</p>` and `<p class="note">Small grey caveat.</p>`
- `::: wide` … `:::` — shrinks a many-column table so it fits the page.
- `::: links` … `:::` — shrinks a table of URLs.

## Honest limitations

- Psychometric instruments (Big Five, HEXACO, VIA, RIASEC, Grit) have peer-reviewed research behind them. Their limits are still real: self-report, reference bias, and easy faking.
- Numerology, astrology, Human Design, Gene Keys, BaZi, Cardology and the Destiny Matrix have no predictive validity. They are in the template because a structured mirror can be genuinely useful for reflection — not because they are true. Keep them in Group B and say so in your report.
- The value of a report like this is **convergence plus a decision**. Fifty lenses agreeing is interesting; a shortlist you can act on is the point. Do not skip the scoring section.

## Licence

MIT. Do what you like with it. No warranty, and nothing here is medical, psychological or financial advice.
