from http.server import BaseHTTPRequestHandler
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Add parent directory to path
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

            # Try to import main
            import main

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Successfully imported main.py!')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            error_msg = f'Import failed: {str(e)}'.encode()
            self.wfile.write(error_msg)
