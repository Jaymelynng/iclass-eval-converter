# Star Chart Converter — Project Instructions

## WHAT THIS IS

evalconvert.com — converts iClassPro XLS skill evaluation exports into branded PDF star charts for 10 gymnastics gyms. Launched April 6, 2026. First tool every person at the company uses. No downtime allowed.

**797 classes renamed. All 10 gyms verified and live. 11,132+ data points stress-tested with zero errors.**

---

## CRITICAL RULES — READ BEFORE DOING ANYTHING

### 1. ALWAYS verify skill trees against the source of truth
File: `auditing tools source of truth and results/Skills_Stars_Audit_Reference (1).xlsx`
NEVER do structure-only checks (counting skills, checking for duplicates). That misses truncated text, swapped order, garbage prefixes. Compare EVERY criterion text and order against the source of truth EVERY TIME.

### 2. Class name format — ages STAY
Format in iClassPro: `Program | Day | Time | Ages`
Format on PDF: `Program | Day | Time` (converter strips ages automatically)
**Ages STAY in the class name. ALWAYS. Never remove them. Never build tools without them.**

### 3. Carry over ALL notes from old class names
If the old name has ANY parenthetical — (NEW!), (Invite Only), (homeschool), (Closing due to low enrollment) — it MUST appear in the new name at the end. No exceptions.

### 4. A/B suffixes — use common sense
Only add A/B when there are genuinely multiple classes of the same program at the same day+time. If a class has a lone "B" with no "A" at that time, DROP the letter. Don't blindly carry over letters.

### 5. After EVERY git push — check Vercel
Test evalconvert.com after every deploy. Localhost working does NOT mean production works. Check Vercel logs within 2 minutes. The .vercelignore and sys.path.insert in api/generate-pdf.py are CRITICAL.

### 6. Never use "Rise Athletics"
The gyms have no umbrella brand name. Never use "Rise Athletics" anywhere.

---

## ARCHITECTURE

- **Frontend:** `public/index.html` (~1968 lines) — single file, vanilla JS + SheetJS, no build step
- **Backend:** `api/pdf_generator.py` (~978 lines) — SINGLE source of truth, never create a root copy
- **API glue:** `api/generate-pdf.py` — Vercel serverless handler, MUST have sys.path.insert
- **Local dev:** `app.py` — Flask server on port 5050
- **Hosting:** Vercel — static + Python serverless
- **Config:** `vercel.json`, `.vercelignore` (MUST exist, excludes large folders)

### Score mapping is POSITIONAL
Scores map by column position in the XLS, NOT by criteria text. Wording differences (lowercase, missing accents, hyphens vs em-dashes) don't matter. ORDER and COUNT matter.

---

## SCORING SYSTEM

**Old:** 0-5 star subjective rating per skill
**New:** 3 binary criteria per skill + 1 mastery star. Each criterion = 0 (gray circle) or 1 (colored star). Mastery = all 3 done together 3x in a row (gold star). "Consistently" = 3 times in a row. Stars earned in any order.

### iClassPro Skill Ratings Settings
- Stars: 1
- 0 star = Working on it
- 1 star = Got it!
- This is GLOBAL — applies to ALL programs. Cannot have different scales per program.

### Old-format programs (Boys Level, IGT)
Each skill = 1 bubble. No 3-criteria breakdown, no mastery. `has_mastery: False` in code.

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
Ninja, Tumbling, IGT, Specialty Class, Cheer, and any class without a recognized program keyword.

---

## FOLDER STRUCTURE

```
/Star Chart Converter
  .claude/
    launch.json              # Local dev server config (port 8765)
    CLAUDE.md                # THIS FILE
  api/
    generate-pdf.py          # Vercel serverless handler
    pdf_generator.py         # PDF engine — SINGLE source of truth
    logos/                   # Logos duplicated here for Vercel access
  public/
    index.html               # Entire frontend
    sop-guide.html           # Printable SOP guide
    logos/                   # Gym logos
    sop-steps/               # Walkthrough screenshots
  renaming-tools/
    CCP/ CPF/ CRR/ EST/ HGA/ OAS/ RBA/ RBK/ SGT/ TIG/
    CLASSES ON THE BACK END AND SETTINGS/   # online-settings JSONs
    CLASSES ON THE FRONT END/               # class-pricing JSONs
    MANAGER-FOLLOWUPS.md                    # Issues to communicate to managers
    hidden-classes-all-gyms.txt             # All hidden classes per gym
  auditing tools source of truth and results/
    Skills_Stars_Audit_Reference (1).xlsx   # THE source of truth for all skills
  stress tests/
    stress-test-notes.html                  # Test documentation
    incident-log.html                       # Production incidents + timeline
  STAR CHART MEETINGS AND PLANNING TRANSCRIPTS/  # Kim + Jayme meeting notes
  HOW_IT_WORKS.md
  TECHNICAL_DOCUMENTATION.md
  PROGRAM_NAME_REFERENCE.md
  V2_PLAN.md
```

---

## GYM STATUS (as of April 6, 2026)

ALL 10 GYMS VERIFIED AND LIVE:
CCP, CPF, CRR, EST, HGA, OAS, RBA, RBK, SGT, TIG

---

## AGES PER GYM (vary — don't assume)

| Gym | Preschool | Junior | Level 1+ |
|-----|-----------|--------|----------|
| CCP | 3-4 | 5-6 | 7+ |
| CPF | 3-4 | 4.5-5 | 6+ (L1/L2), 7+ (L3) |
| CRR | 3-4 | 4.5-5 | 6+ |
| EST | 3-4 | 5-6 | 7+ |
| HGA | 3-4 | 5-6 | 7+ |
| OAS | 3-4 | 5-6 | 7+ |
| RBA | 3-4 | 5-6 | 7+ |
| RBK | 3-4 | 5-6 | 7+ |
| SGT | 3-4 | 5-6 | 7+ |
| TIG | 3-4 | 5-6 | 7+ |

---

## INTERACTION PATTERNS — WHAT I KEEP GETTING WRONG

### Things Jayme has corrected me on repeatedly:
1. **Don't do structure-only skill tree checks.** Always compare against the source of truth spreadsheet. I missed real errors (truncated text, swapped order, garbage prefixes) multiple times because I only checked for duplicates and missing mastery.
2. **Ages stay in the class name.** I removed them twice and had to undo it. The converter strips ages from the PDF. The ages are for iClassPro display.
3. **Carry over parenthetical notes.** Notes like (NEW!), (Invite Only), (homeschool) must be in the new name. I missed this on RBK, CPF, and CRR.
4. **A/B suffixes need common sense.** If only one class at a time slot, no letter — even if the old name has one. I missed lone letters on CRR, CPF, HGA.
5. **Don't say "Rise Athletics."** The gyms have no umbrella brand name. I used it in the SOP guide and had to remove it.
6. **Don't ask questions I should know the answer to.** If the information is in the project files, read them before asking.
7. **When I say I'll update .md files, actually do it.** I agreed multiple times to create this CLAUDE.md and never did.
8. **The scoring system is binary.** Every program uses the same 3-criteria + mastery structure. Don't ask "does this program have criteria?" — they all do. Boys programs are the exception (has_mastery: False).
9. **Hidden classes from the customer portal need warning notes on the rename tool.** Not just in a separate list — ON the tool itself, on each hidden class.
10. **The rename tool's new names need the correct format with ages AND notes.** Format: `Program | Day | Time | Ages (note if any)`

### What works well:
- Building rename tools from class list CSVs/JSONs
- Verifying skill trees against the source of truth (when I actually do it properly)
- Building fixer tools for iClassPro errors
- Handling the XLS→PDF pipeline code changes
- Stress testing and verification

---

## KNOWN ISSUES & FOLLOW-UPS

### Per-gym issues: See `renaming-tools/MANAGER-FOLLOWUPS.md`

### CPF custom programs
- "Dynamite Girls" and "Hot Shots" = Advanced Junior in iClassPro. Need follow-up on naming.

### Boys programs (HGA only)
- Boys Level 1 working. Boys Level 2/3 need correct disciplines assigned.
- Different apparatus (Floor, Mushroom/Pommel, Vault, P Bars, Bars).
- `has_mastery: False` — each skill is one bubble, no 3-criteria breakdown.

### Programs not covered
Ninja, Tumbling, IGT, Specialty Class, Cheer — managers print these separately from iClassPro PDF.

### Vercel incident (April 5, 2026)
Import path broke + bundle exceeded 250MB. Fixed with sys.path.insert and .vercelignore. See `stress tests/incident-log.html`.

---

## V2 PLAN

Move all hardcoded config to Supabase with admin panel:
- Phase 1: Gym Manager
- Phase 2: Keyword Manager
- Phase 3: Skill Editor
- Phase 4: PDF Design Controls
- Phase 5: Individual Student Star Chart (parent-facing)

See `V2_PLAN.md` for details.
