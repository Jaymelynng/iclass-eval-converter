"""
Star Chart PDF Generator — Backend API
Run with: python app.py
Then open http://localhost:5050 in your browser
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
import json, io, traceback
from pdf_generator import generate_pdf

app = Flask(__name__, static_folder='.')

# ── Serve the frontend ───────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ── PDF generation endpoint ──────────────────────────────────────────
@app.route('/generate-pdf', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Required fields
        gym_code    = data.get('gymCode', 'CCP')
        class_name  = data.get('className', 'Class')
        date        = data.get('date', '')
        day         = data.get('day', '')
        time        = data.get('time', '')
        students    = data.get('students', [])   # list of name strings
        program     = data.get('program', '')    # "Preschool", "Junior", etc.
        score_map   = data.get('scoreMap', {})   # see pdf_generator.py for format
        mode        = data.get('mode', 'eval')   # "eval" or "blank"

        # Validate
        if not students:
            return jsonify({'error': 'No students found in data'}), 400
        if not program:
            return jsonify({'error': 'Program not identified'}), 400

        # Generate PDF bytes
        pdf_bytes = generate_pdf(
            gym_code   = gym_code,
            class_name = class_name,
            date       = date,
            day        = day,
            time       = time,
            students   = students,
            program    = program,
            score_map  = score_map,
            mode       = mode,
        )

        # Return PDF as download
        buf = io.BytesIO(pdf_bytes)
        buf.seek(0)
        filename = f"{gym_code}_{program.replace(' ','_')}_{date.replace('/','')}.pdf"
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n* Star Chart PDF Server running at http://localhost:5050\n")
    app.run(debug=True, port=5050)
