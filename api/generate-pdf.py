"""
Vercel serverless function for PDF generation.
POST /generate-pdf with JSON body → returns PDF bytes.
"""
from http.server import BaseHTTPRequestHandler
import json, io, traceback
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_generator import generate_pdf, generate_multi_pdf, generate_split_pdf


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            if not data:
                self._error(400, 'No data received')
                return

            gym_code    = data.get('gymCode', 'CCP')
            mode        = data.get('mode', 'eval')
            classes     = data.get('classes', [])
            page_events = data.get('pageEvents')  # e.g. [['VAULT','BARS'],['BEAM','FLOOR']]

            if classes:
                # Multi-class: one page per class
                # If pageEvents is provided, use the split renderer so each class
                # gets N pages (one per event grouping in pageEvents).
                if page_events and isinstance(page_events, list) and len(page_events) > 0:
                    pdf_bytes = generate_split_pdf(gym_code, classes, page_events, mode)
                else:
                    pdf_bytes = generate_multi_pdf(gym_code, classes, mode)
                first_date = classes[0].get('date', '').replace('/', '')
                filename = f"{gym_code}_Evals_{first_date}.pdf"
            else:
                # Legacy single-class
                class_name = data.get('className', 'Class')
                date       = data.get('date', '')
                day        = data.get('day', '')
                time       = data.get('time', '')
                students   = data.get('students', [])
                program    = data.get('program', '')
                score_map  = data.get('scoreMap', {})

                if not students:
                    self._error(400, 'No students found')
                    return
                if not program:
                    self._error(400, 'Program not identified')
                    return

                pdf_bytes = generate_pdf(
                    gym_code=gym_code, class_name=class_name,
                    date=date, day=day, time=time,
                    students=students, program=program,
                    score_map=score_map, mode=mode,
                )
                filename = f"{gym_code}_{program.replace(' ','_')}_{date.replace('/','')}.pdf"

            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            # Inline so the JS download-attribute controls save (avoids Edge save dialog)
            self.send_header('Content-Disposition', f'inline; filename="{filename}"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.end_headers()
            self.wfile.write(pdf_bytes)

        except Exception as e:
            traceback.print_exc()
            self._error(500, str(e))

    def _error(self, code, msg):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': msg}).encode())
