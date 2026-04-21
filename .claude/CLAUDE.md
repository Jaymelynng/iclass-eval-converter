# Star Chart Converter — Project Instructions

## WHAT THIS IS

evalconvert.com — converts iClassPro XLS skill evaluation exports into branded PDF star charts for 10 gymnastics gyms. Launched April 6, 2026. First tool every person at the company uses. **No downtime allowed.**

**797 classes renamed. All 10 gyms verified and live. 11,132+ data points stress-tested with zero errors.**

---

## ⚠️ CURRENT STATE (as of April 16, 2026 — morning session) ⚠️

### Production = STILL THE OLD VERSION
**evalconvert.com on Vercel has NOT been updated.** Production is running the original colors/layout. All session work is local-only.

### Local working tree = iteration-04 installed with split wrapper
- `api/pdf_generator.py` is now iter-04 (`option-A-page1-horizontal`) + added `generate_split_pdf()` wrapper
- Horizontal-text criteria rendering when ≤16 columns (split mode)
- Rotated-text criteria when >16 columns (single-page all-4-events mode)
- Auto-picks which to use based on column count
- Frontend has simplified 2-button PAGE LAYOUT picker (ALL 4 EVENTS | VAULT+BARS/BEAM+FLOOR)
- All 10 gyms × 6 programs × both modes: render clean, no errors

### Project cleanup done
- `iterations/` folder contains iter-03-clean-lines + iter-04 (both A and B options) for reference
- `test-output/` folder contains all old CRR_TEST_*, PREVIEW_*, TEST_* artifacts
- Project root is clean of test PDFs/PNGs
- `.vercelignore` updated to exclude `iterations/`, `layout-tests/`, `test-output/`

### Backups
- `api/pdf_generator_BACKUP_20260416_003745.py` — original 978-line version
- `api/pdf_generator_BACKUP_20260416_104559_before_iter03.py` — Jayme's 6990-line rewrite (pre iter-03)
- `api/pdf_generator_BACKUP_20260416_105246_before_iter04.py` — iter-03 state (pre iter-04)

---

## CRITICAL RULES — READ BEFORE DOING ANYTHING

### 1. ALWAYS verify skill trees against the source of truth
TWO reference files in `auditing tools source of truth and results/`:
- `Skills_Stars_Audit_Reference (1).xlsx` — full skill tree (skills, event assignment, order)
- `approved shorthand criteria for star chart.xlsx` — **approved PDF wording per criterion** (Preschool, Junior, Advanced Junior, Level 1, Level 2, Level 3). Status column flags Same / Abbreviated / Wrong. Advanced Junior = copy Level 1 verbatim.

NEVER do structure-only checks. Compare EVERY criterion text and order against BOTH files EVERY TIME.

### 2. Class name format — ages STAY in iClassPro
Format in iClassPro: `Program | Day | Time | Ages`
Format on PDF: `Program | Day | Time` (converter strips ages automatically)
**Ages STAY in the class name in iClassPro. ALWAYS.**

### 3. Carry over ALL notes from old class names
Any parenthetical — (NEW!), (Invite Only), (homeschool), etc. — MUST appear in the new name at the end. No exceptions.

### 4. A/B suffixes — use common sense
Only add A/B when there are genuinely multiple classes of the same program at the same day+time.

### 5. After EVERY git push — check Vercel
Test evalconvert.com after every deploy. Localhost working does NOT mean production works. The `.vercelignore` and `sys.path.insert` in `api/generate-pdf.py` are CRITICAL.

### 6. Never use "Rise Athletics"
The gyms have no umbrella brand name.

### 7. Jayme is non-technical — talk plainly
Don't ask UX/decision questions in long lists when the user is stressed. Just propose ONE thing and ship it. Ask before reverting if direction changes.

---

## ARCHITECTURE (as of April 16, 2026 local state)

- **Frontend:** `public/index.html` (~2050 lines) — single file, vanilla JS + SheetJS, no build step. Has the new "PAGE LAYOUT" 4-button picker above the existing two panels.
- **Backend:** `api/pdf_generator.py` (~6990 lines, was ~978) — SINGLE source of truth. **HUGE rewrite from Jayme** with embedded base64 logos, new brand-color system, A-B-A-B event alternation, `generate_split_pdf()` for multi-page event splits.
- **API glue:** `api/generate-pdf.py` — Vercel serverless handler, accepts new `pageEvents` parameter
- **Local dev:** `app.py` — Flask server on port 5050. Accepts `pageEvents`. **Reverted save-dialog change** — back to `as_attachment=True` (original behavior).
- **Hosting:** Vercel — static + Python serverless
- **Config:** `vercel.json`, `.vercelignore` (MUST exist, excludes large folders)
- **Backup:** `api/pdf_generator_BACKUP_20260416_003745.py`

### Score mapping is POSITIONAL
Scores map by column position in the XLS, NOT by criteria text. Order and count matter. Wording differences don't.

---

## NEW IN THIS SESSION (April 15-16, 2026) — LOCAL ONLY

### 1. Brand-unified color system (Jayme's rewrite)
Each gym has a single `brand` color in GYMS dict that drives event/skill/program/safety blocks. WCAG contrast math documented per gym. CRR pink darkened to `#bf0f6e` for readability. EST navy lightened to `#1a4a7a` to separate from charcoal top bar. TIG flipped to navy as brand because orange fails contrast on event strips.

### 2. A-B-A-B event alternation
VAULT + BEAM = brand color. BARS + FLOOR = medium gray `#646262`. Skill-name strip uses 40% darker brand for Vault/Beam, near-black `#1a1a1a` for Bars/Floor. Boys apparatus follow same warm/cool pattern.

### 3. `generate_split_pdf()` function
Located at line ~6878 in pdf_generator.py. Signature:
```python
generate_split_pdf(gym_code, classes, page_events, mode='eval')
```
`page_events` is a list of event-name lists, one per page. Examples:
- `[['VAULT','BARS'], ['BEAM','FLOOR']]` → 2 pages, V+B then B+F
- `[['VAULT'],['BARS'],['BEAM'],['FLOOR']]` → 4 pages, one event each

### 4. Embedded base64 logos
All 10 gym logos baked into pdf_generator.py as base64 PNG strings (LOGO_B64 dict). NO MORE Vercel file path issues. The `_get_logo_image()` function decodes them. The `api/logos/` and `public/logos/` directories may still exist but are no longer the primary source.

### 5. Frontend layout picker (4 preset buttons)
Above the two existing panels (Convert + Print Blank). 2x2 grid:
- ALL 4 EVENTS (1 page · default)
- VAULT + BARS / BEAM + FLOOR (2 pages)
- VAULT + BEAM / BARS + FLOOR (2 pages)
- VAULT + FLOOR / BARS + BEAM (2 pages)

Picks one preset → frontend sends `pageEvents` array → backend routes to `generate_split_pdf` instead of `generate_multi_pdf`.

JS state: `_currentLayout` (default `'all4'`). Function: `setLayout(id)`. Mapping: `LAYOUT_PRESETS` dict.

### 6. Select All / Clear All for blank score sheets
Two buttons at the top of the Print Blank panel. Calls `toggleAllBlankPrograms(true|false)`.

### 7. Multi-line criteria wrapping at larger fonts
Old logic shrunk font to fit single line first → tiny text. New `_split_crit()` algorithm tries multi-line wrapping at requested size FIRST, only shrinks if 4-line wrap also fails. Result: 50%+ bigger criteria text when columns are wide (fewer events selected).

Font size now scales: `_size = min(13.0, max(7.5, COL_W * 0.32))`. Up to 4 lines per criterion.

### 8. Per-gym top_bar_h and logo_size overrides
GYMS dict supports `top_bar_h` and `logo_size` per gym. CRR uses 64/60 for bigger logo readability.

---

## SCORING SYSTEM

**Old:** 0-5 star subjective rating per skill (deprecated)
**New:** 3 binary criteria per skill + 1 mastery star. Each criterion = 0 (gray circle) or 1 (colored star). Mastery = all 3 done together 3x in a row (gold star).

### iClassPro Skill Ratings Settings
- Stars: 1
- 0 star = Working on it
- 1 star = Got it!
- This is GLOBAL — applies to ALL programs.

### Old-format programs (Boys Level, IGT)
Each skill = 1 bubble. `has_mastery: False` in code.

---

## PROGRAMS SUPPORTED

| Program | Students/Page | Safety Section | has_mastery |
|---------|:---:|:---:|:---:|
| Preschool | 6 | Yes | True |
| Junior | 6 | Yes | True |
| Advanced Junior | 8 | No | True |
| Level 1 | 8 | No | True |
| Level 2 | 8 | No | True |
| Level 3 | 8 | No | True |
| Boys Level 1 (HGA only) | 8 | No | False |
| Boys Level 2 (HGA only) | 8 | No | False |
| Boys Level 3 (HGA only) | 8 | No | False |

### NOT supported (silently skipped)
Ninja, Tumbling, IGT, Specialty Class, Cheer.

---

## GYM STATUS (production = April 6, 2026)

ALL 10 GYMS VERIFIED AND LIVE on evalconvert.com (production):
CCP, CPF, CRR, EST, HGA, OAS, RBA, RBK, SGT, TIG

The local working tree has the rewrite installed but **NOT YET DEPLOYED**.

---

## OUTSTANDING WORK (next session)

### Top priority — Push Jayme's rewrite to production
1. Clean up test files in project root (`CRR_TEST_*.pdf`, `PREVIEW_*.png`, `TEST_after_textfix.*`)
2. Visually verify all 10 gyms render cleanly with the new colors (use generate_multi_pdf for each)
3. Verify event-split for all common combos
4. Commit + push to Vercel
5. Smoke test evalconvert.com after deploy (per the April 5 incident rule)

### Open feature requests (Jayme described, not yet built)
1. **Coach name on PDF header** — auto-pulled from the iClass Skill Evaluation PDF (which has "Coach Name - Date" in the header). Approach: user uploads BOTH the XLS (scores) and the PDF (coach extraction). XLS stays primary data source. Build time: ~3 hours.
2. **Trial / first-day / makeup indicators** — these are ICONS on the iClass Roll Sheet PDF (NOT in the eval PDF). 20+ embedded images per page. Would need icon-matching logic. Build time: ~5 hours. **HARDER — fragile to iClass changes.**
3. **Timestamps for staleness alerts** — the Skill Eval PDF has per-score timestamps. Could power "this kid hasn't been evaluated on Vault in 6 weeks" alerts. Build time: ~10 hours including UI.
4. **Color tweak** — Jayme wants the download buttons / event chip colors to be visually different from the top bar / panel header colors. Currently both pull from `--c1`. May need new CSS variable per gym for "secondary brand."

### Known issue — Save dialog popping up
When downloading a PDF, Edge browser shows a save dialog. Likely cause: Edge setting "Ask me what to do with each download." Tried `as_attachment=False` to fix, reverted because it didn't help. **Next session: ask Jayme to check Edge → Settings → Downloads → toggle off "Ask me what to do with each download."**

---

## FOLDER STRUCTURE

```
/Star Chart Converter
  .claude/
    launch.json              # Local dev configs (port 8765 static, port 5050 Flask)
    CLAUDE.md                # THIS FILE
  api/
    generate-pdf.py          # Vercel serverless handler — accepts pageEvents
    pdf_generator.py         # 6990-line rewrite — embedded logos, brand-unified, generate_split_pdf
    pdf_generator_BACKUP_20260416_003745.py  # Original 978-line version, restore if disaster
    logos/                   # Logos still here but pdf_generator.py uses embedded base64 now
  public/
    index.html               # 2050 lines, has new layout picker + Select All buttons
    sop-guide.html
    logos/
    sop-steps/
  renaming-tools/
    [10 gym folders + audit folders]
  auditing tools source of truth and results/
    Skills_Stars_Audit_Reference (1).xlsx
  stress tests/
  STAR CHART MEETINGS AND PLANNING TRANSCRIPTS/
  HOW_IT_WORKS.md
  TECHNICAL_DOCUMENTATION.md
  PROGRAM_NAME_REFERENCE.md
  V2_PLAN.md
  SESSION_HANDOFF.md         # April 16, 2026 session handoff — read this first
```

---

## INTERACTION PATTERNS

### Things Jayme repeatedly corrects:
1. **Don't do structure-only skill tree checks.** Always compare against the source of truth spreadsheet.
2. **Ages stay in iClassPro class names.** The converter strips them from the PDF only.
3. **Carry over parenthetical notes.**
4. **A/B suffixes need common sense.** No lone letters.
5. **Don't say "Rise Athletics."**
6. **Don't ask questions you should know.** Read the project files first.
7. **When you say you'll update .md files, actually do it.**
8. **The scoring system is binary.** Don't ask "does this program have criteria?" — they all do.
9. **Hidden classes need warning notes on the rename tool.**
10. **Rename tool format: `Program | Day | Time | Ages (note if any)`.**
11. **DON'T overcomplicate UX.** When Jayme is stressed, propose ONE clear thing. Don't list 4 options with sub-questions.
12. **Don't assume two PDFs need both XLS and itself for the same data.** The Skill Eval PDF has coach name; the XLS doesn't. Use both for different fields.

### What works well:
- Building rename tools from CSVs/JSONs
- Verifying skill trees (when actually done properly)
- Building fixer tools for iClassPro errors
- XLS→PDF pipeline code changes
- Stress testing

---

## V2 PLAN (UPDATED)

Original V2 plan was Supabase admin panel. Some of that work has been overtaken:

- **Phase 1 (Gym Manager):** Still pending — gyms are still hardcoded in pdf_generator.py
- **Phase 2 (Keyword Manager):** Still pending
- **Phase 3 (Skill Editor):** Still pending — skills still hardcoded
- **Phase 4 (PDF Design Controls):** Partially done — Jayme's rewrite added per-gym brand color, top_bar_h, logo_size overrides. Still hardcoded in Python though.
- **Phase 5 (Individual Student Star Chart):** Still pending

See `V2_PLAN.md` for details.

---

## KNOWN ISSUES & FOLLOW-UPS

### Per-gym issues: See `renaming-tools/MANAGER-FOLLOWUPS.md`

### CPF custom programs
- "Dynamite Girls" and "Hot Shots" = Advanced Junior in iClassPro. Need follow-up on naming.

### Boys programs (HGA only)
- Boys Level 1 working. Boys Level 2/3 need correct disciplines assigned.

### Programs not covered
Ninja, Tumbling, IGT, Specialty Class, Cheer — managers print these separately.

### Vercel incident (April 5, 2026)
Import path broke + bundle exceeded 250MB. Fixed with sys.path.insert and .vercelignore. See `stress tests/incident-log.html`.
