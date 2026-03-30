from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
import math

W, H = landscape(letter)
c = canvas.Canvas("C:/Users/Jayme/Downloads/eval-grid-twoup-clean.pdf", pagesize=(W, H))

RED = HexColor('#CC1724')
DARK = HexColor('#333333')
LGRAY = HexColor('#F0F0F0')
MGRAY = HexColor('#E2E2E2')
DGRAY = HexColor('#999999')
TXTCOLOR = HexColor('#262626')

students = ['Elliana J.', 'Raiylah J.', 'Ellie T.', 'Adelyne Z.', 'Sofia M.', 'Harper L.']

skills = [
    ('VAULT', 'Run + Hurdle to Two-Foot Jump', ['Runs into hurdle, no stopping', 'Hurdles off one foot to both', 'Arms by ears in jump']),
    ('BARS', 'Front Support Fwd Roll (spot)', ['Unassisted front support 3 sec', 'Looks at belly while rolling', 'Hands stay on bar until complete']),
    ('BARS', 'Tuck Hang', ['Holds for 3 sec', 'Knees above belly button', 'Arms by ears']),
    ('BEAM', 'Walk Across Low Beam', ['Chest up, arms out to side', 'Steps heel to toe', 'Walks across without wobbles']),
    ('BEAM', 'Bear Crawl on Line', ['Hands on the line', 'Feet on the line', 'Straight legs']),
    ('BEAM', 'Backward Walk with Coach', ['Chest up, arms out to side', 'Steps heel to toe backward', 'Eyes forward while walking']),
    ('FLOOR', 'Monkey Jump Over Panel Mat', ['Turns hands to favorite foot', 'Jumps over without touching', 'Start & finish arms up']),
    ('FLOOR', 'Backward HS Walk Up (5 sec)', ['Walks feet up, hips over shoulders', 'Straight arms covering ears', 'Straight back']),
    ('FLOOR', 'Forward Roll Down Wedge', ['Starts in pencil shape', 'Eyes on belly', 'Stands up without hands']),
    ('FLOOR', 'Tabletop Hold', ['Holds for 5 sec', 'Back flat, no sagging hips', 'Fingers facing feet']),
    ('SAFETY', 'Safety', ['Follows directions', 'Stays with the group', 'Keeps hands to self']),
]

MARGIN = 18
GAP = 12
BLOCK_W = (W - 2 * MARGIN - GAP) / 2
STAR_COL = 22
CRIT_COL = 150
STU_COL_W = (BLOCK_W - STAR_COL - CRIT_COL) / 6
HEADER_H = 22
NAME_ROW_H = 40
EVENT_H = 14
TITLE_H = 16
CRIT_H = 18
MASTERY_H = 18


def block_x(side):
    return MARGIN if side == 0 else MARGIN + BLOCK_W + GAP


def draw_star_outline(c, cx, cy, size=7, points=5):
    outer = size
    inner = size * 0.38
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        angle = math.pi / 2 + i * math.pi / points
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    p = c.beginPath()
    p.moveTo(pts[0][0], pts[0][1])
    for pt in pts[1:]:
        p.lineTo(pt[0], pt[1])
    p.close()
    c.drawPath(p, stroke=1, fill=0)


def draw_filled_star(c, cx, cy, size=7, points=5):
    outer = size
    inner = size * 0.38
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        angle = math.pi / 2 + i * math.pi / points
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    p = c.beginPath()
    p.moveTo(pts[0][0], pts[0][1])
    for pt in pts[1:]:
        p.lineTo(pt[0], pt[1])
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# Header bar
y = H - MARGIN
for side in range(2):
    bx = block_x(side)
    c.setFillColor(RED)
    c.rect(bx, y - HEADER_H, BLOCK_W, HEADER_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(bx + 8, y - 15, 'HGA')
    c.setFont('Helvetica', 7)
    c.drawString(bx + 40, y - 15, 'Houston Gymnastics Academy  \u00b7  Preschool  \u00b7  Mon 3:30')

y -= HEADER_H

# Student names row
for side in range(2):
    bx = block_x(side)
    c.setFillColor(MGRAY)
    c.rect(bx, y - NAME_ROW_H, BLOCK_W, NAME_ROW_H, fill=1, stroke=0)
    c.setFillColor(TXTCOLOR)
    c.setFont('Helvetica-Bold', 7)
    for i, name in enumerate(students):
        sx = bx + STAR_COL + CRIT_COL + i * STU_COL_W + STU_COL_W / 2
        c.saveState()
        c.translate(sx, y - NAME_ROW_H + 4)
        c.rotate(45)
        c.drawString(0, 0, name)
        c.restoreState()

    c.setFont('Helvetica', 6)
    c.setFillColor(DGRAY)
    c.drawString(bx + 4, y - NAME_ROW_H / 2 - 2, 'Skill / Criteria')

y -= NAME_ROW_H


def draw_event_band(y_pos, side, event_name):
    bx = block_x(side)
    c.setFillColor(RED)
    c.rect(bx, y_pos - EVENT_H, BLOCK_W, EVENT_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7)
    tw = c.stringWidth(event_name, 'Helvetica-Bold', 7)
    c.drawString(bx + BLOCK_W / 2 - tw / 2, y_pos - 10, event_name)


def draw_skill_block(y_pos, side, skill_name, criteria):
    bx = block_x(side)

    # Title bar
    c.setFillColor(DARK)
    c.rect(bx, y_pos - TITLE_H, BLOCK_W, TITLE_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(bx + 6, y_pos - 11, skill_name)

    cy = y_pos - TITLE_H

    # Criteria rows
    for ci, crit in enumerate(criteria):
        bg = LGRAY if ci % 2 == 1 else white
        c.setFillColor(bg)
        c.rect(bx, cy - CRIT_H, BLOCK_W, CRIT_H, fill=1, stroke=0)

        # Border
        c.setStrokeColor(HexColor('#D0D0D0'))
        c.setLineWidth(0.5)
        c.rect(bx, cy - CRIT_H, BLOCK_W, CRIT_H, fill=0, stroke=1)

        # Star number
        c.setFillColor(RED)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(bx + STAR_COL / 2, cy - 12, f'\u2605{ci + 1}')

        # Criteria text
        c.setFillColor(TXTCOLOR)
        c.setFont('Helvetica', 7.5)
        c.drawString(bx + STAR_COL + 4, cy - 12, crit)

        # Student stars
        c.setStrokeColor(HexColor('#CCCCCC'))
        c.setLineWidth(0.8)
        for si in range(6):
            sx = bx + STAR_COL + CRIT_COL + si * STU_COL_W + STU_COL_W / 2
            draw_star_outline(c, sx, cy - CRIT_H / 2, size=7)

        cy -= CRIT_H

    # Mastery row
    c.setFillColor(white)
    c.rect(bx, cy - MASTERY_H, BLOCK_W, MASTERY_H, fill=1, stroke=0)
    c.setStrokeColor(HexColor('#D0D0D0'))
    c.rect(bx, cy - MASTERY_H, BLOCK_W, MASTERY_H, fill=0, stroke=1)

    c.setFillColor(HexColor('#DAA520'))
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(bx + STAR_COL / 2, cy - 13, '\u2605')

    c.setFillColor(DGRAY)
    c.setFont('Helvetica-Oblique', 7)
    c.drawString(bx + STAR_COL + 4, cy - 12, '3x in a row')

    c.setStrokeColor(HexColor('#DDDDDD'))
    c.setLineWidth(0.8)
    for si in range(6):
        sx = bx + STAR_COL + CRIT_COL + si * STU_COL_W + STU_COL_W / 2
        draw_star_outline(c, sx, cy - MASTERY_H / 2, size=7)


# Layout skills two-up
skill_idx = 0
last_event = ['', '']

while skill_idx < len(skills):
    left = skills[skill_idx]
    right = skills[skill_idx + 1] if skill_idx + 1 < len(skills) else None

    # Event bands
    need_band_l = left[0] != last_event[0]
    need_band_r = right and right[0] != last_event[1]

    if need_band_l or need_band_r:
        if need_band_l:
            draw_event_band(y, 0, left[0])
            last_event[0] = left[0]
        if need_band_r:
            draw_event_band(y, 1, right[0])
            last_event[1] = right[0]
        elif right:
            draw_event_band(y, 1, right[0])
        y -= EVENT_H

    # Skill blocks
    draw_skill_block(y, 0, left[1], left[2])
    if right:
        draw_skill_block(y, 1, right[1], right[2])

    block_h = TITLE_H + len(left[2]) * CRIT_H + MASTERY_H
    y -= block_h
    skill_idx += 2

# Footer
y -= 8
c.setFillColor(DGRAY)
c.setFont('Helvetica', 5.5)
c.drawString(MARGIN, y, '\u2605 red = criterion passed  \u00b7  \u2605 gold = all criteria mastered 3\u00d7 in a row')
c.drawRightString(W - MARGIN, y, 'Skills & Stars \u00b7 Preschool \u00b7 Houston Gymnastics Academy')

c.save()
print('Saved to C:/Users/Jayme/Downloads/eval-grid-twoup-clean.pdf')
