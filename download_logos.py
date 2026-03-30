"""
Download gym logos from ActiveCampaign CDN for PDF generation.
Run once: python download_logos.py
"""
import os, urllib.request

LOGOS = {
    'est_logo.png': 'https://content.app-us1.com/g55L0q/2025/05/13/eff29c8b-abb0-4595-aec3-ccf32d7e1940.png',
    'hga_logo.png': 'https://content.app-us1.com/vqqEDb/2026/01/30/49f475ed-3dae-48f9-a3c7-1f5d98ccc26b.png',
    'oas_logo.png': 'https://content.app-us1.com/ARRBG9/2026/01/30/217676e8-f661-411a-8ea8-9a94373c5bb0.png',
    'rba_logo.png': 'https://content.app-us1.com/obb1M5/2026/01/30/d5e1a9ce-e8aa-4a21-a886-523d5a12bbd5.png',
    'rbk_logo.png': 'https://content.app-us1.com/6ddeKB/2026/01/30/ebe5ff82-80c1-419b-b15d-6db55c974a7c.png',
    'sgt_logo.png': 'https://content.app-us1.com/OoonDm/2026/01/09/7d45241b-ea60-4305-8ed9-fcbdafc7906f.png',
    'tig_logo.png': 'https://content.app-us1.com/J77wkW/2025/08/21/d817cd8d-ad31-4897-88b1-bc74d19334bb.png',
}

logo_dir = os.path.join(os.path.dirname(__file__), 'logos')
os.makedirs(logo_dir, exist_ok=True)

for filename, url in LOGOS.items():
    path = os.path.join(logo_dir, filename)
    if os.path.exists(path):
        print(f"  OK {filename} (already exists)")
        continue
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
        })
        with urllib.request.urlopen(req) as resp:
            with open(path, 'wb') as f:
                f.write(resp.read())
        print(f"  DL {filename}")
    except Exception as e:
        print(f"  FAIL {filename}: {e}")

print(f"\nDone. Logos in: {logo_dir}")
