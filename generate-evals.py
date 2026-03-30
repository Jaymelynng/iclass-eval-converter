import pymupdf, json, re, sys

# Parse roll sheet
doc = pymupdf.open('C:/Users/Jayme/Downloads/Roll_Sheets_03-23-2026.pdf')
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
                try:
                    int(line); continue
                except: students.append(line.strip())
    pu = program.upper()
    prog = None
    if 'PRESCHOOL' in pu: prog = 'Preschool'
    elif 'JUNIOR' in pu: prog = 'Junior'
    elif 'GIRLS L1' in pu: prog = 'Girls Level 1'
    elif 'GIRLS L2' in pu: prog = 'Girls Level 2'
    elif 'GIRLS L3' in pu: prog = 'Girls Level 3'
    if prog:
        classes.append({'program':prog,'instructor':instructor,'schedule':schedule,'display':class_display,'students':students})

print(f"Parsed {len(classes)} classes")

# Read working prototype CSS
with open('C:/Users/Jayme/JAYME PROJECTS/ICLASS SUCKS/star-chart-eval-final.html', encoding='utf-8') as f:
    proto = f.read()
css_match = re.search(r'<style>(.*?)</style>', proto, re.DOTALL)
css = css_match.group(1) if css_match else ''

skills_l1 = [
    {"evt":"VAULT","ec":"v","name":"Straight Jump<br>to Resi","crit":["Accelerates into hurdle","Arms down/up","Str body & legs"]},
    {"evt":"VAULT","ec":"v","name":"Handstand<br>Flatback","crit":["Feet together at vert","Str line hands\u2192toes","Lands flat, one piece"]},
    {"evt":"BARS","ec":"b","name":"Kick Pullover","crit":["Chin at bar til toes over","Shifts hands fwd","Str legs throughout"]},
    {"evt":"BARS","ec":"b","name":"Cast","crit":["Str arms throughout","Legs str & together","Str line shldrs\u2192toes"]},
    {"evt":"BARS","ec":"b","name":"Fr Support \u2192<br>Fwd Roll Dn","crit":["Front supp str arms","Chin to chest","Legs tog, lowers slowly"]},
    {"evt":"BEAM","ec":"e","name":"Beam Mount","crit":["Jump to front supp","Leg over, no touch","Stand, arms by ears"]},
    {"evt":"BEAM","ec":"e","name":"Lever","crit":["Arms by ears","Str line fingers\u2192foot","Back leg straight"]},
    {"evt":"BEAM","ec":"e","name":"Relev\u00e9 Walk","crit":["Heels off entire walk","Str legs throughout","Chest up, arms out"]},
    {"evt":"BEAM","ec":"e","name":"Straight Jump","crit":["Arms swing up/down","Toes pointed","Lands same spot"]},
    {"evt":"BEAM","ec":"e","name":"Str Jump<br>Dismount","crit":["Arms up off beam","Str line fingers\u2192toes","Sticks safe landing"]},
    {"evt":"FLOOR","ec":"f","name":"Handstand","crit":["Feet together at vert","Str line hands\u2192toes","Str legs, arms by ears"]},
    {"evt":"FLOOR","ec":"f","name":"Cartwheel","crit":["Legs thru vertical","2nd hand turned in","Arms by ears","Legs str throughout","Opp leg lunge finish"]},
    {"evt":"FLOOR","ec":"f","name":"Backward Roll","crit":["Fingers to shoulders","Continuous movement","Feet & knees together"]},
    {"evt":"FLOOR","ec":"f","name":"Bridge<br>(5 sec hold)","crit":["Str arms in bridge","Head between arms","Feet flat & together"]},
]

def build_page(cls, skills, pn, total):
    studs = cls['students'][:8]
    while len(studs) < 8: studs.append('')
    tc = 2 + len(studs)
    h = '<div class="page">\n'
    h += '<div class="hdr"><img src="https://content.app-us1.com/vqqEDb/2026/01/30/49f475ed-3dae-48f9-a3c7-1f5d98ccc26b.png" style="height:32pt;border-radius:3pt;flex-shrink:0">'
    h += f'<div class="hm"><div class="gn">Houston Gymnastics Academy</div><div class="et">{cls["program"]} Star Chart Evaluation</div></div>'
    h += f'<div class="hr"><div class="fr"><span class="fl">Date:</span><span class="fv">03/23/2026</span></div><div class="fr"><span class="fl">Coach:</span><span class="fv">{cls["instructor"]}</span></div></div></div>\n'
    parts = cls['display'].split('|')
    h += '<div class="cbar">' + ' <span class="sep">\u00b7</span> '.join(f'<span>{p.strip()}</span>' for p in parts) + '</div>\n'
    h += '<div class="leg"><div class="li"><span class="lc"></span><span>\u25cb = criterion checkpoint</span></div>'
    h += '<div class="li"><span style="font-size:12pt;color:var(--red);line-height:1">\u2605</span><span>\u2605 = FINAL \u2014 3\u00d7 in a row</span></div></div>\n'
    h += '<table class="tbl"><colgroup><col style="width:7%"><col style="width:30%">'
    for _ in studs: h += '<col>'
    h += '</colgroup><thead><tr class="col-hdr"><th class="ch-skill">Skill</th><th class="ch-crit">Star Criteria</th>'
    for name in studs:
        bk = ' bk' if not name else ''
        h += f'<th class="ch-stu{bk}">'
        if name:
            p = name.split(', ')
            h += f'<span class="sn"><span class="first">{p[1] if len(p)>1 else ""}</span><span class="last">{p[0]}</span></span>'
        h += '</th>'
    h += '</tr></thead><tbody>'
    prev = None
    for sk in skills:
        if sk['evt'] != prev:
            h += f'<tr class="evd {sk["ec"]}"><td colspan="{tc}">{sk["evt"]}</td></tr>'
            prev = sk['evt']
        h += f'<tr class="sk {sk["ec"]}"><td class="td-sk">{sk["name"]}</td>'
        cp = [f'<span class="cnum">\u2605{i+1}</span> {c}' for i,c in enumerate(sk['crit'])]
        lns = []
        if len(cp) <= 3:
            # 3 criteria: all on one line
            lns.append(' \u00a0\u00b7\u00a0 '.join(cp))
        else:
            # 4-5 criteria: break after 2
            for i in range(0, len(cp), 2):
                lns.append(' \u00a0\u00b7\u00a0 '.join(cp[i:i+2]))
        h += f'<td class="td-c" style="text-align:center">{"<br>".join(lns)}</td>'
        for name in studs:
            fd = ' fd' if not name else ''
            h += '<td class="td-st"><div class="cell-row">'
            for ci in range(len(sk['crit'])): h += f'<span class="c{fd}" data-click="1"></span>'
            ctr = ' s-center' if len(sk['crit']) % 3 == 0 else ''
            h += f'<span class="s{fd}{ctr}" data-click="1">\u2605</span></div></td>'
        h += '</tr>\n'
    h += '</tbody></table>'
    h += f'<div class="footer"><div class="pf" style="flex:1">{cls["program"]} \u00b7 Houston Gymnastics Academy \u00b7 03/23/2026 \u00b7 Page {pn} of {total}</div></div></div>\n'
    return h

def build_roll_page(cls, pn, total):
    studs = cls['students'][:9]  # max 9
    h = '<div class="page">\n'
    h += '<div class="hdr"><img src="https://content.app-us1.com/vqqEDb/2026/01/30/49f475ed-3dae-48f9-a3c7-1f5d98ccc26b.png" style="height:32pt;border-radius:3pt;flex-shrink:0">'
    h += f'<div class="hm"><div class="gn">Houston Gymnastics Academy</div><div class="et">{cls["program"]} Roll Sheet</div></div>'
    h += f'<div class="hr"><div class="fr"><span class="fl">Date:</span><span class="fv">03/23/2026</span></div><div class="fr"><span class="fl">Coach:</span><span class="fv">{cls["instructor"]}</span></div></div></div>\n'
    parts = cls['display'].split('|')
    h += '<div class="cbar">' + ' <span class="sep">\u00b7</span> '.join(f'<span>{p.strip()}</span>' for p in parts) + '</div>\n'
    h += '<table class="roll-tbl"><thead><tr>'
    h += '<th style="width:3%">#</th><th style="width:20%">Student Name</th>'
    h += '<th style="width:8%">Age</th><th style="width:10%">Birthday</th>'
    h += '<th style="width:17%">Guardian</th><th style="width:12%">Phone</th>'
    h += '<th style="width:5%">M</th><th style="width:5%">T</th><th style="width:5%">W</th><th style="width:5%">Th</th><th style="width:5%">F</th>'
    h += '<th style="width:5%">Notes</th>'
    h += '</tr></thead><tbody>\n'
    for i, name in enumerate(studs):
        h += f'<tr><td style="text-align:center">{i+1}</td>'
        h += f'<td class="stu-name">{name}</td>'
        h += '<td></td><td></td><td></td><td></td>'  # age, bday, guardian, phone - blank for now
        h += '<td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td>'
        h += '<td></td></tr>\n'
    # Pad to 8 rows
    for i in range(len(studs), 8):
        h += f'<tr><td style="text-align:center;color:#ccc">{i+1}</td>'
        h += '<td></td><td></td><td></td><td></td><td></td>'
        h += '<td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td><td class="att-cell"></td>'
        h += '<td></td></tr>\n'
    h += '</tbody></table>'
    h += f'<div class="footer"><div class="pf" style="flex:1">{cls["program"]} Roll Sheet \u00b7 Houston Gymnastics Academy \u00b7 03/23/2026 \u00b7 Page {pn} of {total}</div></div></div>\n'
    return h

out = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>HGA Level 1 Evals - PRINT READY</title>
<style>{css}</style></head><body>
<button class="no-print" onclick="window.print()" style="position:fixed;top:12px;right:20px;z-index:999;background:#c91724;color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;font-weight:bold;cursor:pointer">\U0001f5a8 Print All</button>
'''
# === EVAL ONLY ===
for i, c in enumerate(classes):
    out += build_page(c, skills_l1, i+1, len(classes))
out += '<script>document.body.addEventListener("click",e=>{if(e.target.hasAttribute("data-click")&&!e.target.classList.contains("fd"))e.target.classList.toggle("on")});</script></body></html>'

eval_path = 'C:/Users/Jayme/JAYME PROJECTS/ICLASS SUCKS/PRINT-EVAL-GRIDS.html'
with open(eval_path, 'w', encoding='utf-8') as f:
    f.write(out)
print(f"Eval grids: {len(classes)} pages -> {eval_path}")

# === ROLL ONLY ===
out2 = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>HGA Level 1 Roll Sheets - PRINT READY</title>
<style>{css}</style></head><body>
<button class="no-print" onclick="window.print()" style="position:fixed;top:12px;right:20px;z-index:999;background:#c91724;color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;font-weight:bold;cursor:pointer">\U0001f5a8 Print Roll Sheets</button>
'''
for i, c in enumerate(classes):
    out2 += build_roll_page(c, i+1, len(classes))
out2 += '</body></html>'

roll_path = 'C:/Users/Jayme/JAYME PROJECTS/ICLASS SUCKS/PRINT-ROLL-SHEETS.html'
with open(roll_path, 'w', encoding='utf-8') as f:
    f.write(out2)
print(f"Roll sheets: {len(classes)} pages -> {roll_path}")

# === DUPLEX (Roll front, Eval back) ===
out3 = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>HGA Level 1 Roll + Eval DUPLEX - PRINT READY</title>
<style>{css}</style></head><body>
<button class="no-print" onclick="window.print()" style="position:fixed;top:12px;right:20px;z-index:999;background:#c91724;color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;font-weight:bold;cursor:pointer">\U0001f5a8 Print Duplex (Roll + Eval)</button>
'''
for i, c in enumerate(classes):
    out3 += build_roll_page(c, i+1, len(classes))
    out3 += build_page(c, skills_l1, i+1, len(classes))
out3 += '<script>document.body.addEventListener("click",e=>{if(e.target.hasAttribute("data-click")&&!e.target.classList.contains("fd"))e.target.classList.toggle("on")});</script></body></html>'

duplex_path = 'C:/Users/Jayme/JAYME PROJECTS/ICLASS SUCKS/PRINT-DUPLEX-ROLL-EVAL.html'
with open(duplex_path, 'w', encoding='utf-8') as f:
    f.write(out3)
print(f"Duplex: {len(classes)*2} pages -> {duplex_path}")

