# Program Name Reference — iClassPro → Converter

Internal reference only. Documents exactly what class names the converter accepts and rejects.
Matching is **case-insensitive** and **substring-based** — the keyword just needs to appear anywhere in the class name.

---

## How Matching Works

1. The class tab name from the iClassPro XLS export is checked against the alias list
2. Matching is case-insensitive (`PRESCHOOL` = `preschool` = `Preschool`)
3. Matching is substring — the keyword just needs to exist anywhere in the name
4. Pipes (`|`) are stripped by iClassPro on export — the converter never sees them
5. If no alias matches → class is **silently skipped**, no error shown
6. Advanced Junior aliases are checked before Junior to prevent "junior" substring stealing the match

---

## What Passes (Frontend — index.html PROGRAM_MAP)

These are checked against the raw tab name from the XLS.

| Keyword in class name | Resolves to |
|---|---|
| ADVANCED JUNIOR | Advanced Junior |
| ADV JUNIOR | Advanced Junior |
| ADV JR | Advanced Junior |
| ADVJR | Advanced Junior |
| PRESCHOOL | Preschool |
| PRE-SCHOOL | Preschool |
| PRE SCHOOL | Preschool |
| GIRLS LEVEL 1 | Girls Level 1 |
| GIRLS LEVEL 2 | Girls Level 2 |
| GIRLS LEVEL 3 | Girls Level 3 |
| GIRLS L1 | Girls Level 1 |
| GIRLS L2 | Girls Level 2 |
| GIRLS L3 | Girls Level 3 |
| GL1 | Girls Level 1 |
| GL2 | Girls Level 2 |
| GL3 | Girls Level 3 |
| GIRLS 1 | Girls Level 1 |
| GIRLS 2 | Girls Level 2 |
| GIRLS 3 | Girls Level 3 |
| LEVEL 1 | Level 1 |
| LEVEL 2 | Level 2 |
| LEVEL 3 | Level 3 |
| LVL 1 | Level 1 |
| LVL 2 | Level 2 |
| LVL 3 | Level 3 |
| LEV1 | Level 1 |
| LEV2 | Level 2 |
| LEV3 | Level 3 |
| L1 | Level 1 |
| L2 | Level 2 |
| L3 | Level 3 |
| JUNIOR | Junior |
| JR | Junior |

---

## What Passes (Backend — api/pdf_generator.py PROGRAM_ALIASES)

These are checked against the iClassPro discipline column value (used as fallback).

| Keyword | Resolves to |
|---|---|
| preschool | Preschool |
| new preschool | Preschool |
| junior | Junior |
| new junior | Junior |
| advanced junior | Advanced Junior |
| adv junior | Advanced Junior |
| adv jr | Advanced Junior |
| new advanced junior | Advanced Junior |
| girls level 1 | Level 1 |
| level 1 | Level 1 |
| girls l1 | Level 1 |
| gl1 | Level 1 |
| lev1 | Level 1 |
| girls level 2 | Level 2 |
| level 2 | Level 2 |
| girls l2 | Level 2 |
| gl2 | Level 2 |
| lev2 | Level 2 |
| girls level 3 | Level 3 |
| level 3 | Level 3 |
| girls l3 | Level 3 |
| gl3 | Level 3 |
| lev3 | Level 3 |

---

## Frontend vs Backend Discrepancy

The frontend resolves `Girls Level 1/2/3` as separate programs with separate skill data.
The backend collapses them: `Girls Level 1` → `Level 1`, `Girls Level 2` → `Level 2`, etc.
They use the same PDF layout and skills. If these ever need different skill sets, both files must be updated.

The frontend also accepts `L1`, `L2`, `L3`, `LVL 1/2/3`, `Girls 1/2/3` — the backend does not. Frontend is the primary matcher so this is fine in practice, but worth knowing.

---

## What Gets Silently Skipped (No Error, No Warning)

Any class name that does not contain one of the accepted keywords above.
Common examples from gymnastics programs that would fail today:

| Class name typed in iClassPro | Result |
|---|---|
| Recreational / Rec | Skipped |
| Tots / Tiny Tots | Skipped |
| Youth | Skipped |
| Beginner | Skipped |
| Tumbling / Tumble | Skipped |
| Boys / MAG / Men's | Skipped |
| Teen / Adult | Skipped |
| Cheer / Cheerleading | Skipped |
| Acro / Acrobatics | Skipped |
| Dance | Skipped |
| Ninja | Skipped |
| Kinder / Kindergarten | Skipped |
| Mini / Mighty / Tiny | Skipped |
| Stars | Skipped |
| Bronze / Silver / Gold | Skipped |
| Level 4 / Level 5+ | Skipped |
| Level I / Level II / Level III | Skipped |
| Girls Level 4+ | Skipped |
| Ages 3-5 | Skipped |
| Coach name only | Skipped |
| Any non-English name | Skipped |

---

## Known Risks

**Silent wrong match** — more dangerous than a skip.
If a class is named `Junior 2`, it contains `junior` so it maps to Junior program, not Level 2.
The PDF generates with Junior skills and the manager has no idea. Always use the full program keyword.

**L1 / L2 / L3 are too short** — any class name containing "l1", "l2", or "l3" anywhere will match,
including unrelated names. Example: "Girls Team Level 1" → fine. But "Fall 1 Session" contains "l 1"
which may or may not match depending on spacing. These short aliases are the most likely to cause
false positives.

**Adding a new alias** — update BOTH files:
- `api/pdf_generator.py` → `PROGRAM_ALIASES` dict
- `public/index.html` → `PROGRAM_MAP` object

Missing one means local and production behave differently.

---

## Audit & Verification Record

**Audited by:** Jayme Gibson + Claude (Anthropic)
**Date:** April 2, 2026
**Final Result:** PASSED — Zero errors across all tests. 11,132+ data points verified.

---

### Overview

| Test | Scope | Data Type | Gyms | Result |
|---|---|---|---|---|
| Stress Test 1 | Level 1, 6 classes | All scores filled (100%) | All 10 | PASS |
| Stress Test 1B | Level 1, 6 classes | Mixed scores + mastery | All 10 | PASS |
| Stress Test 3 | All 7 programs, 47 pages | Real eval data, 216 students | CRR | 0 mismatches |
| 10-Gym Cross-Check | All 7 programs, 47 pages | Real eval data | All 10 | Identical |

**Grand Total: 11,132+ individual data points verified. Zero errors.**

---

### Score Rendering Rules

| Spreadsheet Value | Renders As | Meaning |
|---|---|---|
| Blank cell (criteria row) | Empty grey circle | Not Yet |
| 1 in a criteria row | Filled colored star | Earned |
| 1 in the mastery / 3x in a row row | Gold star | Skill Complete |
| Blank in mastery row | Empty grey circle | Not Yet / Not Mastered |

- Student names: iClassPro exports full names. Converter renders First Name + Last Initial only (e.g. "Elliana Jones" → "Elliana J.")
- Class names: iClassPro format "Level 1 Monday 330pm Ages 7" is normalized to "Level 1 | Monday | 3:30pm" on the PDF
- A/B splits: When iClassPro creates A/B classes at the same time slot, the converter renders them as separate pages

---

### Stress Test 1 — Level 1, All Criteria Filled

**Spreadsheet:** Stress Test 1 - Level1 Full Scores No Signoff.xlsx
**Score pattern:** Every criteria row = 1. Mastery rows = blank. Produces all filled stars, all empty mastery circles.

| Class | Students | Score Pattern |
|---|---|---|
| Level 1 \| Monday \| 3:30pm | 8 (test names) | All criteria = 1, all mastery = blank |
| Level 1 \| Monday \| 4:30pm | 8 (real names) | All criteria = 1, all mastery = blank |
| Level 1 \| Monday \| 5:30pm | 8 (real names) | All criteria = 1, all mastery = blank |
| Level 1 \| Monday \| 6:30pm | 6 (real names) | All criteria = 1, all mastery = blank |
| Level 1 A \| Monday \| 3:30pm | 8 (real names) | All criteria = 1, all mastery = blank |
| Level 1 B \| Monday \| 3:30pm | 7 (real names) | All criteria = 1, all mastery = blank |

**Total data points:** 1,980 earned (1s) + 720 blanks
**Output:** 10 gyms × 6 pages = 60 PDFs

**Verified:**
- All 10 gym names rendered correctly in headers
- All 6 class names parsed and formatted correctly
- A/B split at 3:30pm rendered as two separate pages
- All filled stars appear in correct gym color for each gym
- Mastery row shows empty circles where mastery = blank
- Student names display as first name + last initial only
- All 60 PDFs structurally identical except gym-specific branding

**RESULT: PASSED**

---

### Stress Test 1B — Level 1, Mixed Scores + Mastery

**Spreadsheet:** Stress Test 1B - Level1 Full Scores No Signoff.xlsx
**Same 6 classes and students as Stress Test 1.**

| Students 1–4 (Partial) | Students 5–8 (Full + Mastery) |
|---|---|
| Criteria 1 = 1, Criteria 2 = 1, Criteria 3 = blank, Mastery = blank | Criteria 1 = 1, Criteria 2 = 1, Criteria 3 = 1, Mastery = 1 |
| PDF: Star Star Circle Circle | PDF: Star Star Star GOLD Star |

**Total data points:** 1,890 earned (1s) + 810 blanks
**Output:** 10 gyms × 6 pages = 60 PDFs

**Verified:**
- Partial scores: C1 and C2 show as filled stars; C3 and mastery show as circles
- Full scores + mastery: all three criteria show as filled stars; mastery shows as gold star
- Gold stars are visually distinct from regular colored stars
- Mixed scoring within the same class renders correctly
- All 10 gyms consistent, all 60 PDFs verified

**RESULT: PASSED**

---

### Stress Test 3 — Real Eval Data, All Programs, Full Visual Audit

**Source:** Real CRR iClassPro export, April 2, 2026
**Spreadsheet:** stress test 3 with classes formatted.xlsx
**Output:** CRR_Evals_04022026.pdf (47 pages)
**Audit method:** 47 PNG images (one per page) compared cell-by-cell against spreadsheet. Every cell read left to right, top to bottom. No cells skipped.

| Program | Classes | Pages | Students | Skills/Student | Mismatches |
|---|---|---|---|---|---|
| Preschool | 5 | 7 (with splits) | 26 | 44 | 0 |
| Junior A | 4 | 6 (with splits) | 28 | 48 | 0 |
| Junior B | 4 | 6 (with splits) | 23 | 48 | 0 |
| Advanced Junior | 2 | 2 | 5 | 58 | 0 |
| Level 1 | 5 | 7 (with splits) | 47 | 58 | 0 |
| Level 2 | 5 | 9 (with splits) | 40 | 52 | 0 |
| Level 3 | 5 | 10 (with splits) | 47 | 52 | 0 |
| **TOTAL** | **30** | **47** | **216** | — | **0** |

**RESULT: 11,132 data points audited. ZERO errors. Every PDF matches its source spreadsheet exactly.**

---

### 10-Gym Cross-Validation

**Method:** Python/PyMuPDF extracted all text from all 47 pages of each gym PDF. Gym name headers stripped. Remaining content compared page-by-page against CRR baseline.

| Code | Gym Name | Pages | Name Correct | vs. Baseline |
|---|---|---|---|---|
| CCP | Capital Gymnastics - Cedar Park | 47 | YES | IDENTICAL |
| CPF | Capital Gymnastics - Pflugerville | 47 | YES | IDENTICAL |
| CRR | Capital Gymnastics - Round Rock | 47 | YES | BASELINE |
| EST | Estrella Gymnastics | 47 | YES | IDENTICAL |
| HGA | Houston Gymnastics Academy | 47 | YES | IDENTICAL |
| OAS | Oasis Gymnastics | 47 | YES | IDENTICAL |
| RBA | Rowland Ballard - Atascocita | 47 | YES | IDENTICAL |
| RBK | Rowland Ballard - Kingwood | 47 | YES | IDENTICAL |
| SGT | Scottsdale Gymnastics | 47 | YES | IDENTICAL |
| TIG | Tigar Gymnastics | 47 | YES | IDENTICAL |

Note: EST (Estrella) uses Navy + Grey only — no red. Special branding handled correctly.
Note: Branding colors not captured by text extraction. Star colors visually confirmed during Stress Tests 1 and 1B.

**RESULT: All 10 gyms — 47 pages each — identical structure. Only gym name header differs.**

---

### Final Summary

The Star Chart Converter has been exhaustively tested across:

- All 10 Rise Athletics gyms
- All 7 programs (Preschool, Junior A, Junior B, Advanced Junior, Level 1, Level 2, Level 3)
- All score types: blank (not yet), earned (star), mastery (gold star)
- Mixed scoring within a single class — different students, different patterns, same page
- Over-capacity multi-page classes (pg 1/2 and pg 2/2 splits)
- A/B/C class splits at the same time slot
- Real student data from actual iClassPro eval exports
- 11,132+ individual data points verified cell-by-cell against source spreadsheet
- Zero errors found

**The Star Chart Converter is verified and ready for production use across all 10 gyms.**
