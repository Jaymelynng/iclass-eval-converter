"""
Star Chart PDF Generator — Backend API
Run with: python app.py
Then open http://localhost:5050 in your browser
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
import sys, os, json, io, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from pdf_generator import generate_pdf, generate_multi_pdf, generate_split_pdf

app = Flask(__name__, static_folder='public')

# ── Serve the frontend ───────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

# ── PDF generation endpoint ──────────────────────────────────────────
@app.route('/generate-pdf', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        gym_code    = data.get('gymCode', 'CCP')
        mode        = data.get('mode', 'eval')
        classes     = data.get('classes', [])
        page_events = data.get('pageEvents')  # [[ev1,ev2],[ev3,ev4]] → split pages

        # Multi-class mode (new): array of classes → one multi-page PDF
        if classes:
            if page_events and isinstance(page_events, list) and len(page_events) > 0:
                pdf_bytes = generate_split_pdf(gym_code, classes, page_events, mode)
            else:
                pdf_bytes = generate_multi_pdf(gym_code, classes, mode)
            first_date = classes[0].get('date', '').replace('/', '')
            filename = f"{gym_code}_Evals_{first_date}.pdf"

        else:
            # Legacy single-class mode (backward compat)
            class_name = data.get('className', 'Class')
            date       = data.get('date', '')
            day        = data.get('day', '')
            time       = data.get('time', '')
            students   = data.get('students', [])
            program    = data.get('program', '')
            score_map  = data.get('scoreMap', {})

            if not students:
                return jsonify({'error': 'No students found in data'}), 400
            if not program:
                return jsonify({'error': 'Program not identified'}), 400

            pdf_bytes = generate_pdf(
                gym_code=gym_code, class_name=class_name,
                date=date, day=day, time=time,
                students=students, program=program,
                score_map=score_map, mode=mode,
            )
            filename = f"{gym_code}_{program.replace(' ','_')}_{date.replace('/','')}.pdf"

        buf = io.BytesIO(pdf_bytes)
        buf.seek(0)
        # Inline (not attachment) so the JS download-attribute controls the
        # filename and triggers auto-save without the browser's "where to save"
        # dialog. The frontend appends the <a> to the DOM before clicking.
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=False, download_name=filename)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n* Star Chart PDF Server running at http://localhost:5050\n")
    app.run(debug=True, port=5050)
