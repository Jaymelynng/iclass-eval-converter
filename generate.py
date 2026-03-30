import pymupdf, json, re, sys, os

# ═══════════════════════════════════════
# PARSE ROLL SHEET
# ═══════════════════════════════════════
roll_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/Jayme/Downloads/Roll_Sheets_03-23-2026.pdf'
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
    elif 'JUNIOR' in pu: prog = 'Junior'
    elif 'GIRLS L1' in pu: prog = 'Girls Level 1'
    elif 'GIRLS L2' in pu: prog = 'Girls Level 2'
    elif 'GIRLS L3' in pu: prog = 'Girls Level 3'
    if prog:
        classes.append({'program':prog,'instructor':instructor,'schedule':schedule,'display':class_display,'students':students})

print(f"Parsed {len(classes)} star chart classes from {doc.page_count} pages")

# ═══════════════════════════════════════
# LOAD SKILL DATA
# ═══════════════════════════════════════
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'all-programs-prepped.json'), encoding='utf-8') as f:
    ALL_SKILLS = json.load(f)

# ═══════════════════════════════════════
# GYM DATA
# ═══════════════════════════════════════
GYMS = {
    'HGA': {'name':'Houston Gymnastics Academy','c1':'#c91724','c2':'#262626','c3':'#d0d0d8','logo':'https://content.app-us1.com/vqqEDb/2026/01/30/49f475ed-3dae-48f9-a3c7-1f5d98ccc26b.png'},
    'CCP': {'name':'Capital Gymnastics Cedar Park','c1':'#1f53a3','c2':'#bf0a30','c3':'#d8d8d8','logo':'https://capgymcpk.activehosted.com/content/d66m4q/2026/02/19/f11d01b7-bbdb-4de8-b5f3-8eeacc4f3017.png'},
    'CPF': {'name':'Capital Gymnastics Pflugerville','c1':'#1f53a3','c2':'#bf0a30','c3':'#d8d8d8','logo':'https://content.app-us1.com/MaaPRn/2025/09/07/fc44683b-d5a8-4547-97f5-91d46e4e647e.png'},
    'CRR': {'name':'Capital Gymnastics Round Rock','c1':'#ff1493','c2':'#c0c0c0','c3':'#3c3939','logo':'https://content.app-us1.com/511e9V/2025/09/07/54697754-fdd0-452b-9275-f1ac2421e995.png'},
    'EST': {'name':'Estrella Gymnastics','c1':'#011837','c2':'#666666','c3':'#100f0f','logo':'https://content.app-us1.com/g55L0q/2025/05/13/eff29c8b-abb0-4595-aec3-ccf32d7e1940.png'},
    'OAS': {'name':'Oasis Gymnastics','c1':'#3eb29f','c2':'#3e266b','c3':'#e7e6f0','logo':'https://content.app-us1.com/ARRBG9/2026/01/30/217676e8-f661-411a-8ea8-9a94373c5bb0.png'},
    'RBA': {'name':'Rowland Ballard Atascocita','c1':'#1a3c66','c2':'#c52928','c3':'#739ab9','logo':'https://content.app-us1.com/obb1M5/2026/01/30/d5e1a9ce-e8aa-4a21-a886-523d5a12bbd5.png'},
    'RBK': {'name':'Rowland Ballard Kingwood','c1':'#1a3c66','c2':'#c52928','c3':'#739ab9','logo':'https://content.app-us1.com/6ddeKB/2026/01/30/ebe5ff82-80c1-419b-b15d-6db55c974a7c.png'},
    'SGT': {'name':'Scottsdale Gymnastics','c1':'#c72b12','c2':'#e6e6e6','c3':'#000000','logo':'https://content.app-us1.com/OoonDm/2026/01/09/7d45241b-ea60-4305-8ed9-fcbdafc7906f.png'},
    'TIG': {'name':'Tigar Gymnastics','c1':'#f57f20','c2':'#0a3651','c3':'#7fc4e0','logo':'https://content.app-us1.com/J77wkW/2025/08/21/d817cd8d-ad31-4897-88b1-bc74d19334bb.png'},
}

gym_code = sys.argv[2] if len(sys.argv) > 2 else 'HGA'
gym = GYMS[gym_code]

# ═══════════════════════════════════════
# BUILD EVAL PAGE
# ═══════════════════════════════════════
def build_eval(cls, skills, pn, total):
    studs = cls['students'][:8]
    while len(studs) < 8: studs.append('')
    tc = 2 + len(studs)

    h = '<div class="page">\n'
    # Header
    h += f'<div class="hdr">'
    h += f'<div class="hm"><img class="logo" src="{gym["logo"]}"><div><div class="gn">{gym["name"]}</div><div class="et">{cls["program"].upper()} STAR CHART EVALUATION</div></div></div>'
    h += f'<div class="hr"><div class="fr"><span class="fl">Date:</span><span class="fv">03/23/2026</span></div>'
    h += f'<div class="fr"><span class="fl">Coach:</span><span class="fv">{cls["instructor"]}</span></div></div></div>\n'

    # Class bar
    if cls['display']:
        parts = cls['display'].split('|')
        h += '<div class="cbar">' + ' <span class="sep">\u00b7</span> '.join(f'<span>{p.strip()}</span>' for p in parts) + '</div>\n'

    # Legend
    h += '<div class="leg">'
    h += '<div class="li"><span class="lc"></span> = criterion checkpoint</div>'
    h += '<div class="li"><span class="ls">\u2605</span> = FINAL \u2014 3\u00d7 in a row</div></div>\n'

    # Table
    h += f'<table class="tbl"><colgroup><col style="width:7%"><col style="width:34%">'
    for _ in studs: h += '<col>'
    h += '</colgroup>\n'

    # Header row
    h += '<thead><tr class="chr"><th class="th-sk">SKILL</th><th class="th-cr">STAR CRITERIA</th>'
    for name in studs:
        if name:
            p = name.split(', ')
            first = p[1] if len(p) > 1 else ''
            last = p[0]
            h += f'<th class="th-st"><span class="sn-first">{first}</span><span class="sn-last">{last}</span></th>'
        else:
            h += '<th class="th-st th-blank"></th>'
    h += '</tr></thead><tbody>\n'

    # Skills
    prev = None
    for sk in skills:
        if sk['evt'] != prev:
            h += f'<tr class="evd {sk["ec"]}"><td colspan="{tc}">{sk["evt"]}</td></tr>\n'
            prev = sk['evt']

        h += f'<tr class="sk {sk["ec"]}"><td class="td-sk">{sk["name"]}</td>'

        # Criteria - all on one line for 3 criteria, break after 2 for 4-5
        cp = [f'<span class="cn">\u2605{i+1}</span> {c}' for i,c in enumerate(sk['crit'])]
        if len(cp) <= 3:
            crit_html = ' \u00a0\u00b7\u00a0 '.join(cp)
        else:
            lines = []
            for i in range(0, len(cp), 2):
                lines.append(' \u00a0\u00b7\u00a0 '.join(cp[i:i+2]))
            crit_html = '<br>'.join(lines)
        h += f'<td class="td-cr">{crit_html}</td>'

        # Student cells
        for name in studs:
            fd = ' fd' if not name else ''
            nc = len(sk['crit'])
            h += '<td class="td-st"><div class="cell">'
            for ci in range(nc):
                h += f'<span class="sq{fd}"></span>'
            ctr = ' ctr' if nc % 3 == 0 else ''
            h += f'<span class="star{fd}{ctr}">\u2605</span>'
            h += '</div></td>'

        h += '</tr>\n'

    h += '</tbody></table>\n'
    h += f'<div class="foot">{cls["program"]} \u00b7 {gym["name"]} \u00b7 03/23/2026 \u00b7 Page {pn} of {total}</div>'
    h += '</div>\n\n'
    return h

# ═══════════════════════════════════════
# CSS
# ═══════════════════════════════════════
CSS = f'''
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
@page{{size:11in 8.5in landscape;margin:0}}
@media print{{
  body{{background:#fff;padding:0;margin:0}}
  .no-print{{display:none!important}}
  .page{{box-shadow:none!important;margin:0!important;border:none!important;padding:.15in .18in}}
  *{{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}}
}}
@page{{size:landscape;margin:0}}
body{{font-family:'Arial Narrow',Arial,sans-serif;background:#333;padding:20px 0}}
.no-print{{position:fixed;top:12px;right:20px;z-index:99;background:{gym["c1"]};color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;font-weight:bold;cursor:pointer}}

.page{{
  width:11in;background:#fff;
  padding:.18in .20in;
  display:flex;flex-direction:column;gap:1.5pt;
  page-break-after:always;
}}
.page:last-child{{
  page-break-after:auto;
  margin:20px auto;
  box-shadow:0 4px 20px rgba(0,0,0,.5);
  border:1px solid #555;
  color:#222;
}}

/* HEADER */
.hdr{{display:flex;align-items:center;gap:8pt;border-bottom:2.5pt solid {gym["c1"]};padding-bottom:3pt}}
.logo{{height:30pt;flex-shrink:0;border-radius:3pt}}
.hm{{flex:1;display:flex;align-items:center;justify-content:center;gap:8pt}}
.gn{{font-size:13pt;font-weight:800;color:{gym["c2"]}}}
.et{{font-size:6.5pt;font-weight:700;color:{gym["c1"]};letter-spacing:2.5pt;margin-top:1pt}}
.hr{{display:flex;flex-direction:column;gap:2pt}}
.fr{{display:flex;gap:3pt;align-items:baseline;font-size:8pt}}
.fl{{font-weight:700;color:{gym["c2"]}}}
.fv{{flex:1;border-bottom:.5pt solid {gym["c2"]};min-width:.9in;color:{gym["c2"]}}}

/* CLASS BAR */
.cbar{{background:{gym["c2"]};color:#fff;font-size:7pt;font-weight:600;padding:1.5pt 8pt;border-radius:2pt;display:flex;justify-content:center;gap:6pt;align-items:center}}
.sep{{color:{gym["c1"]};font-weight:900}}

/* LEGEND */
.leg{{background:#f7f7f9;border:.5pt solid {gym["c3"]};border-radius:1pt;padding:2pt 8pt;display:flex;gap:12pt;font-size:6.5pt;color:{gym["c2"]}}}
.li{{display:flex;align-items:center;gap:3pt}}
.lc{{width:6pt;height:6pt;border:1pt solid {gym["c2"]};border-radius:1pt;display:inline-block}}
.ls{{font-size:9pt;color:{gym["c1"]};line-height:1}}

/* TABLE */
.tbl{{flex:1;border-collapse:collapse;table-layout:fixed;width:100%}}
.chr th{{border:.5pt solid {gym["c3"]};padding:3pt 3pt;font-size:7pt;font-weight:700;text-transform:uppercase;letter-spacing:.5pt}}
.th-sk{{background:#f0f0f3;color:{gym["c2"]};text-align:center;width:7%}}
.th-cr{{background:#f0f0f3;color:{gym["c2"]};text-align:center;font-size:8pt}}
.th-st{{background:#fff;text-align:center;vertical-align:bottom;padding:3pt 1pt!important}}
.th-blank{{background:#f8f8fa}}
.sn-first{{display:block;font-size:9pt;font-weight:800;color:#111}}
.sn-last{{display:block;font-size:6pt;font-weight:600;color:#555}}

/* EVENT DIVIDERS */
tr.evd td{{height:8pt;padding:0 6pt;font-size:5pt;font-weight:800;letter-spacing:2.5pt;color:#fff;text-transform:uppercase;border:none}}
tr.evd.v td{{background:{gym["c1"]}}}
tr.evd.b td{{background:{gym["c2"]}}}
tr.evd.e td{{background:color-mix(in srgb,{gym["c1"]} 60%,#000)}}
tr.evd.f td{{background:color-mix(in srgb,{gym["c2"]} 60%,#888)}}
tr.evd.s td{{background:#8a7a2a}}

/* SKILL ROWS */
.td-sk{{font-size:7pt;font-weight:700;color:{gym["c2"]};padding:2pt 3pt;border:.5pt solid {gym["c3"]};text-align:center;vertical-align:middle;line-height:1.25}}
.td-cr{{font-size:7.5pt;color:#333;padding:2pt 4pt;border:.5pt solid {gym["c3"]};vertical-align:middle;text-align:center;line-height:1.3}}
.cn{{color:{gym["c1"]};font-weight:800;font-size:7.5pt}}
tr.sk.v .td-sk,tr.sk.v .td-cr{{background:#fdf2f3}}
tr.sk.b .td-sk,tr.sk.b .td-cr{{background:#f4f4f6}}
tr.sk.e .td-sk,tr.sk.e .td-cr{{background:#fbe8ea}}
tr.sk.f .td-sk,tr.sk.f .td-cr{{background:#ebebee}}
tr.sk.s .td-sk,tr.sk.s .td-cr{{background:#fdfbe8}}

/* STUDENT CELLS */
.td-st{{border:.5pt solid {gym["c3"]};text-align:center;vertical-align:middle;padding:1pt 0}}
tr.sk:nth-child(odd) .td-st{{background:#fafafa}}
tr.sk:nth-child(even) .td-st{{background:#fff}}

.cell{{display:grid;grid-template-columns:repeat(3,auto);gap:2pt;justify-content:center;justify-items:center;align-items:center;padding:1.5pt}}
.sq{{width:8pt;height:8pt;border:1.2pt solid #999;border-radius:1pt;display:block;cursor:pointer}}
.sq:hover{{border-color:{gym["c1"]};background:#fde8ea}}
.sq.on{{background:{gym["c1"]};border-color:{gym["c1"]}}}
.sq.fd{{border-color:#ddd;cursor:default;background:#f8f8f8}}
.star{{font-size:12pt;color:#d0d0d8;cursor:pointer;line-height:1;display:block;font-weight:900}}
.star.ctr{{grid-column:1/4;justify-self:center}}
.star:hover{{color:#DAA520}}
.star.on{{color:#DAA520;text-shadow:0 1pt 2pt rgba(218,165,32,.4)}}
.star.fd{{color:#e8e8e8;cursor:default}}

/* FOOTER */
.foot{{font-size:5pt;color:#aaa;text-align:right;padding-top:1.5pt;border-top:1pt solid {gym["c1"]};margin-top:auto}}
'''

# ═══════════════════════════════════════
# GENERATE OUTPUT
# ═══════════════════════════════════════
html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{gym["name"]} \u2014 Star Chart Evaluations</title>
<style>{CSS}</style></head><body>
<button class="no-print" onclick="window.print()">\U0001f5a8 Print All ({len(classes)} classes)</button>
'''

for i, cls in enumerate(classes):
    skills = ALL_SKILLS.get(cls['program'], [])
    if skills:
        html += build_eval(cls, skills, i+1, len(classes))
    else:
        print(f"  WARNING: No skill data for {cls['program']}")

html += '''<script>
document.body.addEventListener('click', e => {
  const t = e.target;
  if (t.classList.contains('sq') && !t.classList.contains('fd')) t.classList.toggle('on');
  if (t.classList.contains('star') && !t.classList.contains('fd')) t.classList.toggle('on');
});
</script></body></html>'''

out_path = os.path.join(script_dir, f'EVAL-GRIDS-{gym_code}.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Generated: {out_path}")
print(f"  {len(classes)} classes, {gym['name']}")
print(f"  Open the file and hit Print")
