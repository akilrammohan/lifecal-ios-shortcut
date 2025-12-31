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
    parse_date,
    parse_style_config,
)
from io import BytesIO
from PIL import Image


def get_param(params: dict, key: str) -> str:
    """Get a single query parameter value."""
    values = params.get(key, [None])
    return values[0] if values else None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)

        # Get date parameter
        date_str = get_param(params, 'date')
        target_date = parse_date(date_str)

        # Parse style config from query params
        config = parse_style_config(
            bg=get_param(params, 'bg'),
            past=get_param(params, 'past'),
            today=get_param(params, 'today'),
            future=get_param(params, 'future'),
            text=get_param(params, 'text'),
            shape=get_param(params, 'shape'),
            progress=get_param(params, 'progress'),
            font=get_param(params, 'font'),
        )

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
                "customization": {
                    "bg": "Background color (6-char hex, e.g., 1a1a1a)",
                    "past": "Past days fill color (6-char hex)",
                    "today": "Today highlight color (6-char hex)",
                    "future": "Future days outline color (6-char hex)",
                    "text": "Text color (6-char hex)",
                    "shape": "Day shape: square, circle, or rounded",
                    "progress": "Show year progress: true or 1",
                    "font": "Font style: sans, serif, or mono"
                },
                "usage": "GET /{layout}?date=YYYY-MM-DD&bg=000000&shape=circle",
                "examples": [
                    "/standard?date=2025-12-31",
                    "/quarters?shape=circle&progress=true",
                    "/months?bg=0a0a0a&today=ff5555&font=mono"
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            return

        # Check if path matches a layout
        if path in layout_map:
            try:
                # Generate image with config
                layout_func = layout_map[path]
                img = layout_func(target_date, config)

                # Convert to PNG bytes
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG', optimize=True)
                img_bytes.seek(0)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=86400')  # 24 hours
                self.send_header('Content-Length', str(len(img_bytes.getvalue())))
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
