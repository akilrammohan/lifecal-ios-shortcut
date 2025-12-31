from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import all our layout generators
from main import (
    generate_standard_layout,
    generate_split_layout,
    generate_quarters_layout,
    generate_thirds_layout,
    generate_wide_layout,
    generate_months_layout,
    parse_date
)
from io import BytesIO

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)

        # Get date parameter
        date_str = params.get('date', [None])[0]
        target_date = parse_date(date_str)

        # Route to appropriate layout
        layout_map = {
            '/standard': generate_standard_layout,
            '/split': generate_split_layout,
            '/quarters': generate_quarters_layout,
            '/thirds': generate_thirds_layout,
            '/wide': generate_wide_layout,
            '/months': generate_months_layout,
        }

        # Handle root endpoint
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Yearly Calendar Wallpaper API",
                "layouts": {
                    "standard": "Single column (original layout)",
                    "split": "Two columns (year split in half)",
                    "quarters": "Four quarters (Q1-Q4 in 2x2 grid)",
                    "thirds": "Three columns (year divided into thirds)",
                    "wide": "Wide grid (14 columns - two weeks side-by-side)",
                    "months": "12 months (3x4 traditional calendar grid)"
                },
                "usage": "GET /{layout}?date=YYYY-MM-DD (date parameter optional, defaults to today)",
                "examples": [
                    "/standard?date=2025-12-31",
                    "/quarters",
                    "/months?date=2025-06-15"
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            return

        # Check if path matches a layout
        if path in layout_map:
            try:
                # Generate image
                layout_func = layout_map[path]
                img = layout_func(target_date)

                # Convert to PNG bytes
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG', optimize=True)
                img_bytes.seek(0)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=3600')
                layout_name = path[1:]  # Remove leading /
                self.send_header('Content-Disposition',
                               f'inline; filename={layout_name}_{target_date.strftime("%Y-%m-%d")}.png')
                self.end_headers()
                self.wfile.write(img_bytes.getvalue())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error generating image: {str(e)}'.encode())
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found. Try /, /standard, /split, /quarters, /thirds, /wide, or /months')
