from http.server import BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
from urllib.parse import parse_qs, urlparse
import calendar
import math


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_days_in_year(year: int) -> int:
    """Get total days in a year (365 or 366)."""
    return 366 if is_leap_year(year) else 365


def generate_calendar_image(target_date: datetime) -> bytes:
    """Generate yearly calendar wallpaper image."""
    # iPhone 15 / 15 Pro dimensions
    WIDTH = 1179
    HEIGHT = 2556

    # Grid system
    GRID_UNIT = 16

    # Margins
    MARGIN_LEFT = 4
    MARGIN_RIGHT = 4
    MARGIN_BOTTOM = 10

    # Colors
    BG_COLOR = '#1a1a1a'
    PAST_DAY_COLOR = '#ffffff'
    TODAY_COLOR = '#F56B3F'
    FUTURE_DAY_COLOR = '#404040'
    TEXT_COLOR = '#ffffff'

    # Calculate day of year and total days
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    # Calculate Jan 1 weekday offset
    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7

    # Calculate total cells
    total_cells = jan_1_weekday + total_days

    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Grid configuration
    SQUARE_UNITS = 1
    GAP_UNITS = 1

    cols = 7
    rows = math.ceil(total_cells / cols)

    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    grid_width = (cols * square_size) + ((cols - 1) * gap_size)
    grid_height = (rows * square_size) + ((rows - 1) * gap_size)

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - grid_width) // 2

    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    start_y = grid_bottom_y - grid_height

    # Load font
    try:
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 21)
    except:
        year_font = ImageFont.load_default()

    # Draw grid
    cell_counter = 0
    day_counter = 0

    for row in range(rows):
        for col in range(cols):
            if cell_counter >= total_cells:
                break

            x = start_x + col * (square_size + gap_size)
            y = start_y + row * (square_size + gap_size)

            if cell_counter < jan_1_weekday:
                pass
            else:
                day_counter += 1

                if day_counter < day_of_year:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                elif day_counter == day_of_year:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                else:
                    draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

            cell_counter += 1

    # Add year text
    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    # Convert to PNG bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG', optimize=True)
    img_bytes.seek(0)

    return img_bytes.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        # Get date parameter or use today
        date_str = params.get('date', [None])[0]

        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid date format. Use YYYY-MM-DD')
                return
        else:
            target_date = datetime.now()

        # Generate image
        try:
            img_bytes = generate_calendar_image(target_date)

            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.send_header('Content-Disposition', f'inline; filename=calendar_{target_date.strftime("%Y-%m-%d")}.png')
            self.end_headers()
            self.wfile.write(img_bytes)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
