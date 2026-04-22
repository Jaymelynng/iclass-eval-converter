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
# NUM_ROWS is now per-program — defined in PROGRAMS dict below

# ── Gym configuration ───────────────────────────────────────────────
# v0-style scheme: each gym uses ONE 'brand' color for ALL event/skill/program/safety
# blocks. Top bar is a neutral dark charcoal; criteria rotated text sits on a light
# gray stripe with black text. Distinction between events comes from whitespace +
# skill-name typography, not color variety.
GYMS = {
    'CCP': {
        'name': 'CAPITAL GYMNASTICS — Cedar Park', 'logo': 'logos/CCP_logo_transparent.png',
        'blue': '#1f53a3', 'red': '#bf0a30', 'gray': '#d8d8d8',
        'brand': '#bf0a30',
        'ev_cool': '#1f53a3',  # CCP keeps its blue on Bars/Floor instead of shared gray
    },
    'CPF': {
        'name': 'CAPITAL GYMNASTICS — Pflugerville', 'logo': 'logos/CCP_logo_transparent.png',
        'blue': '#1f53a3', 'red': '#bf0a30', 'gray': '#d8d8d8',
        'brand': '#bf0a30',
        'ev_cool': '#1f53a3',  # CPF = CCP, Capital blue on Bars/Floor
    },
    'CRR': {
        'name': 'CAPITAL GYMNASTICS — Round Rock', 'logo': 'logos/crr_logo.png',
        'blue': '#4a4a4b', 'red': '#ff1493', 'gray': '#3c3939',
        # Full hot pink #ff1493 is 3.64:1 on white — borderline fail on event strip.
        # Darkened 25% to #bf0f6e (6.0:1) keeps the hot pink identity while
        # making white text on event/skill/program blocks clearly readable.
        'brand': '#bf0f6e',
        'top_bar_h': 64, 'logo_size': 60,
    },
    'EST': {
        'name': 'Estrella Gymnastics', 'logo': 'logos/est_logo.png',
        'blue': '#011837', 'red': '#666666', 'gray': '#d8d8d8',
        # Deep navy #011837 passes white text (17.7:1) but is nearly indistinguishable
        # from the charcoal #252626 top bar — the whole header reads as one flat dark
        # block. Using a lighter navy #1a4a7a (9.1:1 on white) for the event/skill
        # strips makes them visually distinct from the top bar while still on-brand.
        'brand': '#1a4a7a',
    },
    'HGA': {
        'name': 'Houston Gymnastics Academy', 'logo': 'logos/hga with shadow.png',
        'blue': '#262626', 'red': '#c91724', 'gray': '#d0d0d8',
        'brand': '#c91724',
    },
    'OAS': {
        'name': 'Oasis Gymnastics', 'logo': 'logos/oasis circle logo.png',
        'blue': '#3e266b', 'red': '#3eb29f', 'gray': '#e7e6f0',
        'brand': '#3eb29f',
    },
    'RBA': {
        'name': 'Rowland Ballard — Atascocita', 'logo': 'logos/rba_logo.png',
        'blue': '#1a3c66', 'red': '#c52928', 'gray': '#739ab9',
        'brand': '#c52928',
    },
    'RBK': {
        'name': 'Rowland Ballard — Kingwood', 'logo': 'logos/rbk_logo.png',
        'blue': '#1a3c66', 'red': '#c52928', 'gray': '#739ab9',
        'brand': '#c52928',
    },
    'SGT': {
        'name': 'Scottsdale Gymnastics', 'logo': 'logos/sgt_logo.png',
        'blue': '#000000', 'red': '#c72b12', 'gray': '#e6e6e6',
        'brand': '#c72b12',
    },
    'TIG': {
        'name': 'Tigar Gymnastics', 'logo': 'logos/tig_logo.png',
        'blue': '#0a3651', 'red': '#f57f20', 'gray': '#7fc4e0',
        # orange #f57f20 is only 2.65:1 on white — FAILS on event strip.
        # Navy #0a3651 (12.7:1) becomes brand for event/skill headers.
        # Orange survives where it's darkened (skill strip) and in the logo.
        'brand': '#0a3651',
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
        'num_rows': 6,
        'skills': [
            {'event':'VAULT','short':'Run + Hurdle\nto Two-Foot Jump',  'criteria':['Runs into hurdle, no stutter-step','Hurdles off 1 foot, lands on 2 feet','Arms by ears in jump']},
            {'event':'BARS', 'short':'Front Support\nFWD Roll\n(with spot)',   'criteria':['Unassisted front support for 3 sec','Looks at belly while rolling','Hands stay on bar until roll is done']},
            {'event':'BARS', 'short':'Tuck Hang',    'criteria':['Holds for 3 sec','Knees above belly button','Arms by ears']},
            {'event':'BEAM', 'short':'Walk Across\nLow Beam\n(Unassisted)',    'criteria':['Chest up with arms out to the side','One foot in front of the other','Walks across beam without wobbles']},
            {'event':'BEAM', 'short':'Bear Crawl\non Line',   'criteria':['Hands on the line','Feet on the line','Straight legs']},
            {'event':'BEAM', 'short':'Backward Walk\nwith Coach',     'criteria':['Chest up with arms out to the side','Heel-to-toe steps backward','Eyes forward while walking back']},
            {'event':'FLOOR','short':'Monkey Jump\nOver Panel Mat',  'criteria':['Turns hands towards "favorite foot"','Jumps over panel mat without touch','Starts and finishes with arms up']},
            {'event':'FLOOR','short':'BWD Handstand\nWalk Up\n(5 sec hold)',  'criteria':['Walk up wall, hips above shoulders','Straight arms covering ears','Straight back']},
            {'event':'FLOOR','short':'FWD Roll\nDown Wedge',   'criteria':['Starts in a pencil shape','Eyes on belly','Stands up without using hands']},
            {'event':'FLOOR','short':'Tabletop Hold',     'criteria':['Holds for 5 sec','Back flat, no sagging hips','Fingers facing feet']},
        ],
        'safety_criteria': ['Follows directions','Stays with the group','Keeps hands to self'],
    },
    'Junior': {
        'has_safety': True,
        'footer_h': 68,
        'num_rows': 6,
        'skills': [
            {'event':'VAULT','short':'Run + Hurdle +\nStraight Jump\nto Panel Mat', 'criteria':['Accelerates into hurdle, no pauses','Hurdles off 1 foot, hits board on 2','Arms down on board, up in the air']},
            {'event':'BARS', 'short':'Pullover\n(with Mat)',      'criteria':['Chin at bar, walks feet above bar','Shifts hands FWD to front support','Front support 3 sec, belly off bar']},
            {'event':'BARS', 'short':'Forward Roll',  'criteria':['From front support, rolls forward','Feet and knees together','Lands on feet with control']},
            {'event':'BARS', 'short':'Front Support\n(5 sec hold)', 'criteria':['Straight arms','Belly in and back rounded','Straight legs, pointed toes in front']},
            {'event':'BEAM', 'short':'Walk Across\nMedium Beam\n(Unassisted)', 'criteria':['Chest up with arms out to the side','One foot in front of the other','Walks across beam without wobbles']},
            {'event':'BEAM', 'short':'Lever\n(Floor)', 'criteria':['Starts/finishes in lunge, no wobbles','Back leg stays straight','Arms by ears']},
            {'event':'BEAM', 'short':'Backward Walk\non Low Beam', 'criteria':['Chest up with arms out to the side','Heel-to-toe steps backward','Eyes forward while walking back']},
            {'event':'FLOOR','short':'Cartwheel\nto Lunge',     'criteria':['Starts fav foot front, ends opposite','Straight legs','Legs pass through vertical']},
            {'event':'FLOOR','short':'Lunge to\nHandstand\n(Mat Supported)', 'criteria':['Starts and finishes in a lunge','Straight legs, feet together vertical','Straight line from hands to toes']},
            {'event':'FLOOR','short':'Forward Roll',  'criteria':['Continuous movement in the roll','Feet and knees together','Stands up without using hands']},
            {'event':'FLOOR','short':'Bridge\n(Feet Elevated)',   'criteria':['Pushes up w/o moving hands/feet','Straight arms by ears','Holds for 3 sec']},
        ],
        'safety_criteria': ['Follows directions','Stays with the group','Keeps hands to self'],
    },
    'Advanced Junior': {
        'has_safety': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'VAULT','short':'Straight Jump\nto Resi',    'criteria':['Run accelerates into the hurdle','Arms down on the board, up in the air','Straight body and legs in the air']},
            {'event':'VAULT','short':'Handstand\nFlatback',       'criteria':['Feet together at vertical','Straight line hands to toes at vertical','Lands flat on the mat as one piece']},
            {'event':'BARS', 'short':'Kick\nPullover',            'criteria':['Chin stays at the bar until toes come over','Shifts hands FWD to front support','Straight legs throughout the skill']},
            {'event':'BARS', 'short':'Cast',                      'criteria':['Straight arms throughout the skill','Legs straight and together','Straight line from shoulders to toes']},
            {'event':'BARS', 'short':'Front\nSupport \u2192\nRoll Down','criteria':['Holds front support with straight arms','Chin to chest','Legs straight/together, lowers to hang']},
            {'event':'BEAM', 'short':'Beam\nMount',               'criteria':['Jumps to front support with straight arms','Straight leg swings over, no beam touch','Stands up with arms by ears']},
            {'event':'BEAM', 'short':'Lever',                     'criteria':['Arms by ears throughout','Straight line from fingers to back foot','Back leg stays straight']},
            {'event':'BEAM', 'short':'Relev\u00e9\nWalk',         'criteria':['Heels stay off the beam the entire walk','Walks with straight legs','Chest up with arms out to the side']},
            {'event':'BEAM', 'short':'Straight\nJump',            'criteria':['Arms up on takeoff, down on landing','Toes pointed in the air','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'Straight\nJump\nDismount',  'criteria':['Arms swing up as feet leave the beam','Straight line from fingers to toes in the air','Sticks landing, hands in front, knees bent']},
            {'event':'FLOOR','short':'Handstand',                 'criteria':['Feet come together at vertical','Straight line from hands to toes','Straight legs in the air/arms stay by ears']},
            {'event':'FLOOR','short':'Cartwheel',                 'criteria':['Legs pass through vertical','Second hand turned in','Arms stay by ears','Legs straight throughout','Finishes in lunge, opposite leg front']},
            {'event':'FLOOR','short':'Backward\nRoll',            'criteria':['Rolls with fingers pointing to shoulders','Continuous movement in the roll','Feet and knees together throughout']},
            {'event':'FLOOR','short':'Bridge\n(5 sec hold)',       'criteria':['Straight arms in the bridge','Head between the arms','Feet flat and together']},
        ],
    },
    'Level 1': {
        'has_safety': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'VAULT','short':'Straight Jump\nto Resi',    'criteria':['Run accelerates into the hurdle','Arms down on the board, up in the air','Straight body and legs in the air']},
            {'event':'VAULT','short':'Handstand\nFlatback',       'criteria':['Feet together at vertical','Straight line hands to toes at vertical','Lands flat on the mat as one piece']},
            {'event':'BARS', 'short':'Kick\nPullover',            'criteria':['Chin stays at the bar until toes come over','Shifts hands FWD to front support','Straight legs throughout the skill']},
            {'event':'BARS', 'short':'Cast',                      'criteria':['Straight arms throughout the skill','Legs straight and together','Straight line from shoulders to toes']},
            {'event':'BARS', 'short':'Front\nSupport \u2192\nRoll Down','criteria':['Holds front support with straight arms','Chin to chest','Legs straight/together, lowers to hang']},
            {'event':'BEAM', 'short':'Beam\nMount',               'criteria':['Jumps to front support with straight arms','Straight leg swings over, no beam touch','Stands up with arms by ears']},
            {'event':'BEAM', 'short':'Lever',                     'criteria':['Arms by ears throughout','Straight line from fingers to back foot','Back leg stays straight']},
            {'event':'BEAM', 'short':'Relev\u00e9\nWalk',         'criteria':['Heels stay off the beam the entire walk','Walks with straight legs','Chest up with arms out to the side']},
            {'event':'BEAM', 'short':'Straight\nJump',            'criteria':['Arms up on takeoff, down on landing','Toes pointed in the air','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'Straight\nJump\nDismount',  'criteria':['Arms swing up as feet leave the beam','Straight line from fingers to toes in the air','Sticks landing, hands in front, knees bent']},
            {'event':'FLOOR','short':'Handstand',                 'criteria':['Feet come together at vertical','Straight line from hands to toes','Straight legs in the air/arms stay by ears']},
            {'event':'FLOOR','short':'Cartwheel',                 'criteria':['Legs pass through vertical','Second hand turned in','Arms stay by ears','Legs straight throughout','Finishes in lunge, opposite leg front']},
            {'event':'FLOOR','short':'Backward\nRoll',            'criteria':['Rolls with fingers pointing to shoulders','Continuous movement in the roll','Feet and knees together throughout']},
            {'event':'FLOOR','short':'Bridge\n(5 sec hold)',       'criteria':['Straight arms in the bridge','Head between the arms','Feet flat and together']},
        ],
    },
    'Level 2': {
        'has_safety': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'VAULT','short':'Handstand\nFlatback\non Resi',       'criteria':['Arms down on the board, up in the air','Straight line from hands to toes at handstand','Lands flat as one piece']},
            {'event':'BARS', 'short':'Chin-Up\nPullover',  'criteria':['Chin to bar (min forehead height)','Feet leave the floor at the same time','Legs straight and together throughout']},
            {'event':'BARS', 'short':'Cast Back\nHip Circle', 'criteria':['Straight arms as shoulders lean backwards','Bar stays against thighs entire circle','Eyes on toes throughout the skill']},
            {'event':'BARS', 'short':'Cast Off\nDismount',     'criteria':['Straight arms throughout the cast','Shoulders over bar before push away','Cast 45 below horizontal']},
            {'event':'BARS', 'short':'Roll Down\nto Chin Hang', 'criteria':['Chin finishes above the bar','Holds tucked chin hang for 5 sec','Feet and knees together throughout']},
            {'event':'BEAM', 'short':'Pivot Turn',        'criteria':['Stays in relev\u00e9 lock the entire turn','Arms stay overhead the entire turn','Straight legs']},
            {'event':'BEAM', 'short':'Vertical\nHandstand',       'criteria':['Feet come together at vertical','Straight line from hands to toes','Arms stay by ears']},
            {'event':'BEAM', 'short':'Side\nHandstand\nDismount',      'criteria':['Holds handstand 1 sec before falling','Straight line from shoulder to toes in dismount','Shoulders over beam from HS to fall']},
            {'event':'FLOOR','short':'Bridge\nKickover',   'criteria':['Straight arms by ears','Legs stay straight through the split','One step from bridge hold to kickover']},
            {'event':'FLOOR','short':'Round-Off\nRebound', 'criteria':['Legs straight/together in snap-down','Hands come off the floor before feet hit','Rebounds up and back immediately']},
            {'event':'FLOOR','short':'Straight Arm\nBackward Roll',  'criteria':['Pushes on pinkies at beginning of roll','Arms stay straight during the roll','Finishes in a strong push-up position']},
            {'event':'FLOOR','short':'Half Turn',         'criteria':['Arms stay in crown the entire turn','Stays in relev\u00e9 the entire turn','Toe stays at the knee the entire turn']},
            {'event':'FLOOR','short':'Step Leap',         'criteria':['Correct leap prep: chest up, arms at sides','Straight legs in the air','Lands in arabesque, front leg bent (1 sec)']},
        ],
    },
    'Level 3': {
        'has_safety': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'VAULT','short':'Front\nHandspring',    'criteria':['Hands touch mat/table before vertical','Straight body when hands touch mat/table','Straight body after hands leave mat/table']},
            {'event':'BARS', 'short':'Glide Swing',         'criteria':['Jumps to the bar with straight arms','Hips extended at the front of the swing','Returns in the same spot as the start']},
            {'event':'BARS', 'short':'Pullover Cast\nBack Hip Circle',  'criteria':['Cast to 45 degrees below horizontal','Straight arms in back hip circle','Legs straight and together throughout']},
            {'event':'BARS', 'short':'Sole Circle\nDismount',    'criteria':['Straight legs throughout','Feet rise as they come off of the bar','Body extended before landing']},
            {'event':'BEAM', 'short':'Side HS\n1/4 Turn\nDismount', 'criteria':['Holds side HS for 1 sec before turning','Keeps body straight during the descent','Straight legs throughout']},
            {'event':'BEAM', 'short':'Half Turn',           'criteria':['Stays in relev\u00e9 the entire turn','Arms freeze in crown during the turn','Toe stays at the knee the entire turn','Finishes the turn before stepping forward']},
            {'event':'BEAM', 'short':'Split Jump',          'criteria':['Straight legs','Minimum 90 degree split','Lands in the same spot it started']},
            {'event':'BEAM', 'short':'Cartwheel',           'criteria':['Second hand turned in','Head stays between arms','Kicks through vertical with straight legs']},
            {'event':'FLOOR','short':'Back\nHandspring',     'criteria':['Skill travels backwards','Hands hit with open shoulders and hips','Thumbs facing each other','Legs together and straight throughout']},
            {'event':'FLOOR','short':'Front\nHandspring',    'criteria':['Straight arms by ears throughout','Lands in a tight arch','Rebounds forward with straight legs']},
            {'event':'FLOOR','short':'Chass\u00e9\nSplit Leap',   'criteria':['Toes pointed in chass\u00e9','Minimum 120 degree split','Straight legs in the split']},
            {'event':'FLOOR','short':'Full Turn',           'criteria':['Arms stay in crown the entire turn','Stays in relev\u00e9 the entire turn','Toe stays at the knee the entire turn']},
            {'event':'FLOOR','short':'Back\nWalkover',       'criteria':['Front leg lifts as hands reach back','Straight legs throughout','Arms stay by ears']},
        ],
    },
    # ── Boys programs (HGA-specific) ──
    # Each event = one skill block. The items under each event are the criteria.
    # Final star ("3x in a row") is auto-added by the renderer.
    'Boys Level 1': {
        'has_safety': False,
        'has_mastery': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'FLOOR','short':'Floor',  'criteria':['Handstand','Cartwheel','Backward roll to feet','Bridge','Forward roll','Round off introduction']},
            {'event':'MUSHROOM','short':'Mushrooms /\nPommel Horse',  'criteria':['Walks arounds','Hop arounds','Swing 3/4','Swing Full']},
            {'event':'VAULT','short':'Vault',  'criteria':['Straight jump','Arm circle','Hurdle - Punch board - Fwd roll','Handstand Flatback']},
            {'event':'P BARS','short':'P Bars',  'criteria':['Monkey walks across bar','5 swings in a row','Forward support walks','Straddle travel']},
            {'event':'BARS','short':'Bars',  'criteria':['Casts','Forward Roll to Chin Hold 3 sec','Kickover Pullover','Skin the Cat Bwd & Fwd']},
        ],
    },
    'Boys Level 2': {
        'has_safety': False,
        'has_mastery': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'FLOOR','short':'Floor',  'criteria':['Cartwheel step-in Hollow body','Handstand forward roll','Backward roll','Handstand hold 2 sec','Handstand hold 2 sec bridge','Round Off']},
            {'event':'POMMEL','short':'Pommel\nHorse',  'criteria':['Mushroom 1/2 double leg circle','Swing leg 1/4 circle','5 whole circles feet in bucket','Prone horse swings 10 outside leg']},
            {'event':'RINGS','short':'Rings',  'criteria':['Pike hold 5 sec rings by ears','Swing fwd inverted hang','Skin the cat German hang 3 sec']},
            {'event':'VAULT','short':'Vault',  'criteria':['Handstand flat back','Resi HS fwd roll over cheese mat']},
            {'event':'P BARS','short':'P Bars',  'criteria':['L support hold 5 sec','Straddle travel straight legs','Straddle V support hold 5 sec','Support swings horizontal','Upper arm swing baby front up rise']},
            {'event':'H BARS','short':'H Bars',  'criteria':['Tap swing straight legs','Back hip circle assisted']},
        ],
    },
    'Boys Level 3': {
        'has_safety': False,
        'has_mastery': False,
        'footer_h': 18,
        'num_rows': 8,
        'skills': [
            {'event':'FLOOR','short':'Floor',  'criteria':['Back handspring','Round off rebound','Backbend kick over','Front limber','Front walkover','Handstand block','Handstand snap rebound']},
            {'event':'POMMEL','short':'Pommel\nHorse',  'criteria':['Mushroom 3/4 double leg circle','Mushroom circle assisted','10 whole circles feet in bucket','Prone horse swings 5 inside both legs']},
            {'event':'RINGS','short':'Rings',  'criteria':['5 swings shifting rings','Pike inverted to back lever German hang','Tuck support to L support return']},
            {'event':'VAULT','short':'Vault',  'criteria':['Resi HS flatback arm circle','Front handspring assisted']},
            {'event':'P BARS','short':'P Bars',  'criteria':['Support half turn support','Support swings above horizontal','Straddle support assisted','Support hops fwd & bwd']},
            {'event':'H BARS','short':'H Bars',  'criteria':['5 top swings','Back hip circle hollow body wrist shift','Cast straddle swing dismount']},
        ],
    },
}

# Alias mapping — iClassPro discipline text → program key
# Only full-form program names are accepted. Short abbreviations like
# "L1", "GL1", "LVL 1", "LEV1" are intentionally NOT matched — managers
# must use the full program name as documented in the SOP format guide.
PROGRAM_ALIASES = {
    'preschool': 'Preschool',
    'new preschool': 'Preschool',
    'junior': 'Junior',
    'new junior': 'Junior',
    'advanced junior': 'Advanced Junior',
    'adv junior': 'Advanced Junior',
    'new advanced junior': 'Advanced Junior',
    'girls level 1': 'Level 1',
    'level 1': 'Level 1',
    'girls level 2': 'Level 2',
    'level 2': 'Level 2',
    'girls level 3': 'Level 3',
    'level 3': 'Level 3',
    'boys level 1': 'Boys Level 1',
    'boys level 2': 'Boys Level 2',
    'boys level 3': 'Boys Level 3',
    # iClass HTML-encodes apostrophes (Boy's → Boy039s) — must match
    'boy039s level 1': 'Boys Level 1',
    'boy039s level 2': 'Boys Level 2',
    'boy039s level 3': 'Boys Level 3',
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

def _build_event_colors(gym):
    """A-B-A-B alternation per the spec:
      VAULT + BEAM  → event strip = gym['ev_brand'] if set, else gym['brand']
      BARS  + FLOOR → event strip = gym['ev_cool'] if set, else #646262 (gray)
    Each gym uses its own brand color for VAULT/BEAM.
    Gyms can override BARS/FLOOR by setting 'ev_cool' in their config
    (e.g. CCP uses its blue on Bars/Floor instead of gray).
    """
    brand = hex_color(gym.get('ev_brand', gym.get('brand', gym['red'])))
    dark  = hex_color(gym.get('ev_cool', '#646262'))
    stripe = hex_color('#e8e8e8')
    ev_dark = {
        'VAULT': brand, 'BEAM': brand,
        'BARS': dark,   'FLOOR': dark,
        'SAFETY': brand,
        'MUSHROOM': dark, 'POMMEL': dark,
        'P BARS': brand,  'H BARS': brand,
        'RINGS': dark,
    }
    ev_med   = {k: hex_color('#ffffff') for k in ev_dark}
    ev_light = {k: stripe for k in ev_dark}
    return ev_dark, ev_med, ev_light


# ── Apparatus icon PNGs (white linework on transparent — placed in colored bands)
import os as _os
_ICON_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'icons')
APPARATUS_ICON = {
    'VAULT': _os.path.join(_ICON_DIR, 'vault_solid.png'),
    'BARS':  _os.path.join(_ICON_DIR, 'bars_solid.png'),
    'BEAM':  _os.path.join(_ICON_DIR, 'beam_solid.png'),
    'FLOOR': _os.path.join(_ICON_DIR, 'floor_solid.png'),
}


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
def build_score_lookup(score_map, students, skills, has_mastery=True):
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

        # Final star row (only for programs with mastery)
        if has_mastery:
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
                 students, program, score_map, mode='eval', _canvas=None, ages='',
                 events_filter=None, criteria_orientation='auto'):
    """
    Returns PDF as bytes (single-page), or draws onto _canvas if provided (multi-page).
    mode: 'eval' = pre-fill scores | 'blank' = all empty
    events_filter: list of event names (e.g. ['VAULT','BARS']) — only those skills render.
                   None = all events (legacy behavior).
    criteria_orientation: 'rotated' | 'horizontal' | 'auto' (auto picks horizontal if
                          NUM_COLS small enough to fit text without wrapping pain).
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

    # v0-style unified palette
    BRAND       = hex_color(gym.get('brand', gym['red']))
    CHARCOAL    = hex_color('#262626')
    LIGHT_BG    = hex_color('#e8e8e8')
    TEXT_DARK   = hex_color('#1a1a1a')

    # Build event colors from this gym's brand (v0-style: single brand for all events)
    EV_DARK, EV_MED, EV_LIGHT = _build_event_colors(gym)

    SKILLS      = prog['skills']
    if events_filter:
        SKILLS = [sk for sk in SKILLS if sk['event'] in events_filter]
        if not SKILLS:
            raise ValueError(f"events_filter {events_filter} matched no skills in {prog_key}")
    HAS_SAF     = prog.get('has_safety', False)
    HAS_MASTERY = prog.get('has_mastery', True)  # default True for girls programs
    FOOTER_H    = prog.get('footer_h', 18)
    NUM_ROWS    = prog.get('num_rows', 6)
    SKILL_TEXT  = WHITE  # always white on the brand-colored skill header
    MAST        = 1 if HAS_MASTERY else 0  # extra column per skill for mastery star

    NUM_SKILLS = len(SKILLS)
    NUM_COLS   = sum(len(sk['criteria'])+MAST for sk in SKILLS)

    # Decide criteria orientation early so layout can adapt.
    if criteria_orientation == 'horizontal':
        USE_HORIZONTAL = True
    elif criteria_orientation == 'rotated':
        USE_HORIZONTAL = False
    else:  # auto
        USE_HORIZONTAL = (NUM_COLS <= 16)

    # Layout
    TOP_BAR_H  = 48
    EV_HDR_H   = 44   # event name (14) + skill name (30) — no icon
    SK_HDR_H   = 0
    STAR_LBL_H = 16 if USE_HORIZONTAL else 11  # taller label row when horizontal
    # Horizontal criteria text only needs ~50pt; rotated needs ~115-130pt.
    if USE_HORIZONTAL:
        CRIT_H = 50
    else:
        CRIT_H = 115 if HAS_SAF else 130

    CONTENT_TOP  = H - MARGIN - TOP_BAR_H
    CONTENT_BOT  = MARGIN + FOOTER_H
    HEADER_H     = EV_HDR_H + SK_HDR_H + CRIT_H + STAR_LBL_H
    DATA_TOP     = CONTENT_TOP - HEADER_H
    DATA_BOT     = CONTENT_BOT
    DATA_H       = DATA_TOP - DATA_BOT
    ROW_H        = DATA_H / NUM_ROWS
    NAME_ZONE_H  = 8
    NAME_W       = 68
    GRID_LEFT    = MARGIN + NAME_W
    GRID_W       = W - MARGIN - GRID_LEFT
    COL_W        = GRID_W / NUM_COLS

    # Score lookup
    if mode == 'eval' and score_map:
        lookup = build_score_lookup(score_map, students, SKILLS, has_mastery=HAS_MASTERY)
    else:
        lookup = {}   # blank mode

    # Column offsets
    skill_col_start = []
    col = 0
    for sk in SKILLS:
        skill_col_start.append(col)
        col += len(sk['criteria']) + MAST

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
    # OAS: purple top bar so the teal brand reads distinctly against it
    _top_bar_hex = gym.get('top_bar', '#252626')
    c.setFillColor(hex_color(_top_bar_hex))
    c.rect(MARGIN, bar_y, USABLE_W, TOP_BAR_H, fill=1, stroke=0)
    # Divider line separating header from the event blocks below
    # Use gold for gyms with warm/neutral brands; use brand color for others
    _warm_gyms = {'RBA', 'RBK', 'CCP', 'CPF', 'SGT', 'HGA'}
    _divider_hex = '#c9a43c' if gym_code in _warm_gyms else gym.get('brand', gym['red'])
    # For OAS specifically use the full teal (not the darkened ev_brand) for the divider
    if gym_code == 'OAS':
        _divider_hex = '#3eb29f'
    c.setFillColor(hex_color(_divider_hex))
    c.rect(MARGIN, bar_y - 3, USABLE_W, 3, fill=1, stroke=0)

    # Logo — check multiple paths for Vercel compatibility
    import os
    _here = os.path.dirname(os.path.abspath(__file__))
    logo_candidates = [
        os.path.join(_here, gym['logo']),
        os.path.join(_here, 'public', gym['logo']),
        os.path.join(_here, '..', 'public', gym['logo']),
        os.path.join(_here, '..', gym['logo']),
        os.path.join(_here, '..', '..', gym['logo']),
    ]
    logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)
    logo_size = 42
    logo_y    = bar_y + (TOP_BAR_H - logo_size) / 2

    # Center logo + gym name as a unit in the page
    c.setFont('Helvetica-Bold', 15)
    name_w  = c.stringWidth(gym['name'], 'Helvetica-Bold', 15)
    pair_w  = logo_size + 8 + name_w
    pair_x  = (W - pair_w) / 2
    logo_x  = pair_x
    text_x  = pair_x + logo_size + 8

    if logo_path:
        c.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto')

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 15)
    # Vertically center the gym name in the top bar (single-line layout)
    c.drawString(text_x, bar_y + TOP_BAR_H/2 - 5, gym['name'])

    # ── CLASS INFO (date / day / time / ages) — right-aligned in header ──
    # Build info string from whatever fields are present
    _info_parts = [p for p in [date, day, time, ages] if p and str(p).strip()]
    _info_str = '   |   '.join(_info_parts)
    if _info_str:
        # Draw below gym name, slightly smaller, light gray so it reads as secondary
        c.setFillColor(hex_color('#cccccc'))
        c.setFont('Helvetica', 8)
        c.drawString(text_x, bar_y + TOP_BAR_H/2 - 17, _info_str)

    # ── SCORE KEY (top-right of header bar) ──────────────────────────
    key_w, key_h = 108, 38
    key_x = W - MARGIN - key_w - 4
    key_y = bar_y + (TOP_BAR_H - key_h) / 2
    c.setFillColor(WHITE)
    c.setStrokeColor(CHARCOAL); c.setLineWidth(1.2)
    c.roundRect(key_x, key_y, key_w, key_h, 3, fill=1, stroke=1)
    # "Key:" label
    c.setFillColor(CHARCOAL); c.setFont('Helvetica-Bold', 6.5)
    c.drawCentredString(key_x + key_w/2, key_y + key_h - 9, 'SCORE KEY')
    # Three items evenly spaced
    item_cx = [key_x + key_w*0.18, key_x + key_w*0.50, key_x + key_w*0.82]
    sym_y   = key_y + key_h - 22
    lbl_y   = key_y + 3
    sym_r   = 6.5
    # Circle (Not Yet)
    c.setFillColor(WHITE); c.setStrokeColor(hex_color('#aaaaaa')); c.setLineWidth(1.4)
    c.circle(item_cx[0], sym_y, sym_r, fill=1, stroke=1)
    # Brand star (Earned)
    draw_star(c, item_cx[1], sym_y, sym_r*1.15, BRAND, BRAND, lw=0)
    # Gold star (Skill Complete)
    draw_star(c, item_cx[2], sym_y, sym_r*1.15, GOLD, hex_color('#8a6a00'), lw=0.5)
    # Labels
    c.setFillColor(CHARCOAL); c.setFont('Helvetica', 5.2)
    c.drawCentredString(item_cx[0], lbl_y, 'Not Yet')
    c.drawCentredString(item_cx[1], lbl_y, 'Earned')
    c.drawCentredString(item_cx[2], lbl_y, 'Skill Complete')

    # ── HEADER: EVENT BANDS ───────────────────────────────────────────
    # Two stacked zones inside EV_HDR_H, both on same colored bg:
    #   • event-name zone (top, 14pt): VAULT/BARS/BEAM/FLOOR — per skill block
    #   • skill-name zone (bottom, 30pt): per-skill name, bold white text
    # Mastery cols stay colored in the header; black "3 ★ in a row" treatment
    # only kicks in in the criteria zone below.
    ev_top        = CONTENT_TOP
    ev_name_h     = 14
    skill_name_h  = EV_HDR_H - ev_name_h
    icon_zone_h   = 0  # no icons in this concept
    BLACK_BG      = hex_color('#1a1a1a')

    # Three zones, all on same colored bg per skill:
    #   y range [ev_top-ev_name_h, ev_top]                       -> event name
    #   y range [ev_top-ev_name_h-icon_zone_h, ...]              -> icon
    #   y range [ev_top-EV_HDR_H, ev_top-ev_name_h-icon_zone_h]  -> skill name
    # Mastery columns: solid black full-height with rotated '3 ★ in a row'.

    ev_name_y_bottom    = ev_top - ev_name_h
    icon_y_bottom       = ev_name_y_bottom - icon_zone_h
    skill_name_y_bottom = icon_y_bottom - skill_name_h  # == ev_top - EV_HDR_H

    # Pass 1: for each skill, paint a colored block covering ALL its columns
    # (criteria + mastery), then place icon + skill name on that block.
    # The mastery column stays colored here in the header zone — the black
    # "3★ in a row" treatment only starts in the criteria zone below.
    FONT_SKILL = 'Helvetica-Bold'
    SIZE_SKILL = 8.5
    LINE_SKILL = 9.5
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        ev_color = EV_DARK.get(ev, BRAND)
        icon_path = APPARATUS_ICON.get(ev)
        n_crit = len(sk['criteria'])
        total_cols = n_crit + MAST
        block_start_x = ev_x(skill_col_start[i])
        block_w = total_cols * COL_W

        # Fill event-name zone (top) with full brand or charcoal color
        c.setFillColor(ev_color)
        c.rect(block_start_x, ev_name_y_bottom, block_w, ev_name_h, fill=1, stroke=0)
        # Skill-name zone (bottom) — per-gym pattern:
        #   VAULT/BEAM  → 40% darker shade of gym's brand color
        #   BARS/FLOOR  → 40% darker shade of ev_cool (or near-black if no ev_cool set)
        # White text on both.
        is_bright_event = ev in ('VAULT', 'BEAM', 'SAFETY', 'P BARS', 'H BARS')
        if is_bright_event:
            skill_bg_hex = _darken(gym.get('ev_brand', gym.get('brand', gym['red'])), 0.40)
        else:
            ev_cool_hex = gym.get('ev_cool')
            skill_bg_hex = _darken(ev_cool_hex, 0.40) if ev_cool_hex else '#1a1a1a'
        skill_fg_hex = '#ffffff'
        c.setFillColor(hex_color(skill_bg_hex))
        c.rect(block_start_x, skill_name_y_bottom, block_w, skill_name_h, fill=1, stroke=0)

        name = sk['short']
        lines = name.split('\n') if '\n' in name else [name]
        max_w_available = block_w - 3
        # 1. Shrink font progressively down to 5.5pt to fit the widest line
        size = SIZE_SKILL
        while size > 5.5 and any(c.stringWidth(ln, FONT_SKILL, size) > max_w_available for ln in lines):
            size -= 0.5
        # 2. If any line still overflows at min font, wrap that line in half
        def _wrap(ln, size):
            if c.stringWidth(ln, FONT_SKILL, size) <= max_w_available:
                return [ln]
            words = ln.split()
            if len(words) < 2:
                return [ln]
            mid = max(1, len(words)//2)
            return [' '.join(words[:mid]), ' '.join(words[mid:])]
        wrapped = []
        for ln in lines:
            wrapped.extend(_wrap(ln, size))
        lines = wrapped[:4]  # hard cap at 4 lines

        line_h = size + 1.0  # tight line spacing to fit multi-line
        # total text block height
        total_h = len(lines) * line_h
        # if total text block exceeds the strip, shrink size further and retry line_h
        while total_h > skill_name_h - 2 and size > 5.0:
            size -= 0.5
            line_h = size + 1.0
            total_h = len(lines) * line_h

        cx = block_start_x + block_w/2
        strip_cy = skill_name_y_bottom + skill_name_h/2
        start_y = strip_cy + (len(lines)-1)*line_h/2 - size/3
        # Text color = opposite of skill strip bg (set above)
        c.setFillColor(hex_color(skill_fg_hex))
        c.setFont(FONT_SKILL, size)
        for li, ln in enumerate(lines):
            c.drawCentredString(cx, start_y - li*line_h, ln)

    # Pass 2: event-name TEXT centered in its zone per skill block
    # (fill already drawn in Pass 1)
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        n_crit = len(sk['criteria'])
        total_cols = n_crit + MAST
        block_start_x = ev_x(skill_col_start[i])
        block_w = total_cols * COL_W
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 9.5)
        c.drawCentredString(block_start_x + block_w/2, ev_name_y_bottom + 4, ev)

    # Thin white vertical dividers between adjacent same-event skill blocks
    # so two pink bars icons (or two charcoal floor icons) don't blur together.
    c.setStrokeColor(hex_color('#ffffff')); c.setLineWidth(0.7)
    for i in range(1, len(SKILLS)):
        if SKILLS[i]['event'] == SKILLS[i-1]['event']:
            dx = ev_x(skill_col_start[i])
            c.line(dx, skill_name_y_bottom, dx, ev_top)

    # Program label block — BRAND color, extends from event-header top all the way
    # to data area bottom (replaces the old charcoal strip above NAME). Gives the
    # program name maximum vertical breathing room and creates a continuous brand
    # strip down the left side instead of a cramped label in the middle.
    prog_block_h = HEADER_H  # full height (was HEADER_H - EV_HDR_H before)
    c.setFillColor(BRAND)
    c.rect(MARGIN, DATA_TOP, NAME_W, prog_block_h, fill=1, stroke=0)

    # Large rotated program name in the block — auto-size so long words (PRESCHOOL)
    # don't get clipped against the rotated column's vertical edges. Center
    # ABOVE the NAME strip (bottom STAR_LBL_H zone) so the rotated word doesn't
    # run into "NAME".
    label_parts = prog_key.upper().split()
    prog_cx = MARGIN + NAME_W / 2
    # Shift the text center up by half of STAR_LBL_H so the word sits in the
    # space above the NAME row.
    prog_cy = DATA_TOP + (prog_block_h + STAR_LBL_H) / 2
    from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
    # Available vertical extent for the rotated word: full block minus the
    # NAME strip minus a little padding.
    _avail_w = prog_block_h - STAR_LBL_H - 16
    c.saveState()
    c.translate(prog_cx, prog_cy)
    c.rotate(90)
    c.setFillColor(WHITE)
    if len(label_parts) == 2:
        # "ADVANCED JUNIOR", "BOYS LEVEL 1" — 2 lines
        _size2 = 22
        _longest = max(label_parts, key=len)
        while _size2 >= 14 and _sw(_longest, 'Helvetica-Bold', _size2) > _avail_w:
            _size2 -= 1
        c.setFont('Helvetica-Bold', _size2)
        c.drawCentredString(0,  _size2 * 0.55, label_parts[0])
        c.drawCentredString(0, -_size2 * 0.75, label_parts[1])
    else:
        # "PRESCHOOL", "JUNIOR" — single line. Auto-shrink to fit.
        _word = label_parts[0]
        _size1 = 26
        while _size1 >= 14 and _sw(_word, 'Helvetica-Bold', _size1) > _avail_w:
            _size1 -= 1
        c.setFont('Helvetica-Bold', _size1)
        c.drawCentredString(0, -_size1 / 3, _word)
    c.restoreState()

    # Skill names are now drawn inside the colored EV_HDR block above.
    sk_top = ev_top - EV_HDR_H

    # ── HEADER: CRITERIA (rotated OR horizontal) ─────────────────────
    # USE_HORIZONTAL was decided earlier so layout could adapt CRIT_H.
    crit_top = sk_top - SK_HDR_H
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        crits_all  = sk['criteria'] + (['3× in a row'] if HAS_MASTERY else [])
        star_labels = [f'★{j+1}' for j in range(len(sk['criteria']))] + (['★F'] if HAS_MASTERY else [])
        for j, (star, crit) in enumerate(zip(star_labels, crits_all)):
            col_x    = ev_x(skill_col_start[i]+j)
            is_final = (j == len(sk['criteria']))
            bg = EV_DARK.get(ev, BRAND) if is_final else LIGHT_BG
            c.setFillColor(bg)
            c.rect(col_x, crit_top-CRIT_H, COL_W, CRIT_H, fill=1, stroke=0)
            c.setStrokeColor(hex_color('#cccccc'))
            c.setLineWidth(0.3)
            c.line(col_x, crit_top-CRIT_H, col_x, crit_top)
            fg = WHITE if is_final else TEXT_DARK

            if USE_HORIZONTAL:
                # Word-wrap the criteria text horizontally inside the cell.
                # Mastery column ("3× in a row") gets bigger font since the text
                # is short and this column deserves emphasis.
                _font = 'Helvetica-Bold'
                _size = 13.0 if is_final else 9.0
                _max_w = COL_W - 4
                _max_h = CRIT_H - 6

                def _wrap_horiz(text, font, size, max_w, canvas_obj):
                    words = text.split()
                    lines, current = [], ''
                    for w in words:
                        trial = (current + ' ' + w).strip()
                        if canvas_obj.stringWidth(trial, font, size) <= max_w:
                            current = trial
                        else:
                            if current:
                                lines.append(current)
                            current = w
                    if current:
                        lines.append(current)
                    return lines

                # Shrink font until wrapped block fits vertically
                _lines = _wrap_horiz(crit, _font, _size, _max_w, c)
                while (len(_lines) * (_size + 2) > _max_h or
                       any(c.stringWidth(ln, _font, _size) > _max_w for ln in _lines)) \
                      and _size > 6.5:
                    _size -= 0.5
                    _lines = _wrap_horiz(crit, _font, _size, _max_w, c)

                _lh = _size + 2
                _total_h = len(_lines) * _lh
                _cy = crit_top - CRIT_H/2
                _cx = col_x + COL_W/2
                _start_y = _cy + _total_h/2 - _size
                c.setFillColor(fg); c.setFont(_font, _size)
                for _li, _ln in enumerate(_lines):
                    c.drawCentredString(_cx, _start_y - _li * _lh, _ln)
            else:
                # Rotated path (Page 2 / Beam+Floor)
                c.saveState()
                c.translate(col_x+COL_W/2, crit_top-CRIT_H/2)
                c.rotate(90)
                _crit_max_w = CRIT_H - 10
                _font = 'Helvetica-Bold'
                _size = 7.5
                def _split_crit(text, font, size, max_w, canvas_obj):
                    while size >= 5.5 and canvas_obj.stringWidth(text, font, size) > max_w:
                        size -= 0.5
                    if canvas_obj.stringWidth(text, font, size) <= max_w:
                        return [text], size
                    words = text.split()
                    best = None
                    for split in range(1, len(words)):
                        l1 = ' '.join(words[:split])
                        l2 = ' '.join(words[split:])
                        if canvas_obj.stringWidth(l1, font, size) <= max_w and \
                           canvas_obj.stringWidth(l2, font, size) <= max_w:
                            best = ([l1, l2], size)
                            break
                    if best:
                        return best
                    return [_truncate_to_width(canvas_obj, text, font, size, max_w)], size
                _lines, _size = _split_crit(crit, _font, _size, _crit_max_w, c)
                c.setFillColor(fg); c.setFont(_font, _size)
                _lh = _size + 1.5
                _total_h = len(_lines) * _lh
                # Baseline offset for proper visual centering. In the rotated
                # frame, the text's ascender/descender causes the visual
                # midpoint to sit ~size/2 above the baseline. Shift baseline
                # by -_size so the text block's visual center lands at y=0.
                _start_y = _total_h / 2 - _size
                for _li, _ln in enumerate(_lines):
                    c.drawCentredString(0, _start_y - _li * _lh, _ln)
                c.restoreState()

    # ── HEADER: STAR LABELS ───────────────────────────────────────────
    starlbl_top = crit_top - CRIT_H
    _lbl_font_sz  = 10 if USE_HORIZONTAL else 6.5
    _lbl_gold_r   = 8.5 if USE_HORIZONTAL else 5.5
    for i, sk in enumerate(SKILLS):
        ev = sk['event']
        star_labels = [f'★{j+1}' for j in range(len(sk['criteria']))] + (['★F'] if HAS_MASTERY else [])
        for j, star in enumerate(star_labels):
            col_x    = ev_x(skill_col_start[i]+j)
            is_final = HAS_MASTERY and (j == len(sk['criteria']))
            c.setFillColor(GOLD if is_final else WHITE)
            c.setStrokeColor(hex_color('#cccccc')); c.setLineWidth(0.3)
            c.rect(col_x, starlbl_top-STAR_LBL_H, COL_W, STAR_LBL_H, fill=1, stroke=1)
            if is_final:
                draw_star(c, col_x+COL_W/2, starlbl_top-STAR_LBL_H/2+0.5,
                          _lbl_gold_r, WHITE, WHITE, lw=0)
            else:
                c.setFillColor(BRAND)
                c.setFont('Helvetica-Bold', _lbl_font_sz)
                c.drawCentredString(col_x+COL_W/2,
                                    starlbl_top-STAR_LBL_H/2 - _lbl_font_sz/3,
                                    star)

    # "NAME" label in navy block
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(MARGIN+NAME_W/2, starlbl_top-STAR_LBL_H/2-2, 'NAME')


    # ── STUDENT ROWS ──────────────────────────────────────────────────
    for row in range(NUM_ROWS):
        ry = row_y(row)
        c.setFillColor(WHITE if row%2==0 else hex_color('#edf0f4'))
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

        # Bubbles centered in the row
        bubble_zone_top    = ry + ROW_H
        bubble_zone_bottom = ry + NAME_ZONE_H
        bubble_cy = (bubble_zone_top + bubble_zone_bottom) / 2

        for i in range(NUM_SKILLS):
            sk     = SKILLS[i]
            n_crit = len(sk['criteria'])
            for j in range(n_crit+MAST):
                col_x    = ev_x(skill_col_start[i]+j)
                cx       = col_x + COL_W/2
                _bub_factor_w = 0.26 if USE_HORIZONTAL else 0.36
                _bub_factor_h = 0.32 if USE_HORIZONTAL else 0.38
                r_bub    = min(COL_W*_bub_factor_w, (ROW_H-NAME_ZONE_H)*_bub_factor_h)
                is_final = HAS_MASTERY and (j == n_crit)

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
                        draw_star(c, cx, bubble_cy, r_bub*1.2, BRAND, BRAND, lw=0)
                    else:
                        c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(1.2)
                        c.circle(cx, bubble_cy, r_bub, fill=1, stroke=1)

    # ── GRID LINES ────────────────────────────────────────────────────
    for i, sk in enumerate(SKILLS):
        x = ev_x(skill_col_start[i])
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.7)
        c.line(x, DATA_BOT, x, DATA_TOP)
    c.line(ev_x(NUM_COLS), DATA_BOT, ev_x(NUM_COLS), DATA_TOP)

    for i, sk in enumerate(SKILLS):
        x = ev_x(skill_col_start[i])
        c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.35)
        c.line(x, starlbl_top-STAR_LBL_H, x, ev_top-EV_HDR_H)
    c.line(ev_x(NUM_COLS), starlbl_top-STAR_LBL_H, ev_x(NUM_COLS), ev_top-EV_HDR_H)

    for i, sk in enumerate(SKILLS):
        for j in range(1, len(sk['criteria'])+MAST):
            x = ev_x(skill_col_start[i]+j)
            c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.4)
            c.line(x, starlbl_top-STAR_LBL_H, x, sk_top-SK_HDR_H)

    c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
    for row in range(NUM_ROWS+1):
        y = DATA_TOP - row*ROW_H
        c.line(MARGIN, y, W-MARGIN, y)

    c.setStrokeColor(CHARCOAL); c.setLineWidth(1.0)
    c.line(MARGIN+NAME_W, CONTENT_BOT, MARGIN+NAME_W, CONTENT_TOP)
    c.line(MARGIN, DATA_TOP, W-MARGIN, DATA_TOP)

    # Clean charcoal divider between data area and safety footer.
    # Drawn here AND re-drawn after safety fills so it can't be painted over.
    c.setStrokeColor(CHARCOAL); c.setLineWidth(1.0)
    c.line(MARGIN, CONTENT_BOT, W-MARGIN, CONTENT_BOT)

    c.setStrokeColor(CHARCOAL); c.setLineWidth(0.8)
    c.line(MARGIN, CONTENT_TOP, W-MARGIN, CONTENT_TOP)

    # ── SAFETY FOOTER ─────────────────────────────────────────────────
    if HAS_SAF:
        ft_y = MARGIN
        ft_h = FOOTER_H
        SAF_CRIT = prog.get('safety_criteria', ['Follows directions','Stays with the group','Keeps hands to self'])

        SAF_BG = hex_color('#eeeeee')
        c.setFillColor(SAF_BG)
        c.rect(MARGIN, ft_y, USABLE_W, ft_h, fill=1, stroke=0)
        # NOTE: safety border is drawn at the END of this block so the per-column
        # fills below cannot paint over the top edge.

        SAF_LBL_W = 52
        c.setFillColor(BRAND)
        c.rect(MARGIN, ft_y, SAF_LBL_W, ft_h, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-13, 'SAFETY')
        c.setFillColor(WHITE); c.setFont('Helvetica-Oblique', 4.8)
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-22, 'assessed')
        c.drawCentredString(MARGIN+SAF_LBL_W/2, ft_y+ft_h-29, 'each class')

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
                c.setFillColor(BRAND)
                c.setFont('Helvetica-Bold', 7)
                c.drawString(key_x, ky+row_h_key/2-2, star)
            c.setFillColor(BRAND if is_f else CCP_GRAY_DK)
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
            c.setFillColor(SAF_BG)
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
                    c.setFillColor(BRAND); c.setFont('Helvetica-Bold', 6)
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
                        draw_star(c, bx, bub_cy, bub_r*1.15, BRAND, BRAND, lw=0)
                    else:
                        c.setFillColor(WHITE); c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.8)
                        c.circle(bx, bub_cy, bub_r, fill=1, stroke=1)

            if col > 0:
                c.setStrokeColor(CCP_GRAY_MID); c.setLineWidth(0.5)
                c.line(sx, ft_y+3, sx, ft_y+ft_h-3)

        # Border drawn LAST so per-column fills can't paint over the top edge.
        c.setStrokeColor(CHARCOAL); c.setLineWidth(1.2)
        c.rect(MARGIN, ft_y, USABLE_W, ft_h, fill=0, stroke=1)

    # ── OUTER BORDER ──────────────────────────────────────────────────
    c.setStrokeColor(CHARCOAL); c.setLineWidth(0.8)
    c.rect(MARGIN, MARGIN, USABLE_W, USABLE_H, fill=0, stroke=1)

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
    Returns one PDF with one page per class (or multiple pages if class exceeds row capacity).
    """
    buf = io.BytesIO()
    c   = canvas.Canvas(buf, pagesize=landscape(letter))

    first_page = True
    for cls in classes:
        program   = cls.get('program', '')
        students  = cls.get('students', [])
        score_map = cls.get('scoreMap', {})

        # Determine row capacity for this program — skip unrecognized programs (Ninja, Xcel, etc.)
        prog_key = resolve_program(program)
        prog     = PROGRAMS.get(prog_key)
        if not prog:
            continue
        capacity = prog.get('num_rows', 6)

        # Split students into pages if over capacity
        if len(students) == 0:
            chunks = [[]]
        else:
            chunks = [students[i:i+capacity] for i in range(0, len(students), capacity)]

        total_pages = len(chunks)
        for chunk_idx, chunk in enumerate(chunks):
            if not first_page:
                c.showPage()
            first_page = False

            # Add page label to class name if overflow
            class_name = cls.get('className', 'Class')
            if total_pages > 1:
                class_name = f"{class_name}  (pg {chunk_idx+1}/{total_pages})"

            # Slice score_map columns for this page's students
            chunk_score_map = _slice_score_map(score_map, chunk_idx * capacity, capacity)

            generate_pdf(
                gym_code   = gym_code,
                class_name = class_name,
                date       = cls.get('date', ''),
                day        = cls.get('day', ''),
                time       = cls.get('time', ''),
                ages       = cls.get('ages', ''),
                students   = chunk,
                program    = program,
                score_map  = chunk_score_map,
                mode       = mode,
                _canvas    = c,
            )

    c.save()
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════
# SPLIT GENERATOR — each class becomes N pages grouped by event-set
# ════════════════════════════════════════════════════════════════════
def generate_split_pdf(gym_code, classes, page_events, mode='eval'):
    """
    Like generate_multi_pdf but each class is split across multiple pages based
    on page_events — a list of event-name lists, one per page.

    Example — two pages, Vault+Bars on p1, Beam+Floor on p2:
        page_events = [['VAULT','BARS'], ['BEAM','FLOOR']]

    Each page uses only those events (via events_filter on generate_pdf).
    The criteria orientation auto-picks (horizontal for ≤16 columns, rotated otherwise).
    Page 1 of Vault+Bars typically gets horizontal text = much more readable.
    """
    buf = io.BytesIO()
    c   = canvas.Canvas(buf, pagesize=landscape(letter))
    first_page = True

    for cls in classes:
        program   = cls.get('program', '')
        students  = cls.get('students', [])
        score_map = cls.get('scoreMap', {})

        prog_key = resolve_program(program)
        prog     = PROGRAMS.get(prog_key)
        if not prog:
            continue
        capacity = prog.get('num_rows', 6)

        if len(students) == 0:
            chunks = [[]]
        else:
            chunks = [students[i:i+capacity] for i in range(0, len(students), capacity)]

        total_student_pages = len(chunks)

        for chunk_idx, chunk in enumerate(chunks):
            for page_idx, ev_list in enumerate(page_events):
                if not first_page:
                    c.showPage()
                first_page = False

                class_name = cls.get('className', 'Class')
                label_parts = []
                if total_student_pages > 1:
                    label_parts.append(f"pg {chunk_idx+1}/{total_student_pages}")
                if len(page_events) > 1:
                    label_parts.append(' + '.join(ev_list))
                if label_parts:
                    class_name = f"{class_name}  ({'  |  '.join(label_parts)})"

                chunk_score_map = _slice_score_map(score_map, chunk_idx * capacity, capacity)

                generate_pdf(
                    gym_code      = gym_code,
                    class_name    = class_name,
                    date          = cls.get('date', ''),
                    day           = cls.get('day', ''),
                    time          = cls.get('time', ''),
                    ages          = cls.get('ages', ''),
                    students      = chunk,
                    program       = program,
                    score_map     = chunk_score_map,
                    mode          = mode,
                    _canvas       = c,
                    events_filter = ev_list,
                )

    c.save()
    return buf.getvalue()


# ── Score map slicer (for overflow pagination) ──────────────────────
def _slice_score_map(score_map, start, count):
    """Slice student columns from a score_map for a paginated chunk."""
    sliced = {}
    for apparatus, rows in score_map.items():
        sliced[apparatus] = [
            (row[start:start+count] if row else [])
            for row in rows
        ]
    return sliced


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
