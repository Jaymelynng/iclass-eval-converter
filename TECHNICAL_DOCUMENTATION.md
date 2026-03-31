# Star Chart Converter — Technical Documentation

## Project Overview

Full-stack web application that converts iClassPro skill evaluation XLS exports into branded, multi-page PDFs. Supports 10 gyms, 6 training programs, automatic score-to-star rendering, and blank grid generation.

---

## Architecture

### Tech Stack
- **Frontend:** HTML5, Vanilla JavaScript (ES6+), SheetJS (XLS parsing)
- **Backend:** Python + ReportLab (PDF generation)
- **Local Dev Server:** Flask 3.0+
- **Production:** Vercel (serverless Python function)

### File Structure

```
/Star Chart Converter
  ├── app.py                     # Flask local dev server (port 5050)
  ├── pdf_generator.py           # PDF engine — local copy (keep in sync with api/)
  ├── requirements.txt           # flask>=3.0, reportlab>=4.0
  ├── vercel.json                # Vercel routing + cache config
  ├── download_logos.py          # One-time utility to fetch gym logos
  ├── logos/                     # Logo files for local dev (app.py)
  ├── reference-pdfs/            # Reference PDFs for design comparison
  ├── SkillsStars_Manager_Checklist (2).docx  # Reference doc
  │
  ├── api/
  │   ├── generate-pdf.py        # Vercel serverless HTTP handler
  │   ├── pdf_generator.py       # PDF engine — production copy (authoritative)
  │   └── requirements.txt       # reportlab>=4.0 only (no Flask needed on Vercel)
  │
  └── public/
      ├── index.html             # Entire frontend (HTML + CSS + JS in one file)
      └── logos/                 # Gym logos served by both Vercel static + browser
          ├── CCP_logo_transparent.png
          ├── crr_logo.png
          ├── est_logo.png
          ├── hga_logo.png
          ├── oas_logo.png
          ├── rba_logo.png
          ├── rbk_logo.png
          ├── sgt_logo.png
          └── tig_logo.png
```

### CRITICAL: Two pdf_generator.py Files

`api/pdf_generator.py` is what Vercel runs. `pdf_generator.py` (root) is what `app.py` (local Flask) imports. **They must always be kept identical.** Whenever you edit one, copy it to the other:

```bash
cp api/pdf_generator.py pdf_generator.py
```

---

## Vercel Deployment

### vercel.json

```json
{
  "builds": [
    { "src": "api/generate-pdf.py", "use": "@vercel/python" },
    { "src": "public/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/generate-pdf", "dest": "/api/generate-pdf.py" },
    { "src": "/(.*)", "dest": "/public/$1" }
  ],
  "headers": [
    {
      "source": "/(.*\\.html)",
      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }]
    }
  ]
}
```

- POST `/generate-pdf` → `api/generate-pdf.py` (Python serverless)
- GET `/*` → `public/` (static files)
- HTML files: no-cache so deploys take effect immediately

### Deploy Command

```bash
npx vercel --prod
```

Vercel also auto-deploys on `git push` to master if GitHub integration is connected.

---

## Gym Configuration

Defined in **both** `api/pdf_generator.py` (Python dict) and `public/index.html` (JS object). Must be kept in sync.

### Python (api/pdf_generator.py)

```python
GYMS = {
    'CCP': {
        'name':  'CAPITAL GYMNASTICS — Cedar Park',
        'logo':  'logos/CCP_logo_transparent.png',
        'blue':  '#1f53a3',   # Primary color: header bar, BARS/BEAM event headers
        'red':   '#bf0a30',   # Secondary color: VAULT/FLOOR event headers
        'gray':  '#d8d8d8',   # Tertiary: text, borders
    },
    # ... 9 more gyms
}
```

### JavaScript (public/index.html)

```javascript
const GYMS = {
  CCP: {
    name: 'Capital Gymnastics Cedar Park',
    c1: '#1f53a3',    // Card border, logo background, modal accent
    c2: '#bf0a30',    // Secondary
    c3: '#d8d8d8',    // Tertiary
    c4: '#ffffff',    // White
    logo: 'https://...'  // CDN URL for browser display
  },
  // ...
}
```

### All 10 Gyms

| Code | Name | blue/c1 | red/c2 | Special Overrides |
|------|------|---------|--------|-------------------|
| CCP | Capital Gymnastics — Cedar Park | `#1f53a3` | `#bf0a30` | — |
| CPF | Capital Gymnastics — Pflugerville | `#1f53a3` | `#bf0a30` | — |
| CRR | Capital Gymnastics — Round Rock | `#4a4a4b` | `#ff1493` | `event_dark: #111111`, `skill_mid: #ff1493` |
| EST | Estrella Gymnastics | `#011837` | `#666666` | — |
| HGA | Houston Gymnastics Academy | `#c91724` | `#262626` | — |
| OAS | Oasis Gymnastics | `#3e266b` | `#3eb29f` | — |
| RBA | Rowland Ballard — Atascocita | `#1a3c66` | `#c52928` | — |
| RBK | Rowland Ballard — Kingwood | `#1a3c66` | `#c52928` | — |
| SGT | Scottsdale Gymnastics | `#c72b12` | `#e6e6e6` | — |
| TIG | Tigar Gymnastics | `#f57f20` | `#0a3651` | — |

### Optional Color Overrides (per-gym)

| Key | Purpose |
|-----|---------|
| `event_dark` | Explicit color for all event band headers (VAULT/BARS/BEAM/FLOOR) |
| `skill_mid` | Explicit color for all skill sub-headers |

Used by CRR to create 3-level differentiation: dark grey header → black event bands → hot pink skill subs.

---

## Color System

### _build_event_colors(blue_hex, red_hex, event_dark_hex=None, skill_mid_hex=None)

Derives a 3-level color palette from the gym's two brand colors:

```
EV_DARK  → darkened (20%) — event headers (VAULT, BARS, BEAM, FLOOR)
EV_MED   → lightened (30%) — skill sub-headers (RUN + HURDLE, etc.)
EV_LIGHT → neutral #f0f0f0 — column stripe backgrounds
```

Color assignment by apparatus:

| Apparatus | EV_DARK source | EV_MED source |
|-----------|---------------|---------------|
| VAULT | red (darkened) | red (lightened) |
| BARS | blue (darkened) | blue (lightened) |
| BEAM | blue (as-is) | blue (lightened) |
| FLOOR | red (darkened) | red (lightened) |
| SAFETY | blue (darkened) | blue (lightened) |

If `event_dark_hex` is set, it overrides ALL event header colors.
If `skill_mid_hex` is set, it overrides ALL skill sub-header colors.

### Helper Functions

```python
_lighten(hex_color, factor)   # Blend toward white by factor (0.0–1.0)
_darken(hex_color, factor)    # Multiply RGB channels by (1-factor)
hex_color(hex_str)            # Convert '#rrggbb' to ReportLab Color object
```

---

## PDF Generation

### Page Dimensions (Landscape Letter)

```
Total:   792 × 612 points (11" × 8.5")
Margin:  18pt all sides
Usable:  756 × 576pt
```

### Layout Zones (top to bottom)

```
TOP_BAR_H    = 48pt   ← gym name, logo, class info
EV_HDR_H     = 15pt   ← VAULT / BARS / BEAM / FLOOR
SK_HDR_H     = 26pt   ← skill names (RUN + HURDLE, etc.)
CRIT_H       = 88pt   ← rotated criteria text
STAR_ROW_H   = 11pt   ← ★1 ★2 ★3 ★F labels
DATA_H       = varies ← student rows (fills remaining space)
FOOTER_H     = 68pt (safety) or 18pt (no safety)
```

### generate_pdf() — Key Parameters

```python
def generate_pdf(
    gym_code,      # e.g. 'CCP'
    class_name,    # e.g. 'Preschool Gymnastics'
    date,          # e.g. '03/30/2026'
    day,           # e.g. 'Monday'
    time,          # e.g. '3:30pm'
    students,      # list of name strings
    program,       # e.g. 'Preschool'
    score_map,     # dict: apparatus → list of row arrays
    mode,          # 'eval' or 'blank'
    _canvas=None   # if provided, draws on this canvas (multi-page mode)
)
```

When `_canvas` is None, creates a BytesIO buffer and returns PDF bytes.
When `_canvas` is provided, draws onto it and returns None (caller owns canvas lifecycle).

### generate_multi_pdf() — Multi-page

```python
def generate_multi_pdf(gym_code, classes, mode='eval'):
    # classes = list of dicts:
    # { className, date, day, time, students, program, scoreMap }
    # Returns: PDF bytes (one page per class)
```

Calls `generate_pdf()` per class with `_canvas=c`, calls `c.showPage()` between pages.

### Star Rendering

```python
def draw_star(c, cx, cy, r, fill_color, stroke_color, lw=0.8):
    # Draws a 5-point star centered at (cx, cy) with outer radius r
    # Points calculated at 72° intervals starting from top
    # Inner radius = r * 0.38
```

Score rendering logic per bubble:

```python
if mode == 'blank' or not earned:
    # Criteria: white circle, gray stroke
    c.circle(bx, cy, bub_r, fill=1, stroke=1)
    # Final star: white star outline
    draw_star(c, bx, cy, bub_r*1.2, WHITE, CCP_GRAY_MID, lw=1.2)
else:
    # Criteria earned: filled red star
    draw_star(c, bx, cy, bub_r*1.15, CCP_RED, CCP_RED, lw=0)
    # Final star earned: filled gold star
    draw_star(c, bx, cy, bub_r*1.2, GOLD, '#8a6a00', lw=0.5)
```

### Score Lookup

```python
lookup = build_score_lookup(score_map, students, SKILLS)
# lookup[skill_idx][crit_idx] = list of bool, one per student
# lookup[skill_idx]['final']  = list of bool, one per student
```

`score_map` structure (from frontend):
```javascript
{
  'vault': [
    [1, 0, 1, ...],   // criterion 1, one value per student
    [0, 1, 1, ...],   // criterion 2
    [1, 0, 0, ...],   // criterion 3
    [1, 1, 0, ...],   // final star ("puts it all together")
  ],
  'bars':  [...],
  'beam':  [...],
  'floor': [...],
  'safety': [...],
}
```

---

## Frontend (public/index.html)

Single-file app (~1250 lines). No build step. No framework.

### Key Functions

| Function | Purpose |
|----------|---------|
| `parseEvalXLS(file)` | Async — reads XLS with SheetJS, returns array of evalData objects |
| `parseTabName(tabName)` | Extracts day/time/program/age from sheet tab name |
| `generatePages(mode)` | Builds request payload, POSTs to `/generate-pdf`, triggers download |
| `generateBlankMulti()` | Generates blank grid PDFs from checkbox selections |
| `openGymModal(code)` | Opens modal, applies gym colors via CSS vars |
| `closeModal()` | Clears inline style overrides, hides modal |
| `applyGymColors(gym)` | Sets `--c1`, `--c2`, `--accent` CSS custom properties |

### XLS Parsing — parseEvalXLS()

SheetJS reads the file. For each sheet:

1. Find header rows containing "Discipline" + "Level"
2. Extract student names from columns 4+ of header row
3. Parse data rows: Discipline → program, Level → apparatus, criterion + scores
4. Handle "Puts it all together" → final star row
5. Normalize apparatus names: "Jr Vault" → "vault"
6. Build `_xlsScoreMap`: `{ apparatus: [[...], [...], ...] }`

Multiple header groups per sheet are supported (iClassPro sometimes splits them).

### Tab Name Parsing — parseTabName()

Handles two formats:
- Pipe: `"Preschool | Monday | 3:30pm | Ages 3-4"`
- Space: `"Preschool  Monday  330pm  Ages "` (double-space separated)

```javascript
function parseTabName(tabName) {
  // 1. Detect separator (pipe vs double-space)
  // 2. Split into segments
  // 3. For each segment:
  //    - dayRe match → result.day
  //    - compactTime match (330pm) → result.time
  //    - colonTime match (3:30pm) → result.time
  //    - age match → result.age
  //    - else → programParts (joined as result.program)
  return { day, time, program, age }
}
```

### Request Payload (frontend → backend)

```javascript
POST /generate-pdf
Content-Type: application/json

{
  gymCode: "HGA",
  classes: [
    {
      className: "Preschool Gymnastics",
      date:      "03/30/2026",
      day:       "Monday",
      time:      "3:30pm",
      students:  ["Elliana J.", "Raiylah J.", "Ellie T."],
      program:   "Preschool",
      scoreMap:  { vault: [[1,0,1],[0,1,1],[1,0,0],[1,1,0]], ... }
    }
  ],
  mode: "eval"   // or "blank"
}
```

### Response

Binary PDF bytes with headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="HGA_Preschool_03-30-2026.pdf"
```

Frontend triggers download via:
```javascript
const url = URL.createObjectURL(new Blob([bytes], {type:'application/pdf'}));
const a = document.createElement('a');
a.href = url; a.download = filename; a.click();
```

---

## Program Definitions

6 programs defined in `api/pdf_generator.py` under `PROGRAMS` dict:

| Program | Skills | Has Safety | Footer Height |
|---------|--------|-----------|---------------|
| Preschool | 10 | Yes | 68pt |
| Junior | 11 | Yes | 68pt |
| Advanced Junior | 14 | No | 18pt |
| Level 1 | 14 | No | 18pt |
| Level 2 | 13 | No | 18pt |
| Level 3 | 13 | No | 18pt |

Each skill:
```python
{
    'event':    'VAULT',           # Apparatus
    'short':    'RUN + HURDLE',    # Displayed in skill header band
    'criteria': [                  # Each becomes one column (+ auto final star)
        'Runs into hurdle, no stopping',
        'Hurdles 1 foot to land on both feet',
        'Arms by ears in jump',
    ]
}
```

Program resolution handles iClassPro naming variations (case-insensitive, substring):
```python
'preschool', 'new preschool'          → 'Preschool'
'junior', 'new junior', 'jr'          → 'Junior'
'advanced junior', 'adv jr', 'adv j'  → 'Advanced Junior'
'girls level 1', 'level 1', 'gl1'     → 'Level 1'
# etc.
```

---

## Logo Resolution

```python
# api/pdf_generator.py
_here = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(_here, gym['logo'])              # api/logos/...
if not os.path.exists(logo_path):
    logo_path = os.path.join(_here, '..', 'public', gym['logo'])  # public/logos/...
if os.path.exists(logo_path):
    c.drawImage(logo_path, MARGIN+4, bar_y+4, width=40, height=40, mask='auto')
```

On Vercel, the first path (`api/logos/`) doesn't exist, so it falls back to `public/logos/`. The `mask='auto'` tells ReportLab to treat white pixels as transparent.

---

## Local Development

```bash
# Install dependencies
pip install flask reportlab

# Run local server
python app.py
# → http://localhost:5050

# app.py serves:
# GET  /           → public/index.html
# GET  /public/*   → static files
# POST /generate-pdf → pdf_generator.py
```

---

## Adding a New Gym

1. **pdf_generator.py** (both root and api/): Add entry to `GYMS` dict
2. **public/index.html**: Add entry to `GYMS` JS object + logo URL
3. **public/logos/**: Add logo PNG (transparent background preferred)
4. Deploy: `git add -A && git commit -m "..." && git push && npx vercel --prod`

## Adding a New Program

1. **api/pdf_generator.py**: Add entry to `PROGRAMS` dict with `skills`, `has_safety`, `footer_h`
2. Add aliases to `resolve_program()` function
3. **public/index.html**: Add checkbox to blank grids section + SKILL_DATA entry
4. Test locally with `python app.py`

---

## Known Constraints

- Max 6 students per page (hardcoded `NUM_ROWS = 6`)
- Criteria text is pixel-width-truncated to fit rotated column (~88pt tall)
- Fonts are limited to ReportLab built-ins (Helvetica family) — no custom fonts
- Logo must be accessible at runtime (Vercel reads from `public/logos/`)
- XLS file must use iClassPro's "Class Evaluation Report" format
