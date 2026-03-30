"""
pdf_generator.py
Generates branded gymnastics eval score sheet PDFs using ReportLab.
Called by app.py with parsed class data from the frontend.
"""

import math, io
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ── Page setup ──────────────────────────────────────────────────────
W, H       = landscape(letter)   # 792 x 612
MARGIN     = 18
USABLE_W   = W - 2*MARGIN
USABLE_H   = H - 2*MARGIN
NUM_ROWS   = 6

# ── Gym configuration ───────────────────────────────────────────────
GYMS = {
    'CCP': {
        'name':   'CAPITAL GYMNASTICS — Cedar Park',
        'logo':   'logos/CCP_logo_transparent.png',
        'blue':   '#1f53a3',
        'red':    '#bf0a30',
        'gray':   '#d8d8d8',
    },
    'CPF': {
        'name':   'CAPITAL GYMNASTICS — Pflugerville',
        'logo':   'logos/CCP_logo_transparent.png',
        'blue':   '#1f53a3',
        'red':    '#bf0a30',
        'gray':   '#d8d8d8',
    },
    'CRR': {
        'name':   'CAPITAL GYMNASTICS — Round Rock',
        'logo':   'logos/CCP_logo_transparent.png',
        'blue':   '#ff1493',
        'red':    '#2a2a2a',
        'gray':   '#3c3939',
    },
    'EST': {
        'name':   'Estrella Gymnastics',
        'logo':   'logos/est_logo.png',
        'blue':   '#011837',
        'red':    '#666666',
        'gray':   '#d8d8d8',
    },
    'HGA': {
        'name':   'Houston Gymnastics Academy',
        'logo':   'logos/hga_logo.png',
        'blue':   '#262626',
        'red':    '#c91724',
        'gray':   '#d0d0d8',
    },
    'OAS': {
        'name':   'Oasis Gymnastics',
        'logo':   'logos/oas_logo.png',
        'blue':   '#3e266b',
        'red':    '#3eb29f',
        'gray':   '#e7e6f0',
    },
    'RBA': {
        'name':   'Rowland Ballard — Atascocita',
        'logo':   'logos/rba_logo.png',
        'blue':   '#1a3c66',
        'red':    '#c52928',
        'gray':   '#739ab9',
    },
    'RBK': {
        'name':   'Rowland Ballard — Kingwood',
        'logo':   'logos/rbk_logo.png',
        'blue':   '#1a3c66',
        'red':    '#c52928',
        'gray':   '#739ab9',
    },
    'SGT': {
        'name':   'Scottsdale Gymnastics',
        'logo':   'logos/sgt_logo.png',
        'blue':   '#000000',
        'red':    '#c72b12',
        'gray':   '#e6e6e6',
    },
    'TIG': {
        'name':   'Tigar Gymnastics',
        'logo':   'logos/tig_logo.png',
        'blue':   '#0a3651',
        'red':    '#f57f20',
        'gray':   '#7fc4e0',
    },
}

# ── Skill definitions per program ────────────────────────────────────
# Each skill: {'event': str, 'short': str, 'criteria': [str, ...]}
# criteria list does NOT include the final star — that's always added automatically
# The criteria text must match EXACTLY what iClassPro exports (used for score mapping)

PROGRAMS = {
    'Preschool': {
        'has_safety': True,
        'footer_h': 68,
        'skills': [
            {'event':'VAULT','short':'RUN + HURDLE',  'criteria':['Runs into hurdle, no stopping','Hurdles 1 foot to land on both feet','Arms by ears in jump']},
            {'event':'BARS', 'short':'BAR FWD ROLL',   'criteria':['Unassisted front support for 3 sec','Looks at belly while rolling','Hands stay on bar until done']},
            {'event':'BARS', 'short':'TUCK HANG',    'criteria':['Holds for 3 sec','Knees above belly button','Arms by ears']},
            {'event':'BEAM', 'short':'WALK BEAM',    'criteria':['Chest up with arms out to the side','Steps heel to toe (front)','Walks across beam w/o wobbles']},
            {'event':'BEAM', 'short':'BEAR CRAWL',   'criteria':['Hands on the line','Feet on the line','Straight legs']},
            {'event':'BEAM', 'short':'BWD WALK',     'criteria':['Chest up with arms out to the side','Steps heel to toe (backward)','Eyes forward while walking back']},
            {'event':'FLOOR','short':'MONKEY JUMP',  'criteria':['Turns hands towards "favorite foot"','Jumps over panel mat w/o touching','Starts and finishes with arms up']},
            {'event':'FLOOR','short':'BWD HS WALK',  'criteria':['Walks up wall, hips over shoulders','Straight arms covering ears','Straight back']},
            {'event':'FLOOR','short':'FWD ROLL',   'criteria':['Starts in a pencil shape','Eyes on belly','Stands up without using hands']},
            {'event':'FLOOR','short':'TABLETOP',     'criteria':['Holds for 5 sec','Back flat, no sagging hips','Fingers facing feet']},
        ],
        'safety_criteria': ['Follows directions','Stays with the group','Keeps hands to self'],
    },
    'Junior': {
        'has_safety': True,
        'footer_h': 68,
        'skills': [
            {'event':'VAULT','short':'RUN + HURDLE + JUMP TO MAT','criteria':['Accelerates into hurdle, no stutter','Hurdles 1 foot, hits board with 2','Arms down on board, up in the air']},
            {'event':'BARS', 'short':'PULLOVER',      'criteria':['Chin at bar as feet walk above bar','Shifts hands, fingers forward','Holds front support, belly off bar']},
            {'event':'BARS', 'short':'FORWARD ROLL',  'criteria':['Tips forward, rolls w/o letting go','Feet and knees together','Lands on feet with control']},
            {'event':'BARS', 'short':'FRONT SUP HOLD','criteria':['Straight arms','Belly in, back rounded','Straight legs, toes pointed']},
            {'event':'BEAM', 'short':'WALK MED BEAM', 'criteria':['Chest up, arms out to the side','Steps heel to toe','Walks across beam w/o wobbles']},
            {'event':'BEAM', 'short':'LEVER (FLOOR)', 'criteria':['Lunge start & finish, no wobble','Back leg stays straight','Arms by ears']},
            {'event':'BEAM', 'short':'BWD WALK BEAM', 'criteria':['Chest up, arms out to the side','Steps heel to toe backward','Eyes forward while walking back']},
            {'event':'FLOOR','short':'CARTWHEEL',     'criteria':['Fav foot starts, opposite finishes','Straight legs','Legs pass through vertical']},
            {'event':'FLOOR','short':'LUNGE TO HANDSTAND (Mat Supported)',      'criteria':['Starts and finishes in a lunge','Straight legs, feet together at vert','Straight line from hands to toes']},
            {'event':'FLOOR','short':'FORWARD ROLL',  'criteria':['Continuous movement in the roll','Feet and knees together','Stands up without using hands']},
            {'event':'FLOOR','short':'BRIDGE ELEV',   'criteria':['Pushes up w/o moving hands or feet','Straight arms by ears','Holds for 3 sec']},
        ],
        'safety_criteria': ['Follows directions','Stays with the group','Keeps hands to self'],
    },
    'Advanced Junior': {
        'has_safety': False,
        'footer_h': 18,
        'skills': [
            {'event':'VAULT','short':'STRAIGHT JUMP', 'criteria':['Run accelerates into the hurdle','Arms down on the board, up in the air','Straight body and legs in the air']},
            {'event':'VAULT','short':'HS FLATBACK',   'criteria':['Feet come together at vertical handstand','Straight line from hands to toes at vertical','Lands flat on the mat as one piece']},
            {'event':'BARS', 'short':'KICK PULLOVER', 'criteria':['Chin stays at the bar until toes come over','Shifts hands, fingers forward to front sup','Straight legs throughout the skill']},
            {'event':'BARS', 'short':'CAST',          'criteria':['Straight arms throughout the skill','Legs straight and together','Straight line from shoulders to toes']},
            {'event':'BARS', 'short':'FS HOLD TO FWD ROLL','criteria':['Holds front support, straight arms','Chin to chest','Legs straight, lowers slowly to hang']},
            {'event':'BEAM', 'short':'BEAM MOUNT',    'criteria':['Jumps to front support, straight arms','Straight leg swings over, no touch','Stands up with arms by ears']},
            {'event':'BEAM', 'short':'LEVER',         'criteria':['Arms by ears throughout','Straight line fingers to back foot','Back leg stays straight']},
            {'event':'BEAM', 'short':'RELEVÉ WALK',   'criteria':['Heels stay off the beam the entire walk','Walks with straight legs','Chest up with arms out to the side']},
            {'event':'BEAM', 'short':'STRAIGHT JUMP', 'criteria':['Arms swing up/down on landing','Toes pointed in the air','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'STR JUMP DISM', 'criteria':['Arms swing up as feet leave beam','Straight line fingers to toes in air','Sticks safe landing position']},
            {'event':'FLOOR','short':'HANDSTAND',     'criteria':['Feet come together at vertical','Straight line from hands to toes','Straight legs in the air/arms stay by ears']},
            {'event':'FLOOR','short':'CARTWHEEL',     'criteria':['Legs pass through vertical','Second hand turned in','Arms stay by ears','Legs straight throughout','Opposite leg lunge finish']},
            {'event':'FLOOR','short':'BACKWARD ROLL', 'criteria':['Rolls with fingers pointing to shoulders','Continuous movement in the roll','Feet and knees together throughout']},
            {'event':'FLOOR','short':'BRIDGE 5 SEC',  'criteria':['Straight arms in the bridge','Head between the arms','Feet flat and together']},
        ],
    },
    'Level 1': {
        'has_safety': False,
        'footer_h': 18,
        'skills': [
            {'event':'VAULT','short':'STRAIGHT JUMP', 'criteria':['Run accelerates into the hurdle','Arms down on the board, up in the air','Straight body and legs in the air']},
            {'event':'VAULT','short':'HS FLATBACK',   'criteria':['Feet come together at vertical handstand','Straight line from hands to toes at vertical','Lands flat on the mat as one piece']},
            {'event':'BARS', 'short':'KICK PULLOVER', 'criteria':['Chin stays at the bar until toes come over','Shifts hands, fingers forward to front sup','Straight legs throughout the skill']},
            {'event':'BARS', 'short':'CAST',          'criteria':['Straight arms throughout the skill','Legs straight and together','Straight line from shoulders to toes']},
            {'event':'BARS', 'short':'FS HOLD TO FWD ROLL','criteria':['Holds front support, straight arms','Chin to chest','Legs straight, lowers slowly to hang']},
            {'event':'BEAM', 'short':'BEAM MOUNT',    'criteria':['Jumps to front support, straight arms','Straight leg swings over, no touch','Stands up with arms by ears']},
            {'event':'BEAM', 'short':'LEVER',         'criteria':['Arms by ears throughout','Straight line fingers to back foot','Back leg stays straight']},
            {'event':'BEAM', 'short':'RELEVÉ WALK',   'criteria':['Heels stay off the beam the entire walk','Walks with straight legs','Chest up with arms out to the side']},
            {'event':'BEAM', 'short':'STRAIGHT JUMP', 'criteria':['Arms swing up/down on landing','Toes pointed in the air','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'STR JUMP DISM', 'criteria':['Arms swing up as feet leave beam','Straight line fingers to toes in air','Sticks safe landing position']},
            {'event':'FLOOR','short':'HANDSTAND',     'criteria':['Feet come together at vertical','Straight line from hands to toes','Straight legs in the air/arms stay by ears']},
            {'event':'FLOOR','short':'CARTWHEEL',     'criteria':['Legs pass through vertical','Second hand turned in','Arms stay by ears','Legs straight throughout','Opposite leg lunge finish']},
            {'event':'FLOOR','short':'BACKWARD ROLL', 'criteria':['Rolls with fingers pointing to shoulders','Continuous movement in the roll','Feet and knees together throughout']},
            {'event':'FLOOR','short':'BRIDGE 5 SEC',  'criteria':['Straight arms in the bridge','Head between the arms','Feet flat and together']},
        ],
    },
    'Level 2': {
        'has_safety': False,
        'footer_h': 18,
        'skills': [
            {'event':'VAULT','short':'HS FLATBACK',       'criteria':['Arms down on board, up in the air','Straight line hands to toes at HS','Lands flat as one piece']},
            {'event':'BARS', 'short':'CHIN-UP PULLOVER',  'criteria':['Pulls chin to bar (min forehead ht)','Feet leave floor at the same time','Legs straight and together throughout']},
            {'event':'BARS', 'short':'CAST BACK HIP CIR', 'criteria':['Straight arms, shoulders lean back','Bar stays against thighs entire circle','Eyes on toes throughout the skill']},
            {'event':'BARS', 'short':'CAST OFF DISM',     'criteria':['Straight arms throughout the cast','Shoulders over bar before pushing away','Cast 45 below horizontal']},
            {'event':'BARS', 'short':'ROLL DN CHIN HANG', 'criteria':['Chin finishes above the bar','Holds tucked chin hang for 5 sec','Feet and knees together throughout']},
            {'event':'BEAM', 'short':'PIVOT TURN',        'criteria':['Stays in relevé lock the entire turn','Arms stay overhead the entire turn','Straight legs']},
            {'event':'BEAM', 'short':'VERTICAL HS',       'criteria':['Feet come together at vertical','Straight line from hands to toes','Arms stay by ears']},
            {'event':'BEAM', 'short':'SIDE HS DISM',      'criteria':['Holds HS 1 sec before falling','Straight line shoulder to toes in dism','Shoulders over beam from HS to fall']},
            {'event':'FLOOR','short':'BRIDGE KICKOVER',   'criteria':['Straight arms by ears','Legs stay straight through the split','One step from bridge hold to kickover']},
            {'event':'FLOOR','short':'ROUND-OFF REBOUND', 'criteria':['Legs together & straight in snap-down','Hands off floor before feet hit','Rebounds up & back immediately']},
            {'event':'FLOOR','short':'STR ARM BWD ROLL',  'criteria':['Pushes on pinkies at beginning of roll','Arms stay straight during the roll','Finishes in a strong push-up position']},
            {'event':'FLOOR','short':'HALF TURN',         'criteria':['Arms stay in crown the entire turn','Stays in relevé the entire turn','Toe stays at the knee the entire turn']},
            {'event':'FLOOR','short':'STEP LEAP',         'criteria':['Chest up, arms at sides in prep','Straight legs in the air','Lands in arabesque (1 sec hold)']},
        ],
    },
    'Level 3': {
        'has_safety': False,
        'footer_h': 18,
        'skills': [
            {'event':'VAULT','short':'FRONT HANDSPRING',    'criteria':['Hands touch before body is vertical','Straight body at hand contact','Straight body after hands leave']},
            {'event':'BARS', 'short':'GLIDE SWING',         'criteria':['Jumps to the bar with straight arms','Hips extended at the front of the swing','Returns in the same spot as the start']},
            {'event':'BARS', 'short':'PO CAST BK HIP CIR',  'criteria':['Cast to 45 degrees below horizontal','Straight arms in back hip circle','Legs straight and together throughout']},
            {'event':'BARS', 'short':'SOLE CIRCLE DISM',    'criteria':['Straight legs throughout','Feet rise as they come off of the bar','Body extended before landing']},
            {'event':'BEAM', 'short':'SIDE HS ¼ TURN DISM', 'criteria':['Holds side HS for 1 sec before turning','Keeps body straight during the descent','Straight legs throughout']},
            {'event':'BEAM', 'short':'HALF TURN',           'criteria':['Stays in relevé the entire turn','Arms freeze in crown during the turn','Toe stays at the knee the entire turn','Finishes the turn before stepping forward']},
            {'event':'BEAM', 'short':'SPLIT JUMP',          'criteria':['Straight legs','Minimum 90 degree split','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'CARTWHEEL',           'criteria':['Second hand turned in','Head stays between arms','Kicks through vertical with straight legs']},
            {'event':'FLOOR','short':'BACK HANDSPRING',     'criteria':['Skill travels backwards','Hands hit with open shoulders and hips','Thumbs facing each other','Legs together and straight throughout']},
            {'event':'FLOOR','short':'FRONT HANDSPRING',    'criteria':['Straight arms by ears throughout','Lands in a tight arch','Rebounds forward with straight legs']},
            {'event':'FLOOR','short':'CHASSÉ SPLIT LEAP',   'criteria':['Toes pointed in chassé','Minimum 120 degree split','Straight legs in the split']},
            {'event':'FLOOR','short':'FULL TURN',           'criteria':['Arms stay in crown the entire turn','Stays in relevé the entire turn','Toe stays at the knee the entire turn']},
            {'event':'FLOOR','short':'BACK WALKOVER',       'criteria':['Front leg lifts as hands reach back','Straight legs throughout','Arms stay by ears']},
        ],
    },
}

# Alias mapping — iClassPro discipline text → program key
PROGRAM_ALIASES = {
    'preschool': 'Preschool',
    'new preschool': 'Preschool',
    'junior': 'Junior',
    'new junior': 'Junior',
    'advanced junior': 'Advanced Junior',
    'adv junior': 'Advanced Junior',
    'adv jr': 'Advanced Junior',
    'new advanced junior': 'Advanced Junior',
    'girls level 1': 'Level 1',
    'level 1': 'Level 1',
    'girls l1': 'Level 1',
    'gl1': 'Level 1',
    'girls level 2': 'Level 2',
    'level 2': 'Level 2',
    'girls l2': 'Level 2',
    'gl2': 'Level 2',
    'girls level 3': 'Level 3',
    'level 3': 'Level 3',
    'girls l3': 'Level 3',
    'gl3': 'Level 3',
}

def resolve_program(name: str) -> str:
    """Map iClassPro discipline string to a PROGRAMS key."""
    key = name.strip().lower()
    # Try exact
    if key in PROGRAM_ALIASES:
        return PROGRAM_ALIASES[key]
    # Try contains
    for alias, prog in PROGRAM_ALIASES.items():
        if alias in key:
            return prog
    return name  # return as-is, will fail gracefully later


# ── Colors ──────────────────────────────────────────────────────────
def hex_color(h):
    return colors.HexColor(h)

GOLD       = hex_color('#C9A43C')
GOLD_LIGHT = hex_color('#FFF8DC')
WHITE      = hex_color('#ffffff')

def _build_event_colors(blue_hex, red_hex):
    """Build event color palettes from a gym's two brand colors.
    VAULT/FLOOR use the 'red' (secondary/accent) color.
    BARS/BEAM/SAFETY use the 'blue' (primary) color.
    Each event gets dark, med, and light variants."""
    dark_blue  = _darken(blue_hex, 0.20)
    dark_red   = _darken(red_hex, 0.20)
    med_blue   = _lighten(blue_hex, 0.30)
    med_red    = _lighten(red_hex, 0.30)
    light_blue = _lighten(blue_hex, 0.90)
    light_red  = _lighten(red_hex, 0.90)

    ev_dark = {
        'VAULT':  hex_color(dark_red),
        'BARS':   hex_color(dark_blue),
        'BEAM':   hex_color(blue_hex),
        'FLOOR':  hex_color(dark_red),
        'SAFETY': hex_color(dark_blue),
    }
    ev_med = {
        'VAULT':  hex_color(med_red),
        'BARS':   hex_color(med_blue),
        'BEAM':   hex_color(med_blue),
        'FLOOR':  hex_color(med_red),
        'SAFETY': hex_color(med_blue),
    }
    ev_light = {
        'VAULT':  hex_color(light_red),
        'BARS':   hex_color(light_blue),
        'BEAM':   hex_color(light_blue),
        'FLOOR':  hex_color(light_red),
        'SAFETY': hex_color(light_blue),
    }
    return ev_dark, ev_med, ev_light


# ── Star drawing ─────────────────────────────────────────────────────
def draw_star(c, cx, cy, r, fill_color, stroke_color, lw=0.5):
    outer, inner = r, r * 0.42
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


# ── Score lookup ─────────────────────────────────────────────────────
def build_score_lookup(score_map, students, skills):
    """
    score_map from frontend: { apparatus_lower: [[row_of_scores], ...] }
    Each inner list = one criterion row, values per student (1=earned, 0/None=not).
    Returns lookup[skill_index][criterion_index][student_index] = bool
    """
    lookup = {}
    row_pointer = {}   # apparatus → current row index

    for skill_idx, sk in enumerate(skills):
        ev = sk['event'].lower()
        if ev not in row_pointer:
            row_pointer[ev] = 0

        n_crit = len(sk['criteria'])
        lookup[skill_idx] = {}

        for crit_idx in range(n_crit):
            row_idx = row_pointer[ev]
            row_data = []
            if ev in score_map and row_idx < len(score_map[ev]):
                row_data = score_map[ev][row_idx]
            scores = []
            for stu_idx in range(len(students)):
                val = row_data[stu_idx] if stu_idx < len(row_data) else None
                scores.append(val == 1 or val == '1')
            lookup[skill_idx][crit_idx] = scores
            row_pointer[ev] += 1

        # Final star row
        row_idx = row_pointer[ev]
        final_row = []
        if ev in score_map and row_idx < len(score_map[ev]):
            final_row = score_map[ev][row_idx]
        final_scores = []
        for stu_idx in range(len(students)):
            val = final_row[stu_idx] if stu_idx < len(final_row) else None
            final_scores.append(val == 1 or val == '1')
        lookup[skill_idx]['final'] = final_scores
        row_pointer[ev] += 1

    return lookup


# ════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ════════════════════════════════════════════════════════════════════
def generate_pdf(gym_code, class_name, date, day, time,
                 students, program, score_map, mode='eval', _canvas=None):
    """
    Returns PDF as bytes (single-page), or draws onto _canvas if provided (multi-page).
    mode: 'eval' = pre-fill scores | 'blank' = all empty
    """

    # Resolve gym and program
    gym  = GYMS.get(gym_code, GYMS['CCP'])
    prog_key = resolve_program(program)
    prog = PROGRAMS.get(prog_key)
    if not prog:
        raise ValueError(f"Unknown program: {program!r}. Known: {list(PROGRAMS.keys())}")

    CCP_BLUE     = hex_color(gym['blue'])
    CCP_BLUE_MID = hex_color(_darken(gym['blue'], 0.15))
    CCP_BLUE_LT  = hex_color(_lighten(gym['blue'], 0.7))
    CCP_BLUE_XLT = hex_color(_lighten(gym['blue'], 0.92))
    CCP_RED      = hex_color(gym['red'])
    CCP_GRAY     = hex_color(gym['gray'])
    CCP_GRAY_MID = hex_color('#b0b0b0')
    CCP_GRAY_DK  = hex_color('#555566')

    # Build event colors from this gym's brand
    EV_DARK, EV_MED, EV_LIGHT = _build_event_colors(gym['blue'], gym['red'])

    SKILLS   = prog['skills']
    HAS_SAF  = prog.get('has_safety', False)
    FOOTER_H = prog.get('footer_h', 18)

    NUM_SKILLS = len(SKILLS)
    NUM_COLS   = sum(len(sk['criteria'])+1 for sk in SKILLS)

    # Layout
    TOP_BAR_H  = 48
    EV_HDR_H   = 15
    SK_HDR_H   = 26
    STAR_LBL_H = 11
    CRIT_H     = 150 if HAS_SAF else 175

    CONTENT_TOP  = H - MARGIN - TOP_BAR_H
    CONTENT_BOT  = MARGIN + FOOTER_H
    HEADER_H     = EV_HDR_H + SK_HDR_H + CRIT_H + STAR_LBL_H
    DATA_TOP     = CONTENT_TOP - HEADER_H
    DATA_H       = DATA_TOP - CONTENT_BOT
    ROW_H        = DATA_H / NUM_ROWS
    NAME_ZONE_H  = 8
    NAME_W       = 68
    GRID_LEFT    = MARGIN + NAME_W
    GRID_W       = W - MARGIN - GRID_LEFT
    COL_W        = GRID_W / NUM_COLS

    # Score lookup
    if mode == 'eval' and score_map:
        lookup = build_score_lookup(score_map, students, SKILLS)
    else:
        lookup = {}   # blank mode

    # Column offsets
    skill_col_start = []
    col = 0
    for sk in SKILLS:
        skill_col_start.append(col)
        col += len(sk['criteria']) + 1

    ev_spans = {}
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        sc = skill_col_start[i]
        ec = skill_col_start[i] + len(sk['criteria'])
        if ev not in ev_spans:
            ev_spans[ev] = [sc, ec]
        else:
            ev_spans[ev][1] = ec

    def ev_x(col_idx): return GRID_LEFT + col_idx * COL_W
    def row_y(row_idx): return DATA_TOP - (row_idx+1)*ROW_H

    # ── Draw ──────────────────────────────────────────────────────────
    if _canvas is not None:
        # Multi-page mode: use provided canvas
        c   = _canvas
        buf = None
    else:
        buf = io.BytesIO()
        c   = canvas.Canvas(buf, pagesize=landscape(letter))

    # White base
    c.setFillColor(WHITE)
    c.rect(MARGIN, MARGIN, USABLE_W, USABLE_H, fill=1, stroke=0)

    # ── TOP BAR ───────────────────────────────────────────────────────
    bar_y = H - MARGIN - TOP_BAR_H
    c.setFillColor(CCP_BLUE)
    c.rect(MARGIN, bar_y, USABLE_W, TOP_BAR_H, fill=1, stroke=0)
    c.setFillColor(CCP_RED)
    c.rect(MARGIN, bar_y+TOP_BAR_H-3, USABLE_W, 3, fill=1, stroke=0)
    c.setFillColor(CCP_GRAY)
    c.rect(MARGIN, bar_y, USABLE_W, 2, fill=1, stroke=0)

    # Logo
    import os
    logo_path = os.path.join(os.path.dirname(__file__), gym['logo'])
    if os.path.exists(logo_path):
        c.drawImage(logo_path, MARGIN+4, bar_y+4, width=40, height=40, mask='auto')

    # Gym name centered
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(W/2, bar_y+31, gym['name'])

    # Class info centered
    parts = [class_name]
    if day:  parts.append(day)
    if date: parts.append(date)
    if time: parts.append(time)
    class_line = '  ·  '.join(parts)
    c.setFillColor(CCP_GRAY)
    c.setFont('Helvetica', 8.5)
    c.drawCentredString(W/2, bar_y+16, class_line)

    # ── HEADER: EVENT BANDS ───────────────────────────────────────────
    ev_top = CONTENT_TOP
    for ev, (sc, ec) in ev_spans.items():
        x = ev_x(sc); w = (ec-sc+1)*COL_W
        c.setFillColor(EV_DARK.get(ev, CCP_BLUE))
        c.rect(x, ev_top-EV_HDR_H, w, EV_HDR_H, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 7.5)
        c.drawCentredString(x+w/2, ev_top-EV_HDR_H+5, ev)

    # Navy block for name col
    c.setFillColor(CCP_BLUE)
    c.rect(MARGIN, ev_top-EV_HDR_H, NAME_W, EV_HDR_H, fill=1, stroke=0)
    c.rect(MARGIN, DATA_TOP, NAME_W, HEADER_H-EV_HDR_H, fill=1, stroke=0)

    # ── HEADER: SKILL NAMES ───────────────────────────────────────────
    sk_top = ev_top - EV_HDR_H
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        x  = ev_x(skill_col_start[i])
        w  = (len(sk['criteria'])+1)*COL_W
        c.setFillColor(EV_MED.get(ev, CCP_BLUE_MID))
        c.rect(x, sk_top-SK_HDR_H, w, SK_HDR_H, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 6)
        name = sk['short']
        max_w = w - 4
        if c.stringWidth(name, 'Helvetica-Bold', 6) > max_w:
            words = name.split()
            mid = max(1, len(words)//2)
            line1 = ' '.join(words[:mid])
            line2 = ' '.join(words[mid:])
            c.drawCentredString(x+w/2, sk_top-SK_HDR_H+17, line1)
            c.drawCentredString(x+w/2, sk_top-SK_HDR_H+8,  line2)
        else:
            c.drawCentredString(x+w/2, sk_top-SK_HDR_H+12, name)

    # ── HEADER: CRITERIA (rotated) ────────────────────────────────────
    crit_top = sk_top - SK_HDR_H
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        crits_all  = sk['criteria'] + ['3× in a row']
        star_labels = [f'★{j+1}' for j in range(len(sk['criteria']))] + ['★F']
        for j, (star, crit) in enumerate(zip(star_labels, crits_all)):
            col_x    = ev_x(skill_col_start[i]+j)
            is_final = (j == len(sk['criteria']))
            bg = EV_DARK.get(ev, CCP_BLUE) if is_final else EV_LIGHT.get(ev, CCP_BLUE_XLT)
            c.setFillColor(bg)
            c.rect(col_x, crit_top-CRIT_H, COL_W, CRIT_H, fill=1, stroke=0)
            c.setStrokeColor(hex_color('#cccccc') if not is_final else EV_MED.get(ev, CCP_BLUE_MID))
            c.setLineWidth(0.3)
            c.line(col_x, crit_top-CRIT_H, col_x, crit_top)
            c.saveState()
            c.translate(col_x+COL_W/2, crit_top-CRIT_H/2)
            c.rotate(90)
            fg   = WHITE if is_final else EV_DARK.get(ev, CCP_BLUE)
            font = 'Helvetica-Bold'
            size = 8.0
            c.setFillColor(fg); c.setFont(font, size)
            # Truncate by pixel width, not character count
            # CRIT_H is the available space (text is rotated 90°)
            max_text_w = CRIT_H - 8  # 4pt padding each side
            display = _truncate_to_width(c, crit, font, size, max_text_w)
            c.drawCentredString(0, -size/3, display)
            c.restoreState()

    # ── HEADER: STAR LABELS ───────────────────────────────────────────
    starlbl_top = crit_top - CRIT_H
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        star_labels = [f'★{j+1}' for j in range(len(sk['criteria']))] + ['★F']
        for j, star in enumerate(star_labels):
            col_x    = ev_x(skill_col_start[i]+j)
            is_final = (j == len(sk['criteria']))
            c.setFillColor(GOLD if is_final else EV_LIGHT.get(ev, CCP_BLUE_XLT))
            c.setStrokeColor(hex_color('#cccccc')); c.setLineWidth(0.3)
            c.rect(col_x, starlbl_top-STAR_LBL_H, COL_W, STAR_LBL_H, fill=1, stroke=1)
            if is_final:
                draw_star(c, col_x+COL_W/2, starlbl_top-STAR_LBL_H/2+0.5, 5.5, WHITE, WHITE, lw=0)
            else:
                c.setFillColor(EV_DARK.get(ev, CCP_BLUE))
                c.setFont('Helvetica-Bold', 6.5)
                c.drawCentredString(col_x+COL_W/2, starlbl_top-STAR_LBL_H+3.5, star)

    # "NAME" label in navy block
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(MARGIN+NAME_W/2, starlbl_top-STAR_LBL_H/2-2, 'NAME')

    # ── STUDENT ROWS ──────────────────────────────────────────────────
    for row in range(NUM_ROWS):
        ry = row_y(row)
        c.setFillColor(WHITE if row%2==0 else hex_color('#f7f8fa'))
        c.rect(MARGIN, ry, USABLE_W, ROW_H, fill=1, stroke=0)

        # Student name
        name_str = students[row] if row < len(students) else ''
        if name_str:
            # First name + last initial
            parts = name_str.strip().split()
            if len(parts) >= 2:
                display = f"{parts[0]} {parts[-1][0]}."
            else:
                display = name_str
            c.setFillColor(hex_color('#222222'))
            c.setFont('Helvetica-Bold', 10)
            c.drawCentredString(MARGIN+NAME_W/2, ry+ROW_H/2-4, display)

        # Bubbles
        bubble_zone_top    = ry + ROW_H
        bubble_zone_bottom = ry + NAME_ZONE_H
        bubble_cy = (bubble_zone_top + bubble_zone_bottom) / 2

        for i in range(NUM_SKILLS):
            sk     = SKILLS[i]
            n_crit = len(sk['criteria'])
            for j in range(n_crit+1):
                col_x    = ev_x(skill_col_start[i]+j)
                cx       = col_x + COL_W/2
                r_bub    = min(COL_W*0.31, (ROW_H-NAME_ZONE_H)*0.35)
                is_final = (j == n_crit)

                # Get earned state
                if mode == 'blank' or not lookup:
                    earned = False
                else:
                    if is_final:
                        earned = lookup.get(i, {}).get('final', [False]*NUM_ROWS)
                        earned = earned[row] if row < len(earned) else False
                    else:
                        earned = lookup.get(i, {}).get(j, [False]*NUM_ROWS)
                        earned = earned[row] if row < len(earned) else False

                if is_final:
                    if earned:
                        draw_star(c, cx, bubble_cy, r_bub*1.2, GOLD, hex_color('#8a6a00'), lw=0.5)
                    else:
                        draw_star(c, cx, bubble_cy, r_bub*1.2, WHITE, CCP_GRAY_MID, lw=1.2)
                else:
                    if earned:
                        draw_star(c, cx, bubble_cy, r_bub*1.2, CCP_RED, CCP_RED, lw=0)
                    else:
                        c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(1.2)
                        c.circle(cx, bubble_cy, r_bub, fill=1, stroke=1)

    # ── GRID LINES ────────────────────────────────────────────────────
    for i, sk in enumerate(SKILLS):
        x = ev_x(skill_col_start[i])
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.7)
        c.line(x, CONTENT_BOT, x, DATA_TOP)
    c.line(ev_x(NUM_COLS), CONTENT_BOT, ev_x(NUM_COLS), DATA_TOP)

    for i, sk in enumerate(SKILLS):
        x = ev_x(skill_col_start[i])
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.35)
        c.line(x, starlbl_top-STAR_LBL_H, x, ev_top-EV_HDR_H)
    c.line(ev_x(NUM_COLS), starlbl_top-STAR_LBL_H, ev_x(NUM_COLS), ev_top-EV_HDR_H)

    for i, sk in enumerate(SKILLS):
        for j in range(1, len(sk['criteria'])+1):
            x = ev_x(skill_col_start[i]+j)
            c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.18)
            c.line(x, starlbl_top-STAR_LBL_H, x, sk_top-SK_HDR_H)

    c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.3)
    for row in range(NUM_ROWS+1):
        y = DATA_TOP - row*ROW_H
        c.line(MARGIN, y, W-MARGIN, y)

    c.setStrokeColor(CCP_BLUE); c.setLineWidth(1.4)
    c.line(MARGIN+NAME_W, CONTENT_BOT, MARGIN+NAME_W, CONTENT_TOP)
    c.line(MARGIN, DATA_TOP, W-MARGIN, DATA_TOP)

    c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
    c.line(MARGIN, sk_top,      W-MARGIN, sk_top)
    c.line(MARGIN, crit_top,    W-MARGIN, crit_top)
    c.line(MARGIN, starlbl_top, W-MARGIN, starlbl_top)

    c.setStrokeColor(CCP_BLUE_MID); c.setLineWidth(1.0)
    c.line(MARGIN, CONTENT_TOP, W-MARGIN, CONTENT_TOP)

    # ── SAFETY FOOTER ─────────────────────────────────────────────────
    if HAS_SAF:
        ft_y = MARGIN
        ft_h = FOOTER_H
        SAF_CRIT = prog.get('safety_criteria', ['Follows directions','Stays with the group','Keeps hands to self'])

        c.setFillColor(CCP_BLUE_XLT)
        c.rect(MARGIN, ft_y, USABLE_W, ft_h, fill=1, stroke=0)
        c.setStrokeColor(CCP_BLUE); c.setLineWidth(1.2)
        c.line(MARGIN, ft_y+ft_h, W-MARGIN, ft_y+ft_h)

        SAF_LBL_W = 52
        c.setFillColor(CCP_BLUE)
        c.rect(MARGIN, ft_y, SAF_LBL_W, ft_h, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-13, 'SAFETY')
        c.setFillColor(CCP_GRAY); c.setFont('Helvetica', 4.8)
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-22, 'assessed')
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-29, 'each class')
        c.setStrokeColor(CCP_RED); c.setLineWidth(1.2)
        c.line(MARGIN+SAF_LBL_W, ft_y, MARGIN+SAF_LBL_W, ft_y+ft_h)

        SAF_KEY_W = 146
        key_x = MARGIN + SAF_LBL_W + 5
        saf_all = [(f'★{i+1}', t) for i,t in enumerate(SAF_CRIT)] + [('★F','3× in a row')]
        row_h_key = (ft_h-10)/len(saf_all)
        for idx, (star, crit_txt) in enumerate(saf_all):
            ky = ft_y + ft_h - 6 - (idx+1)*row_h_key
            is_f = (idx == len(SAF_CRIT))
            if is_f:
                # Draw solid gold star instead of ★F text
                draw_star(c, key_x+5, ky+row_h_key/2, 5, GOLD, GOLD, lw=0)
            else:
                c.setFillColor(CCP_BLUE)
                c.setFont('Helvetica-Bold', 7)
                c.drawString(key_x, ky+row_h_key/2-2, star)
            c.setFillColor(CCP_RED if is_f else CCP_GRAY_DK)
            c.setFont('Helvetica-Bold' if is_f else 'Helvetica', 6.5)
            c.drawString(key_x+18, ky+row_h_key/2-2, crit_txt)

        saf_grid_x = MARGIN + SAF_LBL_W + SAF_KEY_W + 6
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.7)
        c.line(saf_grid_x-2, ft_y+4, saf_grid_x-2, ft_y+ft_h-4)

        N_SAF       = 6
        saf_total_w = W - MARGIN - saf_grid_x
        saf_col_w   = saf_total_w / N_SAF
        NAME_H_SAF  = 13
        STAR_H_SAF  = 10
        BUB_H_SAF   = ft_h - NAME_H_SAF - STAR_H_SAF - 6
        n_saf_stars = len(SAF_CRIT) + 1  # criteria + final

        # Safety score lookup
        saf_lookup = {}
        if mode == 'eval' and score_map and 'safety' in score_map:
            saf_rows = score_map['safety']
            for ci in range(len(SAF_CRIT)+1):
                row_data = saf_rows[ci] if ci < len(saf_rows) else []
                saf_lookup[ci] = [
                    (row_data[si] == 1 or row_data[si] == '1') if si < len(row_data) else False
                    for si in range(N_SAF)
                ]

        for col in range(N_SAF):
            sx = saf_grid_x + col*saf_col_w
            c.setFillColor(CCP_BLUE_XLT if col%2==0 else WHITE)
            c.rect(sx, ft_y, saf_col_w, ft_h, fill=1, stroke=0)

            # Name
            stu_name = students[col] if col < len(students) else ''
            if stu_name:
                parts = stu_name.strip().split()
                display = f"{parts[0]} {parts[-1][0]}." if len(parts) >= 2 else stu_name
                c.setFillColor(hex_color('#222222')); c.setFont('Helvetica-Bold', 6.5)
                c.drawCentredString(sx+saf_col_w/2, ft_y+ft_h-8, display)
            c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
            c.line(sx+3, ft_y+ft_h-NAME_H_SAF+1, sx+saf_col_w-3, ft_y+ft_h-NAME_H_SAF+1)

            sub_w = saf_col_w / n_saf_stars
            star_label_y = ft_y + 5 + BUB_H_SAF
            saf_star_labels = [f'★{i+1}' for i in range(len(SAF_CRIT))] + ['★F']
            for j, lbl in enumerate(saf_star_labels):
                bx = sx + j*sub_w + sub_w/2
                if j == len(SAF_CRIT):
                    draw_star(c, bx, star_label_y+4, 4.5, GOLD, GOLD, lw=0)
                else:
                    c.setFillColor(CCP_BLUE); c.setFont('Helvetica-Bold', 6)
                    c.drawCentredString(bx, star_label_y+1, lbl)

            bub_r  = min(sub_w*0.30, BUB_H_SAF*0.40)
            bub_cy = ft_y + 5 + BUB_H_SAF/2
            for j in range(n_saf_stars):
                bx       = sx + j*sub_w + sub_w/2
                is_f     = (j == len(SAF_CRIT))
                earned_s = saf_lookup.get(j, [False]*N_SAF)[col] if saf_lookup else False
                if is_f:
                    if earned_s:
                        draw_star(c, bx, bub_cy, bub_r*1.15, GOLD, hex_color('#8a6a00'), lw=0.5)
                    else:
                        draw_star(c, bx, bub_cy, bub_r*1.15, WHITE, CCP_GRAY_MID, lw=1.0)
                else:
                    if earned_s:
                        draw_star(c, bx, bub_cy, bub_r*1.15, CCP_RED, CCP_RED, lw=0)
                    else:
                        c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.8)
                        c.circle(bx, bub_cy, bub_r, fill=1, stroke=1)

            if col > 0:
                c.setStrokeColor(CCP_GRAY); c.setLineWidth(0.4)
                c.line(sx, ft_y+3, sx, ft_y+ft_h-3)

    # ── OUTER BORDER ──────────────────────────────────────────────────
    c.setStrokeColor(CCP_BLUE); c.setLineWidth(2.0)
    c.rect(MARGIN, MARGIN, USABLE_W, USABLE_H, fill=0, stroke=1)
    c.setFillColor(CCP_RED)
    c.rect(MARGIN, H-MARGIN-3, USABLE_W, 3, fill=1, stroke=0)
    c.rect(MARGIN, MARGIN, USABLE_W, 3, fill=1, stroke=0)

    if buf is not None:
        # Single-page mode: finalize and return bytes
        c.save()
        return buf.getvalue()
    else:
        # Multi-page mode: page drawn, caller owns the canvas
        return None


# ════════════════════════════════════════════════════════════════════
# MULTI-CLASS GENERATOR — one PDF, one page per class
# ════════════════════════════════════════════════════════════════════
def generate_multi_pdf(gym_code, classes, mode='eval'):
    """
    classes: list of dicts with keys: className, date, day, time, students, program, scoreMap
    Returns one PDF with one page per class.
    """
    buf = io.BytesIO()
    c   = canvas.Canvas(buf, pagesize=landscape(letter))

    for i, cls in enumerate(classes):
        if i > 0:
            c.showPage()  # new page for each class after the first
        generate_pdf(
            gym_code   = gym_code,
            class_name = cls.get('className', 'Class'),
            date       = cls.get('date', ''),
            day        = cls.get('day', ''),
            time       = cls.get('time', ''),
            students   = cls.get('students', []),
            program    = cls.get('program', ''),
            score_map  = cls.get('scoreMap', {}),
            mode       = mode,
            _canvas    = c,
        )

    c.save()
    return buf.getvalue()


# ── Text truncation helper ──────────────────────────────────────────
def _truncate_to_width(canvas_obj, text, font, size, max_w):
    """Truncate text to fit within max_w points at the given font/size."""
    w = canvas_obj.stringWidth(text, font, size)
    if w <= max_w:
        return text
    # Binary search for the longest substring that fits
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if canvas_obj.stringWidth(text[:mid], font, size) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]


# ── Color helpers ────────────────────────────────────────────────────
def _lighten(hex_str, amount):
    r = int(hex_str[1:3],16); g = int(hex_str[3:5],16); b = int(hex_str[5:7],16)
    r = int(r + (255-r)*amount); g = int(g + (255-g)*amount); b = int(b + (255-b)*amount)
    return f'#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}'

def _darken(hex_str, amount):
    r = int(hex_str[1:3],16); g = int(hex_str[3:5],16); b = int(hex_str[5:7],16)
    r = int(r*(1-amount)); g = int(g*(1-amount)); b = int(b*(1-amount))
    return f'#{r:02x}{g:02x}{b:02x}'
