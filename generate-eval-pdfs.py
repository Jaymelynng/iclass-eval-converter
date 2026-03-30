"""
Generate Eval Grid PDFs from iClassPro Roll Sheet exports.
Drop in a roll sheet PDF → get polished eval grids with student names, blank scoring bubbles.

Usage:
    python generate-eval-pdfs.py [roll_sheet.pdf] [GYM_CODE]

Example:
    python generate-eval-pdfs.py Roll_Sheets_03-23-2026.pdf CCP
"""

import pymupdf, json, math, os, sys, urllib.request, tempfile
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import numpy as np

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
script_dir = os.path.dirname(os.path.abspath(__file__))

roll_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.expanduser('~'), 'Downloads', 'Roll_Sheets_03-23-2026.pdf')
gym_code = sys.argv[2] if len(sys.argv) > 2 else 'CCP'

# ═══════════════════════════════════════════════════════════════════════
# GYM DATA
# ═══════════════════════════════════════════════════════════════════════
GYMS = {
    'HGA': {
        'name': 'Houston Gymnastics Academy',
        'display': 'HOUSTON GYMNASTICS ACADEMY',
        'c1': '#c91724', 'c2': '#262626', 'c3': '#d0d0d8',
        'logo': 'https://content.app-us1.com/vqqEDb/2026/01/30/49f475ed-3dae-48f9-a3c7-1f5d98ccc26b.png',
    },
    'CCP': {
        'name': 'Capital Gymnastics Cedar Park',
        'display': 'CAPITAL GYMNASTICS  —  Cedar Park',
        'c1': '#1f53a3', 'c2': '#bf0a30', 'c3': '#d8d8d8',
        'logo': 'https://capgymcpk.activehosted.com/content/d66m4q/2026/02/19/f11d01b7-bbdb-4de8-b5f3-8eeacc4f3017.png',
    },
    'CPF': {
        'name': 'Capital Gymnastics Pflugerville',
        'display': 'CAPITAL GYMNASTICS  —  Pflugerville',
        'c1': '#1f53a3', 'c2': '#bf0a30', 'c3': '#d8d8d8',
        'logo': 'https://content.app-us1.com/MaaPRn/2025/09/07/fc44683b-d5a8-4547-97f5-91d46e4e647e.png',
    },
    'CRR': {
        'name': 'Capital Gymnastics Round Rock',
        'display': 'CAPITAL GYMNASTICS  —  Round Rock',
        'c1': '#ff1493', 'c2': '#c0c0c0', 'c3': '#3c3939',
        'logo': 'https://content.app-us1.com/511e9V/2025/09/07/54697754-fdd0-452b-9275-f1ac2421e995.png',
    },
    'EST': {
        'name': 'Estrella Gymnastics',
        'display': 'ESTRELLA GYMNASTICS',
        'c1': '#011837', 'c2': '#666666', 'c3': '#100f0f',
        'logo': 'https://content.app-us1.com/g55L0q/2025/05/13/eff29c8b-abb0-4595-aec3-ccf32d7e1940.png',
    },
    'OAS': {
        'name': 'Oasis Gymnastics',
        'display': 'OASIS GYMNASTICS',
        'c1': '#3eb29f', 'c2': '#3e266b', 'c3': '#e7e6f0',
        'logo': 'https://content.app-us1.com/ARRBG9/2026/01/30/217676e8-f661-411a-8ea8-9a94373c5bb0.png',
    },
    'RBA': {
        'name': 'Rowland Ballard Atascocita',
        'display': 'ROWLAND BALLARD  —  Atascocita',
        'c1': '#1a3c66', 'c2': '#c52928', 'c3': '#739ab9',
        'logo': 'https://content.app-us1.com/obb1M5/2026/01/30/d5e1a9ce-e8aa-4a21-a886-523d5a12bbd5.png',
    },
    'RBK': {
        'name': 'Rowland Ballard Kingwood',
        'display': 'ROWLAND BALLARD  —  Kingwood',
        'c1': '#1a3c66', 'c2': '#c52928', 'c3': '#739ab9',
        'logo': 'https://content.app-us1.com/6ddeKB/2026/01/30/ebe5ff82-80c1-419b-b15d-6db55c974a7c.png',
    },
    'SGT': {
        'name': 'Scottsdale Gymnastics',
        'display': 'SCOTTSDALE GYMNASTICS',
        'c1': '#c72b12', 'c2': '#e6e6e6', 'c3': '#000000',
        'logo': 'https://content.app-us1.com/OoonDm/2026/01/09/7d45241b-ea60-4305-8ed9-fcbdafc7906f.png',
    },
    'TIG': {
        'name': 'Tigar Gymnastics',
        'display': 'TIGAR GYMNASTICS',
        'c1': '#f57f20', 'c2': '#0a3651', 'c3': '#7fc4e0',
        'logo': 'https://content.app-us1.com/J77wkW/2025/08/21/d817cd8d-ad31-4897-88b1-bc74d19334bb.png',
    },
}

gym = GYMS[gym_code]

# ═══════════════════════════════════════════════════════════════════════
# PARSE ROLL SHEET
# ═══════════════════════════════════════════════════════════════════════
print(f"Parsing roll sheet: {roll_path}")
doc = pymupdf.open(roll_path)
classes = []
for i in range(doc.page_count):
    text = doc[i].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    program = instructor = schedule = ''
    students = []
    class_display = ''
    for line in lines:
        if line.startswith('Instructors:'): instructor = line.replace('Instructors:','').strip()
        if line.startswith('Program:'): program = line.replace('Program:','').strip()
        if line.startswith('Schedule:'): schedule = line.replace('Schedule:','').strip()
        if '|' in line and 'Ages' in line and 'CLA-' not in line:
            class_display = line.strip()
    in_stu = False
    for line in lines:
        if line == 'Student':
            in_stu = True
            continue
        if in_stu:
            if line.startswith('CLA-') or line.startswith('Page ') or ('|' in line and 'Ages' in line): break
            if ',' in line:
                try: int(line); continue
                except: students.append(line.strip())
    pu = program.upper()
    prog = None
    if 'PRESCHOOL' in pu: prog = 'Preschool'
    elif 'JUNIOR' in pu and 'ADV' not in pu: prog = 'Junior'
    elif 'ADV' in pu and 'JUNIOR' in pu: prog = 'Advanced Junior'
    elif 'GIRLS L1' in pu or 'LEVEL 1' in pu: prog = 'Girls Level 1'
    elif 'GIRLS L2' in pu or 'LEVEL 2' in pu: prog = 'Girls Level 2'
    elif 'GIRLS L3' in pu or 'LEVEL 3' in pu: prog = 'Girls Level 3'
    if prog:
        classes.append({
            'program': prog,
            'instructor': instructor,
            'schedule': schedule,
            'display': class_display,
            'students': students
        })

print(f"  Found {len(classes)} eval classes from {doc.page_count} roll sheet pages")

# ═══════════════════════════════════════════════════════════════════════
# LOAD SKILL DATA
# ═══════════════════════════════════════════════════════════════════════
with open(os.path.join(script_dir, 'all-programs-prepped.json'), encoding='utf-8') as f:
    ALL_SKILLS = json.load(f)

# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD + PREP LOGO
# ═══════════════════════════════════════════════════════════════════════
logo_dir = os.path.join(script_dir, 'logos')
os.makedirs(logo_dir, exist_ok=True)
logo_path = os.path.join(logo_dir, f'{gym_code}_logo_transparent.png')

if not os.path.exists(logo_path):
    print(f"  Downloading logo for {gym_code}...")
    raw_path = os.path.join(logo_dir, f'{gym_code}_logo_raw.png')
    try:
        req = urllib.request.Request(gym['logo'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            with open(raw_path, 'wb') as f:
                f.write(resp.read())
        # Remove black background
        img = Image.open(raw_path).convert('RGBA')
        data = np.array(img)
        black_mask = (data[:,:,0] < 40) & (data[:,:,1] < 40) & (data[:,:,2] < 40)
        data[:,:,3][black_mask] = 0
        Image.fromarray(data).save(logo_path)
        print(f"  Logo saved: {logo_path}")
    except Exception as e:
        print(f"  WARNING: Could not download logo: {e}")
        logo_path = None
else:
    print(f"  Using cached logo: {logo_path}")


# ═══════════════════════════════════════════════════════════════════════
# COLOR SYSTEM — derives event colors from gym brand
# ═══════════════════════════════════════════════════════════════════════
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(max(0,min(255,int(r))), max(0,min(255,int(g))), max(0,min(255,int(b))))

def lighten(hex_color, amount=0.85):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount)

def darken(hex_color, amount=0.3):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(r * (1 - amount), g * (1 - amount), b * (1 - amount))

def midtone(hex_color, amount=0.4):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount)

# Build event color palette from gym's c1 (primary) and c2 (secondary)
c1, c2 = gym['c1'], gym['c2']

EV_DARK = {
    'VAULT': colors.HexColor(c2),
    'BARS':  colors.HexColor(darken(c1, 0.3)),
    'BEAM':  colors.HexColor(c1),
    'FLOOR': colors.HexColor(darken(c2, 0.3)),
    'SAFETY': colors.HexColor('#8a7a2a'),
}
EV_MED = {
    'VAULT': colors.HexColor(midtone(c2, 0.4)),
    'BARS':  colors.HexColor(midtone(c1, 0.4)),
    'BEAM':  colors.HexColor(midtone(c1, 0.55)),
    'FLOOR': colors.HexColor(midtone(c2, 0.5)),
    'SAFETY': colors.HexColor('#b0a050'),
}
EV_LIGHT = {
    'VAULT': colors.HexColor(lighten(c2, 0.92)),
    'BARS':  colors.HexColor(lighten(c1, 0.92)),
    'BEAM':  colors.HexColor(lighten(c1, 0.94)),
    'FLOOR': colors.HexColor(lighten(c2, 0.94)),
    'SAFETY': colors.HexColor('#fdfbe8'),
}

# Fixed brand constants
BRAND_BLUE     = colors.HexColor(c1)
BRAND_RED      = colors.HexColor(c2)
BRAND_GRAY     = colors.HexColor(gym['c3'])
CCP_GRAY       = colors.HexColor('#d8d8d8')
CCP_GRAY_MID   = colors.HexColor('#b0b0b0')
CCP_GRAY_DK    = colors.HexColor('#555566')
WHITE          = colors.HexColor('#ffffff')
GOLD           = colors.HexColor('#C9A43C')
GOLD_LIGHT     = colors.HexColor('#FFF8DC')


# ═══════════════════════════════════════════════════════════════════════
# STAR DRAWING
# ═══════════════════════════════════════════════════════════════════════
def draw_star(c, cx, cy, r, fill_color, stroke_color, lw=1.0):
    outer = r
    inner = r * 0.42
    pts = []
    for k in range(10):
        angle = math.pi/2 + k * math.pi/5
        rad = outer if k % 2 == 0 else inner
        pts.append((cx + rad * math.cos(angle), cy + rad * math.sin(angle)))
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.setFillColor(fill_color)
    c.setStrokeColor(stroke_color)
    c.setLineWidth(lw)
    c.drawPath(p, fill=1, stroke=1)


# ═══════════════════════════════════════════════════════════════════════
# BUILD ONE EVAL PAGE
# ═══════════════════════════════════════════════════════════════════════
def build_eval_page(c, cls, skills, subtitle_text):
    """
    Draws one landscape-letter eval grid page.
    skills = list of skill dicts (excluding SAFETY — safety handled in footer)
    cls = class dict with 'students' list
    """
    page_size = landscape(letter)
    W, H = page_size
    MARGIN = 18

    # Filter out SAFETY from main grid — it goes in footer
    main_skills = [s for s in skills if s['evt'] != 'SAFETY']
    safety_skill = next((s for s in skills if s['evt'] == 'SAFETY'), None)

    NUM_SKILLS = len(main_skills)
    NUM_COLS = NUM_SKILLS * 4
    NUM_ROWS = 6

    # Get student names (max 6 per page, format: "First L.")
    raw_students = cls['students']
    student_names = []
    for name in raw_students:
        if ',' in name:
            parts = name.split(',')
            last = parts[0].strip()
            first = parts[1].strip() if len(parts) > 1 else ''
            student_names.append(f"{first} {last[0]}.")
        else:
            student_names.append(name)

    # Split into pages of 6
    pages_of_students = []
    for i in range(0, len(student_names), 6):
        page = student_names[i:i+6]
        while len(page) < 6:
            page.append('')
        pages_of_students.append(page)
    if not pages_of_students:
        pages_of_students = [[''] * 6]

    for page_students in pages_of_students:
        USABLE_W = W - 2 * MARGIN
        USABLE_H = H - 2 * MARGIN

        # Heights
        TOP_BAR_H = 48
        FOOTER_H = 68
        EV_HDR_H = 15
        SK_HDR_H = 14
        STAR_LBL_H = 11
        CRIT_H = 150

        CONTENT_TOP = H - MARGIN - TOP_BAR_H
        CONTENT_BOT = MARGIN + FOOTER_H
        HEADER_H = EV_HDR_H + SK_HDR_H + CRIT_H + STAR_LBL_H
        DATA_TOP = CONTENT_TOP - HEADER_H
        DATA_H = DATA_TOP - CONTENT_BOT
        ROW_H = DATA_H / NUM_ROWS

        # Widths
        NAME_W = 68
        GRID_LEFT = MARGIN + NAME_W
        GRID_RIGHT = W - MARGIN
        GRID_W = GRID_RIGHT - GRID_LEFT
        COL_W = GRID_W / NUM_COLS if NUM_COLS > 0 else 18

        # Event spans
        ev_spans = {}
        for i, sk in enumerate(main_skills):
            ev = sk['evt']
            if ev not in ev_spans:
                ev_spans[ev] = [i * 4, i * 4 + 3]
            else:
                ev_spans[ev][1] = i * 4 + 3

        def ev_x(col): return GRID_LEFT + col * COL_W
        def row_y(row): return DATA_TOP - (row + 1) * ROW_H

        # ── WHITE BACKGROUND ──
        c.setFillColor(WHITE)
        c.rect(MARGIN, MARGIN, USABLE_W, USABLE_H, fill=1, stroke=0)

        # ── TOP BAR ──
        bar_y = H - MARGIN - TOP_BAR_H
        c.setFillColor(BRAND_BLUE)
        c.rect(MARGIN, bar_y, USABLE_W, TOP_BAR_H, fill=1, stroke=0)
        c.setFillColor(BRAND_RED)
        c.rect(MARGIN, bar_y + TOP_BAR_H - 3, USABLE_W, 3, fill=1, stroke=0)
        c.setFillColor(CCP_GRAY)
        c.rect(MARGIN, bar_y, USABLE_W, 2, fill=1, stroke=0)

        # Logo
        if logo_path and os.path.exists(logo_path):
            logo_size = 40
            logo_x = MARGIN + 4
            logo_y = bar_y + TOP_BAR_H / 2 - logo_size / 2
            try:
                c.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto')
            except:
                pass

        # Gym name
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(W / 2, bar_y + 31, gym['display'])

        # Subtitle
        c.setFillColor(CCP_GRAY); c.setFont('Helvetica', 8.5)
        c.drawCentredString(W / 2, bar_y + 16, subtitle_text)

        # ── EVENT BANDS ──
        ev_top = CONTENT_TOP
        for ev, (sc, ec) in ev_spans.items():
            x = ev_x(sc); w = (ec - sc + 1) * COL_W
            c.setFillColor(EV_DARK.get(ev, BRAND_BLUE))
            c.rect(x, ev_top - EV_HDR_H, w, EV_HDR_H, fill=1, stroke=0)
            c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 7.5)
            c.drawCentredString(x + w / 2, ev_top - EV_HDR_H + 5, ev)

        # ── SKILL NAMES ──
        sk_top = ev_top - EV_HDR_H
        for i, sk in enumerate(main_skills):
            ev = sk['evt']
            x = ev_x(i * 4); w = 4 * COL_W
            c.setFillColor(EV_MED.get(ev, BRAND_BLUE))
            c.rect(x, sk_top - SK_HDR_H, w, SK_HDR_H, fill=1, stroke=0)
            c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 6.5)
            # Use short name if available, otherwise truncate full name
            short_name = sk.get('short', sk['name'])
            if len(short_name) > 20:
                short_name = short_name[:18] + '..'
            c.drawCentredString(x + w / 2, sk_top - SK_HDR_H + 4.5, short_name)

        # ── CRITERIA (rotated text) ──
        crit_top = sk_top - SK_HDR_H
        for i, sk in enumerate(main_skills):
            ev = sk['evt']
            crits_all = sk['crit'] + ['3× in a row']
            # Pad to exactly 4 if fewer than 3 criteria
            while len(crits_all) < 4:
                crits_all.insert(-1, '')  # insert blanks before final

            for j in range(4):
                col_x = ev_x(i * 4 + j)
                is_final = (j == 3)
                crit = crits_all[j] if j < len(crits_all) else ''

                bg = EV_DARK.get(ev, BRAND_BLUE) if is_final else EV_LIGHT.get(ev, WHITE)
                c.setFillColor(bg)
                c.rect(col_x, crit_top - CRIT_H, COL_W, CRIT_H, fill=1, stroke=0)

                # Hairline divider
                c.setStrokeColor(colors.HexColor('#cccccc') if not is_final else EV_MED.get(ev, BRAND_BLUE))
                c.setLineWidth(0.3)
                c.line(col_x, crit_top - CRIT_H, col_x, crit_top)

                # Rotated text
                c.saveState()
                c.translate(col_x + COL_W / 2, crit_top - CRIT_H / 2)
                c.rotate(90)
                fg = WHITE if is_final else EV_DARK.get(ev, BRAND_BLUE)
                size = 8.0 if is_final else 7.5
                c.setFillColor(fg); c.setFont('Helvetica-Bold', size)
                display_crit = crit[:38] if crit else ''
                c.drawCentredString(0, -size / 3, display_crit)
                c.restoreState()

        # ── STAR LABELS ──
        starlbl_top = crit_top - CRIT_H
        for i, sk in enumerate(main_skills):
            ev = sk['evt']
            for j, star in enumerate(['★1', '★2', '★3', '★F']):
                col_x = ev_x(i * 4 + j); is_final = (j == 3)
                c.setFillColor(GOLD if is_final else EV_LIGHT.get(ev, WHITE))
                c.setStrokeColor(colors.HexColor('#cccccc')); c.setLineWidth(0.3)
                c.rect(col_x, starlbl_top - STAR_LBL_H, COL_W, STAR_LBL_H, fill=1, stroke=1)
                if is_final:
                    draw_star(c, col_x + COL_W / 2, starlbl_top - STAR_LBL_H / 2 + 0.5, 5.5, WHITE, WHITE, lw=0)
                else:
                    c.setFillColor(EV_DARK.get(ev, BRAND_BLUE))
                    c.setFont('Helvetica-Bold', 6.5)
                    c.drawCentredString(col_x + COL_W / 2, starlbl_top - STAR_LBL_H + 3.5, star)

        # ── NAME COLUMN HEADER ──
        c.setFillColor(BRAND_BLUE)
        c.rect(MARGIN, CONTENT_TOP - EV_HDR_H, NAME_W, EV_HDR_H, fill=1, stroke=0)
        c.setFillColor(BRAND_BLUE)
        c.rect(MARGIN, DATA_TOP, NAME_W, HEADER_H - EV_HDR_H, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(MARGIN + NAME_W / 2, starlbl_top - STAR_LBL_H / 2 - 2, 'NAME')

        # ── DATA ROWS ──
        NAME_ZONE_H = 8
        for row in range(NUM_ROWS):
            ry = row_y(row)
            c.setFillColor(WHITE if row % 2 == 0 else colors.HexColor('#f7f8fa'))
            c.rect(MARGIN, ry, USABLE_W, ROW_H, fill=1, stroke=0)

            # Student name
            sname = page_students[row] if row < len(page_students) else ''
            c.setFillColor(colors.HexColor('#222222')); c.setFont('Helvetica-Bold', 10)
            c.drawCentredString(MARGIN + NAME_W / 2, ry + ROW_H / 2 - 4, sname)

            # Bubbles
            bubble_zone_top = ry + ROW_H
            bubble_zone_bottom = ry + NAME_ZONE_H
            bubble_cy = (bubble_zone_top + bubble_zone_bottom) / 2

            for i in range(NUM_SKILLS):
                for j in range(4):
                    col_x = ev_x(i * 4 + j)
                    cx = col_x + COL_W / 2
                    r = min(COL_W * 0.31, (ROW_H - NAME_ZONE_H) * 0.35)
                    is_final = (j == 3)

                    if is_final:
                        # ★F always star shape — gray outline (blank)
                        draw_star(c, cx, bubble_cy, r * 1.2, WHITE, CCP_GRAY_MID, lw=1.2)
                    else:
                        # ★1/2/3 = circle outline (blank)
                        c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(1.2)
                        c.circle(cx, bubble_cy, r, fill=1, stroke=1)

        # ── GRID LINES ──
        # Skill group dividers (data rows)
        for i in range(NUM_SKILLS + 1):
            x = ev_x(i * 4)
            c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.7)
            c.line(x, CONTENT_BOT, x, DATA_TOP)

        # Skill dividers in header
        for i in range(NUM_SKILLS + 1):
            x = ev_x(i * 4)
            c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.35)
            c.line(x, starlbl_top - STAR_LBL_H, x, ev_top - EV_HDR_H)

        # Star sub-dividers
        for col in range(NUM_COLS):
            if col % 4 != 0:
                x = ev_x(col)
                c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.18)
                c.line(x, starlbl_top - STAR_LBL_H, x, sk_top - SK_HDR_H)

        # Horizontal row lines
        c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.3)
        for row in range(NUM_ROWS + 1):
            y = DATA_TOP - row * ROW_H
            c.line(MARGIN, y, W - MARGIN, y)

        # Bottom data separator
        spare_y = DATA_TOP - 6 * ROW_H
        c.setStrokeColor(colors.HexColor(midtone(c1, 0.5))); c.setLineWidth(0.8)
        c.line(MARGIN, spare_y, W - MARGIN, spare_y)

        # Structural lines
        c.setStrokeColor(BRAND_BLUE); c.setLineWidth(1.4)
        c.line(MARGIN + NAME_W, CONTENT_BOT, MARGIN + NAME_W, CONTENT_TOP)
        c.line(MARGIN, DATA_TOP, W - MARGIN, DATA_TOP)

        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
        c.line(MARGIN, sk_top, W - MARGIN, sk_top)
        c.line(MARGIN, crit_top, W - MARGIN, crit_top)
        c.line(MARGIN, starlbl_top, W - MARGIN, starlbl_top)

        c.setStrokeColor(colors.HexColor(midtone(c1, 0.5))); c.setLineWidth(1.0)
        c.line(MARGIN, CONTENT_TOP, W - MARGIN, CONTENT_TOP)

        # ══ SAFETY FOOTER ══
        ft_y = MARGIN
        ft_h = FOOTER_H
        CCP_BLUE_XLT = colors.HexColor(lighten(c1, 0.95))

        c.setFillColor(CCP_BLUE_XLT)
        c.rect(MARGIN, ft_y, USABLE_W, ft_h, fill=1, stroke=0)
        c.setStrokeColor(BRAND_BLUE); c.setLineWidth(1.2)
        c.line(MARGIN, ft_y + ft_h, W - MARGIN, ft_y + ft_h)

        # "SAFETY" label panel
        SAF_LBL_W = 52
        c.setFillColor(BRAND_BLUE)
        c.rect(MARGIN, ft_y, SAF_LBL_W, ft_h, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(MARGIN + SAF_LBL_W / 2, ft_y + ft_h - 13, 'SAFETY')
        c.setFillColor(CCP_GRAY); c.setFont('Helvetica', 4.8)
        c.drawCentredString(MARGIN + SAF_LBL_W / 2, ft_y + ft_h - 22, 'assessed')
        c.drawCentredString(MARGIN + SAF_LBL_W / 2, ft_y + ft_h - 29, 'each class')

        c.setStrokeColor(BRAND_RED); c.setLineWidth(1.2)
        c.line(MARGIN + SAF_LBL_W, ft_y, MARGIN + SAF_LBL_W, ft_y + ft_h)

        # Safety criteria key
        SAF_KEY_W = 146
        key_x = MARGIN + SAF_LBL_W + 5
        saf_labels = [('★1', 'Follows directions'), ('★2', 'Stays with group'),
                      ('★3', 'Hands to self'), ('★F', '3× in a row')]
        if safety_skill:
            for i, crit in enumerate(safety_skill['crit'][:3]):
                saf_labels[i] = (f'★{i+1}', crit)

        row_h_key = (ft_h - 10) / 4
        for idx, (star, crit) in enumerate(saf_labels):
            ky = ft_y + ft_h - 6 - (idx + 1) * row_h_key
            is_f = (idx == 3)
            c.setFillColor(GOLD if is_f else BRAND_BLUE)
            c.setFont('Helvetica-Bold', 7)
            c.drawString(key_x, ky + row_h_key / 2 - 2, star)
            c.setFillColor(BRAND_RED if is_f else CCP_GRAY_DK)
            c.setFont('Helvetica-Bold' if is_f else 'Helvetica', 6.5)
            c.drawString(key_x + 18, ky + row_h_key / 2 - 2, crit)

        # Divider
        saf_grid_x = MARGIN + SAF_LBL_W + SAF_KEY_W + 6
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.7)
        c.line(saf_grid_x - 2, ft_y + 4, saf_grid_x - 2, ft_y + ft_h - 4)

        # 6 athlete safety columns
        N_SAF = 6
        saf_total_w = W - MARGIN - saf_grid_x
        saf_col_w = saf_total_w / N_SAF
        NAME_H_SAF = 13
        STAR_H_SAF = 10
        BUB_H_SAF = ft_h - NAME_H_SAF - STAR_H_SAF - 6

        for col in range(N_SAF):
            sx = saf_grid_x + col * saf_col_w
            c.setFillColor(CCP_BLUE_XLT if col % 2 == 0 else WHITE)
            c.rect(sx, ft_y, saf_col_w, ft_h, fill=1, stroke=0)

            # Athlete label
            aname = page_students[col] if col < len(page_students) and page_students[col] else f'Athlete {col + 1}'
            c.setFillColor(colors.HexColor('#222222')); c.setFont('Helvetica-Bold', 6.5)
            # Truncate if too long
            display_name = aname if len(aname) <= 12 else aname[:10] + '..'
            c.drawCentredString(sx + saf_col_w / 2, ft_y + ft_h - 8, display_name)

            # Name underline
            c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
            c.line(sx + 3, ft_y + ft_h - NAME_H_SAF + 1, sx + saf_col_w - 3, ft_y + ft_h - NAME_H_SAF + 1)

            # Star labels
            sub_w = saf_col_w / 4
            star_label_y = ft_y + 5 + BUB_H_SAF
            for j, lbl in enumerate(['★1', '★2', '★3', '★F']):
                bx = sx + j * sub_w + sub_w / 2
                if j == 3:
                    draw_star(c, bx, star_label_y + 4, 4.5, GOLD, GOLD, lw=0)
                else:
                    c.setFillColor(BRAND_BLUE)
                    c.setFont('Helvetica-Bold', 6)
                    c.drawCentredString(bx, star_label_y + 1, lbl)

            # Bubbles (blank)
            bub_r = min(sub_w * 0.30, BUB_H_SAF * 0.40)
            bub_cy = ft_y + 5 + BUB_H_SAF / 2
            for j in range(4):
                bx = sx + j * sub_w + sub_w / 2
                if j == 3:
                    draw_star(c, bx, bub_cy, bub_r * 1.15, WHITE, CCP_GRAY_MID, lw=1.0)
                else:
                    c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.8)
                    c.circle(bx, bub_cy, bub_r, fill=1, stroke=1)

            if col > 0:
                c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.4)
                c.line(sx, ft_y + 3, sx, ft_y + ft_h - 3)

        # ── OUTER BORDER ──
        c.setStrokeColor(BRAND_BLUE); c.setLineWidth(2.0)
        c.rect(MARGIN, MARGIN, USABLE_W, USABLE_H, fill=0, stroke=1)
        c.setFillColor(BRAND_RED)
        c.rect(MARGIN, H - MARGIN - 3, USABLE_W, 3, fill=1, stroke=0)
        c.rect(MARGIN, MARGIN, USABLE_W, 3, fill=1, stroke=0)

        c.showPage()


# ═══════════════════════════════════════════════════════════════════════
# BUILD SHORT NAMES FOR SKILLS
# ═══════════════════════════════════════════════════════════════════════
# Map full skill names to short display names
SHORT_NAMES = {
    # Preschool
    'Run + Hurdle to Two-Foot Jump': 'RUN + HURDLE',
    'Front Support Forward Roll (with spot)': 'FWD ROLL ●',
    'Tuck Hang': 'TUCK HANG',
    'Walk Across Low Beam (Unassisted)': 'WALK BEAM',
    'Bear Crawl on Line': 'BEAR CRAWL',
    'Backward Walk with Coach': 'BWD WALK',
    'Monkey Jump Over Panel Mat': 'MONKEY JUMP',
    'Backward Handstand Walk Up (5 sec hold)': 'BWD HS WALK',
    'Forward Roll Down Wedge': 'FWD ROLL ▽',
    'Tabletop Hold': 'TABLETOP',
    # Junior
    'Run + Hurdle + Straight Jump to Panel Mat': 'RUN + HURDLE',
    'Pullover (with Mat)': 'PULLOVER',
    'Forward Roll': 'FWD ROLL',
    'Front Support (5 sec hold)': 'FRONT SUPPORT',
    'Walk Across Medium Beam (Unassisted)': 'WALK BEAM',
    'Lever (Floor)': 'LEVER',
    'Backward Walk on Low Beam': 'BWD WALK',
    'Cartwheel to Lunge': 'CARTWHEEL',
    'Lunge to Handstand (Mat Supported)': 'HANDSTAND',
    'Bridge (Feet Elevated)': 'BRIDGE',
    # Advanced Junior / L1 / L2 / L3 — add as needed
    'Straight Jump to Resi': 'STR JUMP',
    'Handstand Flatback': 'HS FLATBACK',
    'Kick Pullover': 'PULLOVER',
    'Cast': 'CAST',
    'Front Support Hold → Forward Roll Down': 'FS → ROLL',
    'Beam Mount': 'MOUNT',
    'Lever': 'LEVER',
    'Relevé Walk': 'RELEVÉ WALK',
    'Straight Jump': 'STR JUMP',
    'Straight Jump Dismount': 'DISMOUNT',
    'Handstand': 'HANDSTAND',
    'Cartwheel': 'CARTWHEEL',
    'Backward Roll': 'BWD ROLL',
    'Bridge (5 sec hold)': 'BRIDGE',
    'Chin-Up Pullover': 'PULLOVER',
    'Cast Back Hip Circle': 'CAST BHC',
    'Cast Off Dismount': 'CAST OFF',
    'Roll Down to Chin Hang': 'ROLL → CHIN',
    'Pivot Turn': 'PIVOT TURN',
    'Vertical Handstand': 'V. HANDSTAND',
    'Side Handstand Dismount': 'HS DISMOUNT',
    'Bridge Kickover': 'KICKOVER',
    'Round-Off Rebound': 'RO REBOUND',
    'Straight Arm Backward Roll': 'SA BWD ROLL',
    'Half Turn': 'HALF TURN',
    'Step Leap': 'STEP LEAP',
    'Front Handspring': 'FHS',
    'Glide Swing': 'GLIDE',
    'Pullover Cast Back Hip Circle': 'PO CAST BHC',
    'Sole Circle Dismount': 'SOLE CIRCLE',
    'Side Handstand 1/4 Turn Dismount': 'HS 1/4 DSMNT',
    'Split Jump': 'SPLIT JUMP',
    'Back Handspring': 'BHS',
    'Chassé Split Leap': 'SPLIT LEAP',
    'Full Turn': 'FULL TURN',
    'Back Walkover': 'BWO',
    'Handstand Flatback on Resi': 'HS FLATBACK',
}

def add_short_names(skills):
    """Add 'short' key to skill dicts based on SHORT_NAMES lookup."""
    for sk in skills:
        if 'short' not in sk:
            sk['short'] = SHORT_NAMES.get(sk['name'], sk['name'][:16].upper())
    return skills


# ═══════════════════════════════════════════════════════════════════════
# GENERATE ALL PAGES
# ═══════════════════════════════════════════════════════════════════════
out_path = os.path.join(script_dir, f'Eval_Grids_{gym_code}.pdf')
print(f"\nGenerating: {out_path}")

c_pdf = canvas.Canvas(out_path, pagesize=landscape(letter))

page_count = 0
for cls in classes:
    skills = ALL_SKILLS.get(cls['program'], [])
    if not skills:
        print(f"  WARNING: No skill data for program '{cls['program']}' — skipping")
        continue

    skills = add_short_names(skills)

    # Build subtitle from class info
    parts = []
    if cls['display']:
        # Parse the display line for class name/time
        dp = cls['display'].split('|')
        parts = [p.strip() for p in dp if p.strip()]
    if not parts:
        parts = [cls['program'], cls.get('schedule', '')]

    subtitle = '  ·  '.join(p for p in parts if p)

    build_eval_page(c_pdf, cls, skills, subtitle)
    page_count += 1
    print(f"  Page {page_count}: {cls['program']} — {len(cls['students'])} students")

c_pdf.save()
print(f"\nDone! {page_count} pages -> {out_path}")
print(f"Open the PDF and print it.")
