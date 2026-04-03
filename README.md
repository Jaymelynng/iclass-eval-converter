# iClass Eval Converter — Star Chart PDF Generator

Converts iClassPro skill-evaluation XLS exports into branded, print-ready PDFs for 10 gyms and 6 training programs. Built with Python + ReportLab on the backend and plain HTML/JS on the frontend, deployed on Vercel.

---

## Quick links

| Doc | What's in it |
|-----|-------------|
| [HOW_IT_WORKS.md](HOW_IT_WORKS.md) | Non-technical guide — step-by-step for gym staff |
| [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) | Architecture, gym config, PDF layout details |
| [PROGRAM_NAME_REFERENCE.md](PROGRAM_NAME_REFERENCE.md) | Keyword → program mapping used by the parser |

---

## Running locally

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5050
```

`app.py` is a Flask dev server that uses the same `api/pdf_generator.py` that runs on Vercel, so local behaviour is identical to production.

---

## Project structure

```
├── app.py                  # Flask local dev server (port 5050)
├── requirements.txt        # flask>=3.0, reportlab>=4.0
├── vercel.json             # Vercel routing config
├── api/
│   ├── generate-pdf.py     # Vercel serverless handler (POST /generate-pdf)
│   ├── pdf_generator.py    # PDF engine — single source of truth
│   └── requirements.txt    # reportlab>=4.0 (Vercel reads this)
└── public/
    ├── index.html          # Entire frontend (HTML + CSS + JS)
    └── logos/              # Gym logo PNGs
```

> **Rule:** always edit `api/pdf_generator.py`. Never create a root-level copy.

---

## Deployment

This repository is connected to **Vercel** via the GitHub integration. Every push to `main` triggers an automatic production deploy — no manual `vercel` CLI command needed.

The GitHub Actions workflow (`.github/workflows/deploy.yml`) drives the deploy using three repository secrets that must be set in **Settings → Secrets and variables → Actions**:

| Secret | Where to find it |
|--------|-----------------|
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens |
| `VERCEL_ORG_ID` | Vercel → Account Settings → General → Your ID (or team ID) |
| `VERCEL_PROJECT_ID` | Vercel → Project → Settings → General → Project ID |

Pull-request pushes deploy to a **preview URL** (not production).

---

## CI

Every push and pull request runs `.github/workflows/ci.yml`, which:
1. Installs Python dependencies
2. Checks all Python files compile without errors (`python -m py_compile`)
