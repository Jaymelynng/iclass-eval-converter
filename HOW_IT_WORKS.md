# Star Chart Converter — How It Works (Non-Technical Guide)

## What Is This?

The Star Chart Converter is a tool that takes the skill evaluation data from iClassPro and automatically turns it into a ready-to-print PDF score sheet — branded with your gym's colors and logo.

Instead of manually writing scores or filling in sheets by hand, you export one file from iClassPro, upload it here, and get a fully formatted PDF in about 2 seconds.

---

## The Problem It Solves

iClassPro stores evaluation scores digitally but can't print them in a clean, branded format that works well for coaches on the gym floor. This tool bridges that gap — it reads exactly what's in iClassPro and puts it into a beautiful one-page score sheet per class.

---

## The 10 Gyms

Each gym has its own brand colors and logo built in:

| Gym | Code | Colors |
|-----|------|--------|
| Capital Gymnastics — Cedar Park | CCP | Navy & Red |
| Capital Gymnastics — Pflugerville | CPF | Navy & Red |
| Capital Gymnastics — Round Rock | CRR | Dark Grey & Hot Pink |
| Estrella Gymnastics | EST | Dark Navy & Grey |
| Houston Gymnastics Academy | HGA | Red & Black |
| Oasis Gymnastics | OAS | Purple & Teal |
| Rowland Ballard — Atascocita | RBA | Dark Blue & Red |
| Rowland Ballard — Kingwood | RBK | Dark Blue & Red |
| Scottsdale Gymnastics | SGT | Orange & Black |
| Tigar Gymnastics | TIG | Orange & Teal |

The PDF automatically uses the right colors and logo for whichever gym you select — you don't set anything up.

---

## The 6 Programs

| Program | Who It's For | Safety Section |
|---------|-------------|----------------|
| Preschool | Youngest gymnasts | Yes |
| Junior | Next level up | Yes |
| Advanced Junior | Intermediate | No |
| Level 1 | Competitive track starts here | No |
| Level 2 | Competitive Level 2 | No |
| Level 3 | Competitive Level 3 | No |

The tool automatically detects which program the class is based on the class name in iClassPro. You don't have to select it manually.

---

## Step-by-Step: How to Use It

### 1. Export From iClassPro
- Go to your class evaluations in iClassPro
- Export the file as **XLS** (Excel format — this is required, not CSV or PDF)
- You can export multiple classes at once — each class will be its own page in the PDF

### 2. Open the Tool
- Go to the website link
- You'll see cards for all 10 gyms

### 3. Pick Your Gym
- Click your gym's card
- A window opens — the colors change to match your gym automatically

### 4. Upload the File
- Drag the XLS file into the box, or click to browse and select it
- The tool reads it instantly — no waiting

### 5. Download the PDF
- Click **CONVERT EVAL SCORES**
- The PDF downloads automatically in a few seconds
- One page per class — if you uploaded 4 classes, you get a 4-page PDF

### 6. Print
- Open the PDF and print on standard paper in **landscape** (horizontal) orientation

---

## What the PDF Shows

### Header (Top of Page)
- Gym logo in the corner
- Gym name in the center
- Class name, day of week, date, and class time directly below

> Example: `Preschool Gymnastics · Monday · 03/30/2026 · 3:30pm`

The day and time come from how you named the class in iClassPro. The tool reads the tab name automatically — as long as you name it something like `Preschool | Monday | 3:30pm | Ages 3-4` it will pick it up.

### The Grid (Main Area)
- **Left column:** Student names (first name + last initial)
- **Top rows:** Apparatus names (VAULT, BARS, BEAM, FLOOR), then skill names, then criteria
- **The bubbles:** One circle or star per criterion per student

The grid fits **6 students per page**.

### The Bubbles — What They Mean

| Symbol | Meaning |
|--------|---------|
| ○ Grey circle | Not scored yet — criterion not achieved |
| ★ Colored star | Student earned this criterion |
| ★ Gold star | Student achieved mastery (earned it 3 times in a row) |

When a coach goes into iClassPro and marks a student as having earned a skill, the next time you export and run it through the converter, that circle becomes a star.

### Safety Section (Preschool & Junior only)
At the bottom of the page, there's a separate section showing 3 safety behaviors assessed every class:
1. Follows directions
2. Stays with the group
3. Keeps hands to self

Same circle/star system as the main grid.

---

## Blank Score Sheets

You can also print blank sheets — no scores pre-filled, all empty circles. Use these when you want coaches to fill them in by hand during class.

To get blank sheets:
- Open any gym
- On the **right side** of the modal, select the program and how many copies you want
- Click print — you don't even need to upload a file

---

## How the Class Name Becomes the Header

This is important. The tool reads the **tab name** of the Excel sheet to figure out what to put in the PDF header. iClassPro names those tabs based on the class name you set.

**Format that works best:**
```
Preschool | Monday | 3:30pm | Ages 3-4
```

This becomes: `Preschool Gymnastics · Monday · 03/30/2026 · 3:30pm`

The tool also handles older formats like `Mon 330 Preschool 34 yrs`.

**Takeaway:** If you want the day and time to show on the PDF, include them in the iClassPro class name using the pipe format above.

---

## How Scores Flow From iClassPro Into Stars

1. Coach enters scores in iClassPro (marks criteria as earned)
2. You export the Class Evaluation Report as XLS
3. The tool reads the spreadsheet:
   - Finds each criterion for each skill
   - Checks which students have a score (1 = earned, 0 = not yet)
   - Also checks the "Puts it all together" row = the gold/final star
4. For each student + criterion: if earned → fills in a colored star, if not → leaves an empty circle

The data flows directly from iClassPro. No manual entry. No guessing.

---

## Troubleshooting

| What Happened | What to Do |
|---------------|-----------|
| File won't upload | Make sure it's saved as **.xlsx** from iClassPro (not CSV, not PDF) |
| Day/time not showing on PDF | Name your iClassPro classes using this format: `Program \| Day \| Time \| Ages` |
| Wrong program detected | Check the class name in iClassPro — it must contain a program keyword like "Preschool", "Junior", "Level 1", etc. The internal discipline type doesn't control this. |
| Scores aren't showing | Make sure you exported the **Class Evaluation Report**, not just a roster |
| PDF has empty student slots | That's normal — the sheet always has 6 rows; extra ones are left blank |
| Logo not showing | Contact the developer — the logo file may need to be updated for that gym |
| Colors look wrong | Make sure you selected the right gym card before uploading |
| Fewer pages than expected | One or more class names don't contain a recognized program keyword. Check the class names in iClassPro — if a class is named something like "Tumbling" or "Rec Gym" with no program word, the tool doesn't know which skills to use and skips that class silently. Rename to include the program name. |
| Two classes at the same time showing as one page | This was a known bug — it's been fixed. Each group now gets its own page. If you still see it, contact the developer. |
| Class name on PDF shows "Girls Recreational Gymnastics" | The tool couldn't read the program from the class name in iClassPro. Rename the class to include the program name (e.g. "Level 1 Monday 3:30pm Ages 7-8"). |
| Two pages both say "Level 2" with no A/B | Two sections were exported on the same sheet. The tool auto-adds A/B labels. If you want them labeled something specific (e.g. "Level 2 Comp" vs "Level 2 Rec"), add that distinction to the class name in iClassPro. |

---

## What Would Break This Tool

These are the things that, if they changed, would cause the tool to produce wrong output or skip classes entirely — with no error message.

| What Changes | What Breaks | How to Fix |
|-------------|------------|-----------|
| Class name in iClassPro doesn't include the program word | That class is silently skipped — no page in PDF | Always include the program in the class name: "Preschool", "Junior", "Level 1", "Level 2", "Level 3", "Advanced Junior" |
| Class name format changes drastically | Day/time may not parse, showing nothing in PDF header | Use this format: `Program \| Day \| Time \| Ages` |
| iClassPro changes how they export the XLS file | Scores or class names could land in wrong columns | Contact the developer — the parser would need to be updated |
| A new program is added in iClassPro that the tool doesn't know about | Classes silently skipped | Developer needs to add the new program to the tool |
| Two classes at the same time aren't distinctly named | Both pages show the same name with just A/B | Name them differently in iClassPro if you need different labels |
| Someone deletes or renames a logo file | PDF generates without a logo | Re-upload the correct logo file with the correct filename |

**The most common silent failure: a class that gets skipped with no error.** If your PDF has fewer pages than you expected, the first thing to check is the class name in iClassPro — it needs to include one of these words: `Preschool`, `Junior`, `Advanced Junior`, `Level 1`, `Level 2`, or `Level 3`.

---

## What This Tool Does NOT Do

- It does **not** connect directly to iClassPro (no live sync)
- It does **not** change anything in iClassPro
- It does **not** save anything — every PDF is generated fresh from the file you upload
- It does **not** store student data anywhere

Every time you run it, it reads the file and generates the PDF fresh. Nothing is stored.

---

## Tips

- **Export all classes at once** — the tool handles multiple classes in one file and creates one PDF with all pages
- **Landscape printing** — the sheets are wider than tall, make sure your printer is set to landscape
- **One gym at a time** — each XLS file should be for one gym's classes
- **Update scores in iClassPro first** — then export, then run through the converter to get the latest stars
- **Blank sheets for new classes** — if you haven't evaluated yet, use the blank grid option and fill in by hand
