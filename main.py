from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
import calendar
import math

app = FastAPI()


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_days_in_year(year: int) -> int:
    """Get total days in a year (365 or 366)."""
    return 366 if is_leap_year(year) else 365


def generate_calendar_image(target_date: datetime) -> Image.Image:
    """
    Generate a yearly calendar wallpaper image.

    Design specs:
    - Dark gray/almost black background
    - White filled squares for days that have occurred
    - Empty squares for future days
    - Year text in bottom left corner (small)
    - Grid layout: 52-53 weeks × 7 days (handles leap years)
    - Grid-based design: entire canvas divided into 16px grid units
    """
    # iPhone 15 / 15 Pro dimensions
    WIDTH = 1179
    HEIGHT = 2556

    # Grid system: all measurements in multiples of 16px
    GRID_UNIT = 16

    # Margins (in grid units)
    MARGIN_LEFT = 4    # 64px
    MARGIN_RIGHT = 4   # 64px
    MARGIN_BOTTOM = 10 # 160px

    # Colors (matching tweet aesthetic)
    BG_COLOR = '#1a1a1a'  # Dark gray/almost black
    PAST_DAY_COLOR = '#ffffff'  # White filled squares
    TODAY_COLOR = '#F56B3F'  # Anthropic orange for current day
    FUTURE_DAY_COLOR = '#404040'  # Lighter gray for visible outline
    TEXT_COLOR = '#ffffff'

    # Calculate day of year and total days
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    # Calculate what day of the week January 1 falls on
    # We want Sunday = 0, Monday = 1, ..., Saturday = 6
    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7  # Convert Python's Mon=0 to our Sun=0

    # Calculate total cells needed (empty days before Jan 1 + all days in year)
    total_cells = jan_1_weekday + total_days

    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Calendar grid configuration (in grid units)
    SQUARE_UNITS = 1  # Each square is 1 grid unit (16px)
    GAP_UNITS = 1     # Each gap is 1 grid unit (16px)

    cols = 7  # Days per week
    # Calculate rows needed based on actual calendar layout
    rows = math.ceil(total_cells / cols)

    # Convert to pixels
    square_size = SQUARE_UNITS * GRID_UNIT  # 16px
    gap_size = GAP_UNITS * GRID_UNIT        # 16px

    # Calculate total grid dimensions in pixels
    # Grid: square + gap + square + gap + ... + square
    # Width: 7 squares + 6 gaps
    grid_width = (cols * square_size) + ((cols - 1) * gap_size)  # 7*16 + 6*16 = 208px
    # Height: Variable based on rows needed
    grid_height = (rows * square_size) + ((rows - 1) * gap_size)

    # Position grid
    # Horizontal: centered between left and right margins
    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT  # 1179 - 128 = 1051px
    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - grid_width) // 2  # 64 + (1051-208)/2 ≈ 485px

    # Vertical: bottom-aligned with bottom margin, top calculated accordingly
    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)  # 2556 - 160 = 2396px
    start_y = grid_bottom_y - grid_height

    # Load font for year text
    try:
        year_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 21)
    except:
        year_font = ImageFont.load_default()

    # Draw grid of squares
    cell_counter = 0  # Total cells (including empty ones before Jan 1)
    day_counter = 0   # Actual day number (0 = not started, 1-365/366 = actual days)

    for row in range(rows):
        for col in range(cols):
            # Stop if we've drawn all cells
            if cell_counter >= total_cells:
                break

            # Calculate position using grid system
            x = start_x + col * (square_size + gap_size)
            y = start_y + row * (square_size + gap_size)

            # Check if this cell is before Jan 1 (empty cell)
            if cell_counter < jan_1_weekday:
                # Empty cell before the year starts - don't draw anything
                pass
            else:
                # This is an actual day of the year
                day_counter += 1

                # Determine if this day has occurred, is today, or is in the future
                if day_counter < day_of_year:
                    # Past day - filled white square
                    draw.rectangle(
                        [x, y, x + square_size, y + square_size],
                        fill=PAST_DAY_COLOR
                    )
                elif day_counter == day_of_year:
                    # Today - filled orange square (Anthropic orange)
                    draw.rectangle(
                        [x, y, x + square_size, y + square_size],
                        fill=TODAY_COLOR
                    )
                else:
                    # Future day - empty square with visible outline
                    draw.rectangle(
                        [x, y, x + square_size, y + square_size],
                        outline=FUTURE_DAY_COLOR,
                        width=2
                    )

            cell_counter += 1

    # Add year text in bottom left (aligned to grid)
    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT  # 64px from left edge
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)  # 2 grid units below grid bottom
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "message": "Yearly Calendar Wallpaper API",
        "usage": "GET /calendar?date=YYYY-MM-DD (optional, defaults to today)",
        "example": "/calendar?date=2025-12-30"
    }


@app.get("/calendar")
def get_calendar(date: str = None):
    """
    Generate a yearly calendar wallpaper image.

    Args:
        date: Optional date in YYYY-MM-DD format. Defaults to today.

    Returns:
        PNG image of the yearly calendar with current day highlighted.
    """
    # Parse date or use today
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
    else:
        target_date = datetime.now()

    # Generate image
    img = generate_calendar_image(target_date)

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG', optimize=True)
    img_bytes.seek(0)

    # Return as streaming response
    return StreamingResponse(
        img_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": f"inline; filename=calendar_{target_date.strftime('%Y-%m-%d')}.png"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
