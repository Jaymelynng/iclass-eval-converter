# Usage Tracking — Future Build

Parked Apr 22 2026. Jayme wants per-manager usage visibility eventually — who's using the tool, who isn't.

## Level 1: Vercel Analytics (5 min, free)
- Anonymous page views / daily visitor count / geography
- Answers: "Is it getting used?"

## Level 2: Per-gym PDF logging (~1 hour)
- Log every POST to /generate-pdf: timestamp, gym code, mode, class count
- Answers: "Which gyms are generating, which aren't"
- Still anonymous (no per-manager data)
- Can go to a file or a Supabase table

## Level 3: Full login + per-manager history (~3 hours) — WHAT JAYME ACTUALLY WANTS
- Each manager logs in once
- Every action tied to them: PDF generation, panel open, What's New views
- Per-manager weekly/monthly reports ("Megan at CPF used it 12 times last week")
- Solves the cross-device "seen" badge problem (stored server-side, not localStorage)
- Requires: Supabase auth, login screen, linking managers to iClass accounts

## Starting point when we pick this up
- Add Vercel Analytics first (5 min freebie)
- Then Level 2 to scope the DB schema
- Then Level 3 builds on Level 2's table

