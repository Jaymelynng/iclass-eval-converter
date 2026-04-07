# Star Chart Converter — Technical Documentation

## Project Overview

Full-stack web application that converts iClassPro skill evaluation XLS exports into branded, multi-page PDFs. Supports 10 gyms, 9 training programs (6 girls + 3 boys), automatic score-to-star rendering, and blank grid generation.

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
  ├── requirements.txt           # flask>=3.0, reportlab>=4.0
  ├── vercel.json                # Vercel routing + cache config
  ├── reference-pdfs/            # Reference PDFs for design comparison
  ├── stress tests/              # Stress test spreadsheets + audit results
  ├── renaming-tools/            # iClassPro class rename tool (HTML)
  ├── auditing tools source of truth and results/  # Skill tree audit reference + results
  ├── STAR CHART MEETINGS AND PLANNING TRANSCRIPTS/  # Meeting notes and planning docs
  ├── SkillsStars_Manager_Checklist (2).docx  # Reference doc
  │
  ├── api/
  │   ├── generate-pdf.py        # Vercel serverless HTTP handler
  │   ├── pdf_generator.py       # PDF engine — single authoritative source
  │   └── logos/                 # Logo copies for Vercel Python function access
  │
  └── public/
      ├── index.html             # Entire frontend (HTML + CSS + JS in one file)
      ├── sop-guide.html         # Standard Operating Procedure guide for managers
      └── logos/                 # Gym logos served by both Vercel static + browser
          ├── CCP_logo_transparent.png
          ├── crr_logo.png
          ├── est_logo.png
          ├── hga with shadow.png
          ├── hga_logo.png
          ├── oas_logo.png
          ├── oasis circle logo.png
          ├── rba_logo.png
          ├── rbk_logo.png
          ├── sgt_logo.png
          └── tig_logo.png
```

### Single pdf_generator.py — api/ is authoritative

`api/pdf_generator.py` is the single source of truth — it's what Vercel runs AND what `app.py` (local Flask) imports. `app.py` adds `api/` to `sys.path` at startup so both environments use the same file. **Never create a root-level copy.** Edit `api/pdf_generator.py` only.

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

### CRITICAL: .vercelignore

The `.vercelignore` file MUST exist in the repo root. It excludes large folders from the serverless bundle. Without it, the bundle exceeds Vercel's 250MB Lambda limit and deploys fail silently (500 errors on every request).

```
node_modules
stress tests
renaming-tools
layout-attempts
auditing tools source of truth and results
reference-pdfs
.playwright-mcp
```

**If you add a new large folder to the repo, add it to `.vercelignore` immediately.**

### CRITICAL: Python Import Path

`api/generate-pdf.py` MUST include this before importing pdf_generator:

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

Vercel's Python runtime does NOT automatically add the `api/` directory to the module search path. Without this, the serverless function crashes with `ModuleNotFoundError: No module named 'pdf_generator'`. This broke in production on April 5, 2026 when Vercel updated their runtime.

### Post-Deploy Checklist

After every `git push` or `npx vercel --prod`:
1. Wait 2 minutes for Vercel to build
2. Check Vercel logs at vercel.com → star-chart-converter → Logs for errors
3. Open evalconvert.com, select any gym, upload a test file, confirm PDF downloads
4. If 500 error: check logs for import errors or bundle size errors

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

1. Find ALL header rows containing "Discipline" + "Level" (there may be multiple per sheet)
2. For each header group, extract student names from columns 4+ of **that specific header row**
3. Parse data rows between header groups, mapping scores to local student column indices
4. Handle "Puts it all together" → final star row
5. Normalize apparatus names: "Jr Vault" → "vault"
6. Build `_xlsScoreMap` per group: `{ apparatus: [[...], [...], ...] }`
7. One `evalResult` object is pushed per header group, not per sheet

**CRITICAL: One result per header group, not per sheet.**
iClassPro sometimes exports two classes at the same day/time as a single sheet with two header sections. The parser splits these into separate `evalResult` objects. Each gets an A/B suffix appended to the class name (e.g. "Level 1 A", "Level 1 B").

```javascript
// A/B suffix logic
const groupSuffix = headerRowIndices.length > 1 ? ' ' + String.fromCharCode(65 + gIdx) : '';
```

If a sheet has only one header group, no suffix is added.

### CRITICAL: Class Name Source — Tab Name, Not Discipline Column

**The iClassPro discipline column does NOT contain the class name.** It contains an internal program label like `"NEW Girls Recreational Gymnastics"` or `"NEW Preschool Gymnastics"`. This is **not** what you want in the PDF header.

The real class name (e.g. `"Level 1"`, `"Preschool"`, `"Advanced Junior"`) comes from the **XLS sheet tab name**, which maps to the iClassPro class name.

The parser uses `tabInfo.program` (extracted from the tab name) as the `className` sent to the backend. The discipline column value is used **only** as a fallback when tab name parsing fails.

**PROGRAM_MAP matching also uses tab name as fallback.** If the discipline column doesn't resolve to a known program (Level 1/2/3 all show as "Girls Recreational Gymnastics"), the parser re-runs PROGRAM_MAP matching against the tab name:

```javascript
if (program === 'Unknown' && evalData.tabName) {
    const tabUpper = evalData.tabName.toUpperCase();
    for (const [key, val] of Object.entries(PROGRAM_MAP)) {
        if (tabUpper.includes(key)) { program = val; break; }
    }
}
```

Classes that still resolve to `'Unknown'` after both passes are **silently skipped** — they don't error, they just don't appear in the PDF. This is the most common cause of "missing pages."

---

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

**Ages stripping from tab names:** After extracting day and time, the parser strips age segments and truncation fragments from the program name. This handles iClassPro tab names like `"Level 1  Monday  330pm  Ages 7-8"` where "Ages 7-8" would otherwise become part of the class name. The cleanup chain:
```javascript
tabInfo.program.replace(/\s*ages?\s+[\d–-]+\s*$/i, '')  // "Ages 7-8"
               .replace(/\s*ages?\s*$/i, '')              // trailing "Ages" alone
               .replace(/\s+ag$/i, '')                     // truncated "Ag" fragment
               .trim()
```
Single-letter fragments after the time field (like a lone "A" from truncated "Ages") are also skipped during segment parsing.

**Known limitation: iClassPro strips pipe characters from XLS tab names on export.**
Even if the class is named `"Level 1 | Monday | 3:30pm | Ages 7-8"` in iClassPro, the XLS tab name will come through as `"Level 1  Monday  330pm  Ages 7-8"` (spaces only, no pipes). The parser handles both formats, so this works — but it means the pipe format in iClassPro class names is effectively cosmetic only.

**Known limitation: Single-number ages don't parse.**
`parseTabName` only detects age ranges like `"5-6"` or `"7-8"`. A single age like `"7"` or `"7+"` is not extracted. The `ages` field in the PDF header will be empty for classes with a single-number age. This does not affect scores or program detection.

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

9 programs defined in `api/pdf_generator.py` under `PROGRAMS` dict:

| Program | Skills | Has Safety | Has Mastery | Footer Height | num_rows | Events |
|---------|--------|-----------|-------------|---------------|----------|--------|
| Preschool | 10 | Yes | Yes | 68pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Junior | 11 | Yes | Yes | 68pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Advanced Junior | 14 | No | Yes | 18pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Level 1 | 14 | No | Yes | 18pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Level 2 | 13 | No | Yes | 18pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Level 3 | 13 | No | Yes | 18pt | 6 | 4 (Vault, Bars, Beam, Floor) |
| Boys Level 1 | 22 | No | No | 18pt | 8 | 5 (Floor, Mushroom, Vault, P Bars, Bars) |
| Boys Level 2 | 22 | No | No | 18pt | 8 | 6 (Floor, Pommel, Rings, Vault, P Bars, H Bars) |
| Boys Level 3 | 23 | No | No | 18pt | 8 | 6 (Floor, Pommel, Rings, Vault, P Bars, H Bars) |

### has_mastery Flag

Girls programs use `has_mastery: True` (default). Each skill has 3 criteria columns plus a final "mastery" star column ("Puts it all together"). Boys programs use `has_mastery: False` — their skills are structured as flat criteria lists per event with no final mastery star. The `build_score_lookup()` function and the PDF renderer both check `has_mastery` to decide whether to draw the 4th star column.

Each skill (girls programs):
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

Each skill (boys programs):
```python
{
    'event':    'FLOOR',           # Apparatus
    'short':    'Floor',           # Displayed in skill header band
    'criteria': [                  # Each becomes one column (NO final star)
        'Handstand',
        'Cartwheel',
        'Backward roll to feet',
        'Bridge',
        'Forward roll',
        'Round off introduction',
    ]
}
```

Program resolution handles iClassPro naming variations (case-insensitive, substring):
```python
'preschool', 'new preschool'          → 'Preschool'
'junior', 'new junior', 'jr'          → 'Junior'
'advanced junior', 'adv jr', 'adv j'  → 'Advanced Junior'
'girls level 1', 'level 1', 'gl1'     → 'Level 1'
'boys level 1', 'boys l1'             → 'Boys Level 1'
'boy039s level 1'                     → 'Boys Level 1'  # iClassPro apostrophe corruption
# etc.
```

### PROGRAM_SKIP

`PROGRAM_SKIP` is a JavaScript array of regex patterns in `public/index.html`. Any class whose name matches a PROGRAM_SKIP pattern is rejected **before** program matching — it never reaches the PDF generator. Currently empty:

```javascript
const PROGRAM_SKIP = [
  // Currently empty — Boys Level now supported
];
```

This existed previously to skip Boys Level classes before they were supported. When Boys Level 1/2/3 were added to both frontend and backend, the skip patterns were removed. If a new unsupported program needs to be excluded, add a regex pattern here.

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

Logos are copied to both `api/logos/` and `public/logos/`. On Vercel, the Python function resolves `api/logos/` first (local to the serverless bundle). The `public/logos/` fallback exists for backwards compatibility. The `mask='auto'` tells ReportLab to treat white pixels as transparent.

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

### Code Changes
1. **api/pdf_generator.py**: Add entry to `GYMS` dict (name, logo path, blue/red hex, optional overrides)
2. **public/index.html**: Add entry to `GYMS` JS object + logo CDN URL
3. **public/logos/**: Add logo PNG (transparent background preferred)
4. **api/logos/**: Copy same logo PNG here (Vercel Python function needs local access)
5. Deploy: `git add -A && git commit -m "..." && git push && npx vercel --prod`

### Full Onboarding Process (per gym)
1. **Skill tree verification**: Compare the gym's iClassPro skill ratings against the source of truth audit reference (`Skills_Stars_Audit_Reference.xlsx` in `auditing tools source of truth and results/`). Every criterion text and order must match exactly. Do not do structure-only checks.
2. **Rename tool**: Use the renaming tool (`renaming-tools/`) to generate properly formatted class names following the `Program | Day | Time | Ages` convention.
3. **Class rename in iClassPro**: Apply the generated names to all classes in the gym's iClassPro account.
4. **Skill ratings**: Verify that skill rating scales in iClassPro match the expected 1-star binary system (3 criteria + 1 mastery per skill for girls programs, flat criteria for boys).
5. **Discipline assignment**: Ensure every class has the correct discipline assigned in iClassPro so the converter can resolve the program.
6. **Test export**: Export a Class Evaluation Report from iClassPro and run it through the converter. Verify page count, class names, scores, and layout.
7. **Manager walkthrough**: Walk the gym manager through the SOP guide (`public/sop-guide.html`) covering export, upload, and download steps.

## Adding a New Program

1. **api/pdf_generator.py**: Add entry to `PROGRAMS` dict with `skills`, `has_safety`, `footer_h`
2. Add aliases to `resolve_program()` function
3. **public/index.html**: Add checkbox to blank grids section + SKILL_DATA entry
4. Test locally with `python app.py`

---

## Known Constraints

- Max 6 students per page for girls programs (hardcoded `NUM_ROWS = 6`); max 8 for boys programs (`num_rows: 8`)
- Criteria text is pixel-width-truncated to fit rotated column (~88pt tall)
- Fonts are limited to ReportLab built-ins (Helvetica family) — no custom fonts
- Logo must be accessible at runtime (Vercel reads from `api/logos/` first, falls back to `public/logos/`)
- XLS file must use iClassPro's "Class Evaluation Report" format
- Single-number ages (e.g. "7") are not extracted from tab names — only age ranges ("5-6") work
- Classes resolving to program `'Unknown'` are silently dropped (no error, no page)
- Boys Level classes use different apparatus than girls (Floor, Mushroom/Pommel, Vault, P Bars, Bars/H Bars, Rings) — the color system maps these to the same palette using event name matching
- **Hidden classes in iClassPro**: Classes set to "hidden" in iClassPro still appear in the XLS export. Managers may see unexpected classes in the converter output. This is an iClassPro behavior, not a converter bug.
- **iClassPro bulk assign bug**: When bulk-assigning skill ratings in iClassPro, the system sometimes applies ratings to the wrong students or duplicates ratings across classes. Always verify ratings after bulk operations by re-exporting and checking the converter output.
- **iClassPro apostrophe corruption**: iClassPro encodes apostrophes as `039` in some exports (e.g. `"Boy039s Level 1"`). The `PROGRAM_ALIASES` dict in `pdf_generator.py` includes these corrupted forms as aliases.

---

## Pain Points Discovered in Testing

These are the real-world failure modes found during stress testing. Know these before touching the parser.

### 1. iClassPro Discipline Column ≠ Class Name
The "Discipline" column in the XLS export says things like `"NEW Girls Recreational Gymnastics"` — not `"Level 1"`. This is an iClassPro internal label. It caused Level 1, Level 2, and Level 3 to all be undetectable from the discipline column alone. **Fix:** The parser now falls back to the tab name for both class name and program detection. Do not rely on the discipline column for program resolution.

### 2. Two Classes Same Day/Time → One Sheet
iClassPro merges two class sections (e.g. two Level 1 groups at 3:30pm Monday) into a single XLS sheet with two sets of header rows. The old parser turned this into one result with 12 students, or just missed the second group entirely. **Fix:** The parser now loops over all header groups within a sheet and creates one `evalResult` per group. A/B suffixes are added automatically.

**Action required from gym side:** If there are two separate groups that need distinct labels (e.g. "Level 2 A" vs "Level 2 B"), the class names in iClassPro must include A/B in the name. Otherwise both show as "Level 2" and the auto-suffix is the only differentiator.

### 3. iClassPro Strips Pipe Characters From Tab Names
Class names formatted as `"Level 1 | Monday | 3:30pm"` in iClassPro come through the XLS export as `"Level 1  Monday  330pm"`. The parser handles space-separated format, so this works, but it's not obvious. If parsing breaks, check whether separator detection is failing on an unusual tab name format.

### 4. api/pdf_generator.py Is the Only Copy — Edit There Only
There is one `pdf_generator.py`: `api/pdf_generator.py`. This is what Vercel runs in production and what local Flask (`app.py`) imports via `sys.path.insert`. There is no root-level copy. Do not create one. All edits go to `api/pdf_generator.py` only.

### 5. Unknown Program = Silent Drop
If a class tab name doesn't contain any keyword that PROGRAM_MAP recognizes, the class is silently skipped. No error is shown. The PDF simply has fewer pages. This is the most dangerous silent failure — the manager gets a PDF and may not notice a class is missing. If the page count is lower than expected, check for unusual class names in iClassPro that don't contain standard program keywords.

### 6. Score Mapping Is Positional
Scores are mapped by position (column index) within each header group. If the iClassPro export ever inserts extra columns, changes column order, or adds blank columns before student data, all scores will map to the wrong students or fail silently. The parser assumes student data starts at column index 4.

### 7. Vercel Timeout Risk (Untested at Scale)
Vercel serverless functions have a 10-second default timeout. Converting 24 classes in one request has not caused timeouts in testing, but very large exports (50+ classes, hundreds of students) have not been stress-tested. If timeouts occur, the fix would be batching classes into multiple requests.

---

## What Would Break This Tool

Ordered by likelihood.

| Risk | Trigger | Symptom | Fix |
|------|---------|---------|-----|
| **Missing pages** | Class tab name has no program keyword (e.g. class named "Tumbling" not "Preschool Tumbling") | Fewer PDF pages than expected, no error | Rename class in iClassPro to include program keyword, or add alias to PROGRAM_MAP |
| **Wrong class label on PDF** | parseTabName fails to extract program segment (unusual tab format) | PDF header shows iClassPro internal name like "Girls Recreational Gymnastics" | Fix tab name format in iClassPro to follow `Program \| Day \| Time \| Ages` |
| **Duplicate groups merged or missing** | Two classes at same day/time, iClassPro puts them on one sheet | Only one group appears, or scores cross-contaminate between groups | Already fixed in current parser — would break again if parser is reverted |
| **All scores wrong** | iClassPro adds/removes columns before student data | Stars in wrong positions or all empty | Check column structure of raw XLS, update column offset constant in parser |
| **New program not recognized** | iClassPro class uses program name not in PROGRAM_MAP | Classes silently skipped | Add aliases to PROGRAM_MAP in index.html and resolve_program() in pdf_generator.py |
| **Logo missing** | Logo PNG file deleted or renamed in `public/logos/` | PDF generates with blank logo area (no crash) | Re-add logo file with correct filename matching GYMS dict |
| **Backend/frontend out of sync** | New program added to one but not both | PDF generates with wrong skills, or frontend sends program name backend doesn't know | Always update both files together, redeploy |
| **iClassPro export format change** | iClassPro updates their XLS export structure | Parser fails silently or produces garbage | Re-examine raw XLS structure and update column constants |
| **Vercel timeout** | Very large export (50+ classes) | Download never happens, no error message shown | Batch into multiple smaller exports |
