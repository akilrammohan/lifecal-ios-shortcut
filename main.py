from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from dataclasses import dataclass
import calendar
import math
import os
import re


@dataclass
class StyleConfig:
    """Configuration for calendar styling."""
    bg_color: str = '#1a1a1a'
    past_color: str = '#ffffff'
    today_color: str = '#F56B3F'
    future_color: str = '#404040'
    text_color: str = '#ffffff'
    shape: str = 'square'  # square, circle, rounded
    show_progress: bool = False
    font: str = 'sans'  # sans, serif, mono


def validate_hex_color(color: str, default: str) -> str:
    """Validate a hex color string (without #) and return with # prefix."""
    if color and re.match(r'^[0-9a-fA-F]{6}$', color):
        return f'#{color}'
    return default


def parse_style_config(
    bg: str = None,
    past: str = None,
    today: str = None,
    future: str = None,
    text: str = None,
    shape: str = None,
    progress: str = None,
    font: str = None,
) -> StyleConfig:
    """Parse URL parameters into a StyleConfig."""
    config = StyleConfig()

    # Validate and apply colors
    if bg:
        config.bg_color = validate_hex_color(bg, config.bg_color)
    if past:
        config.past_color = validate_hex_color(past, config.past_color)
    if today:
        config.today_color = validate_hex_color(today, config.today_color)
    if future:
        config.future_color = validate_hex_color(future, config.future_color)
    if text:
        config.text_color = validate_hex_color(text, config.text_color)

    # Validate shape
    if shape and shape.lower() in ('square', 'circle', 'rounded'):
        config.shape = shape.lower()

    # Parse progress flag
    if progress and progress.lower() in ('true', '1', 'yes'):
        config.show_progress = True

    # Validate font
    if font and font.lower() in ('sans', 'serif', 'mono'):
        config.font = font.lower()

    return config


def draw_day_shape(draw: ImageDraw.Draw, x: int, y: int, size: int,
                   color: str, shape: str, fill: bool = True) -> None:
    """Draw a day indicator shape (square, circle, or rounded)."""
    if shape == 'circle':
        if fill:
            draw.ellipse([x, y, x + size, y + size], fill=color)
        else:
            draw.ellipse([x, y, x + size, y + size], outline=color, width=2)
    elif shape == 'rounded':
        radius = size // 4  # 25% corner radius
        if fill:
            draw.rounded_rectangle([x, y, x + size, y + size], radius=radius, fill=color)
        else:
            draw.rounded_rectangle([x, y, x + size, y + size], radius=radius, outline=color, width=2)
    else:  # square (default)
        if fill:
            draw.rectangle([x, y, x + size, y + size], fill=color)
        else:
            draw.rectangle([x, y, x + size, y + size], outline=color, width=2)


# iPhone 15 / 15 Pro dimensions
WIDTH = 1179
HEIGHT = 2556

# Grid system: all measurements in multiples of 16px
GRID_UNIT = 16

# Margins (in grid units)
MARGIN_LEFT = 4     # 64px
MARGIN_RIGHT = 4    # 64px
MARGIN_TOP = 30     # 480px (space for iOS time/date, adjusted for parallax-sized image)
MARGIN_BOTTOM = 8   # 128px

# Colors
BG_COLOR = '#1a1a1a'
PAST_DAY_COLOR = '#ffffff'
TODAY_COLOR = '#F56B3F'
FUTURE_DAY_COLOR = '#404040'
TEXT_COLOR = '#ffffff'


def get_font(size: int, font_style: str = 'sans') -> ImageFont.FreeTypeFont:
    """
    Try to load a TrueType font from bundled font or common system locations.

    Args:
        size: Font size in pixels
        font_style: One of 'sans', 'serif', or 'mono'
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Font file mappings for each style
    font_files = {
        'sans': ['DejaVuSans.ttf', 'DejaVuSans.ttf'],
        'serif': ['DejaVuSerif.ttf', 'DejaVuSerif.ttf'],
        'mono': ['DejaVuSansMono.ttf', 'DejaVuSansMono.ttf'],
    }

    # Get the font file for the requested style (default to sans)
    font_file = font_files.get(font_style, font_files['sans'])[0]

    font_paths = [
        # Bundled font (ships with the project)
        os.path.join(script_dir, font_file),
        # Linux (Vercel, Ubuntu, Debian)
        f"/usr/share/fonts/truetype/dejavu/{font_file}",
        f"/usr/share/fonts/dejavu/{font_file}",
    ]

    # Add fallbacks for each style
    if font_style == 'sans':
        font_paths.extend([
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ])
    elif font_style == 'serif':
        font_paths.extend([
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/System/Library/Fonts/Times.ttc",
            "/Library/Fonts/Times New Roman.ttf",
            "C:\\Windows\\Fonts\\times.ttf",
        ])
    elif font_style == 'mono':
        font_paths.extend([
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/System/Library/Fonts/Courier.ttc",
            "/Library/Fonts/Courier New.ttf",
            "C:\\Windows\\Fonts\\cour.ttf",
        ])

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue

    # If no font found for the style, try sans as ultimate fallback
    if font_style != 'sans':
        return get_font(size, 'sans')

    # If no font found, raise an error with helpful message
    raise RuntimeError(
        f"No TrueType font found. Tried: {', '.join(font_paths)}"
    )


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_days_in_year(year: int) -> int:
    """Get total days in a year (365 or 366)."""
    return 366 if is_leap_year(year) else 365


def parse_birthday(birthday_str: str) -> datetime:
    """
    Parse birthday string in YYYY-MM-DD format.

    Args:
        birthday_str: Date string in YYYY-MM-DD format

    Returns:
        datetime object

    Raises:
        ValueError: If format is invalid or date is invalid
    """
    if not birthday_str:
        raise ValueError("Birthday parameter is required")

    # Try to parse YYYY-MM-DD format
    try:
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid birthday format. Expected YYYY-MM-DD, got: {birthday_str}")

    # Check if birthday is in the future
    if birthday > datetime.now():
        raise ValueError(f"Birthday cannot be in the future: {birthday_str}")

    return birthday


def get_week_start(date: datetime) -> datetime:
    """
    Get the Sunday that starts the week containing the given date.

    Args:
        date: Any date

    Returns:
        datetime object for the Sunday of that week (at midnight)
    """
    # weekday(): Monday=0, Sunday=6
    # We want Sunday=0, so we add 1 and modulo 7
    days_since_sunday = (date.weekday() + 1) % 7
    week_start = date - timedelta(days=days_since_sunday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)


def calculate_life_weeks(birthday: datetime, current_date: datetime) -> tuple:
    """
    Calculate week-of-life information for life calendar.

    Args:
        birthday: Date of birth
        current_date: Current date to calculate from

    Returns:
        Tuple of (total_weeks, current_week_index, is_current_week_complete, age_years)
        - total_weeks: Total weeks lived (complete + current)
        - current_week_index: 0-based index of current week
        - is_current_week_complete: True if current week is fully past
        - age_years: Age in years (fractional)
    """
    # Get the week start for birthday and current date
    birth_week_start = get_week_start(birthday)
    current_week_start = get_week_start(current_date)

    # Calculate total complete weeks between birth week start and current week start
    days_diff = (current_week_start - birth_week_start).days
    weeks_lived = days_diff // 7

    # Check if current week is complete
    # Current week ends on Saturday (6 days after Sunday start)
    current_week_end = current_week_start + timedelta(days=6)
    is_current_week_complete = current_date > current_week_end

    # If current week is not complete, we're still in it
    # If complete, we've moved to the next week
    current_week_index = weeks_lived

    # Calculate age in years (for display)
    age_years = (current_date - birthday).days / 365.25

    return weeks_lived, current_week_index, is_current_week_complete, age_years


def generate_error_image(error_message: str, config: StyleConfig = None) -> Image.Image:
    """
    Generate an error image with a message.

    Args:
        error_message: Error message to display
        config: Style configuration (optional)

    Returns:
        PIL Image object
    """
    if config is None:
        config = StyleConfig()

    # Create image with background
    img = Image.new('RGB', (WIDTH, HEIGHT), config.bg_color)
    draw = ImageDraw.Draw(img)

    # Load font for error message
    try:
        font = get_font(32, config.font)
        title_font = get_font(48, config.font)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    # Draw error title
    title = "Error"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    title_y = HEIGHT // 2 - 100
    draw.text((title_x, title_y), title, fill=config.today_color, font=title_font)

    # Draw error message (word wrap)
    max_width = WIDTH - 128  # Leave margins
    words = error_message.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    # Draw wrapped text
    y = title_y + 80
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (WIDTH - line_width) // 2
        draw.text((x, y), line, fill=config.text_color, font=font)
        y += 40

    return img


def generate_life_layout(birthday: datetime, current_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate life calendar wallpaper (80 years x 52 weeks grid).
    Each cell represents one week of life.

    Args:
        birthday: Date of birth
        current_date: Current date (for calculating progress)
        config: Style configuration

    Returns:
        PIL Image object
    """
    if config is None:
        config = StyleConfig()

    # Calculate life weeks
    weeks_lived, current_week_index, is_current_week_complete, age_years = calculate_life_weeks(birthday, current_date)

    # Grid configuration
    WEEKS_PER_YEAR = 52
    BASE_YEARS = 80

    # Calculate how many years we need to display
    # If person is older than 80, extend the grid
    years_to_display = max(BASE_YEARS, math.ceil(age_years) + 1)

    # Calculate total weeks to display
    total_weeks = years_to_display * WEEKS_PER_YEAR

    # Grid dimensions: 52 columns (weeks) x years_to_display rows (years)
    cols = WEEKS_PER_YEAR
    rows = years_to_display

    # Calculate cell and gap sizes to fit the screen
    # Available space after margins
    margin_left_px = MARGIN_LEFT * GRID_UNIT
    margin_right_px = MARGIN_RIGHT * GRID_UNIT
    margin_top_px = MARGIN_TOP * GRID_UNIT
    margin_bottom_px = MARGIN_BOTTOM * GRID_UNIT

    available_width = WIDTH - margin_left_px - margin_right_px
    available_height = HEIGHT - margin_top_px - margin_bottom_px

    # Reserve space for progress text if enabled
    progress_text_height = 60 if config.show_progress else 0
    available_height -= progress_text_height

    # Calculate cell size and gap
    # We want: cols * cell_size + (cols - 1) * gap = available_width
    # Let's use gap = cell_size * 0.8 for good spacing
    # cols * cell + (cols - 1) * cell * 0.8 = available_width
    # cell * (cols + (cols - 1) * 0.8) = available_width
    cell_size_width = available_width / (cols + (cols - 1) * 0.8)
    cell_size_height = available_height / (rows + (rows - 1) * 0.8)

    # Use the smaller dimension to ensure it fits
    cell_size = min(cell_size_width, cell_size_height)
    cell_size = int(cell_size)
    gap = int(cell_size * 0.8)

    # Ensure minimum size
    if cell_size < 4:
        cell_size = 4
        gap = 3

    # Calculate actual grid dimensions
    grid_width = cols * cell_size + (cols - 1) * gap
    grid_height = rows * cell_size + (rows - 1) * gap

    # Center the grid
    start_x = margin_left_px + (available_width - grid_width) // 2
    start_y = margin_top_px + (available_height - grid_height) // 2

    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), config.bg_color)
    draw = ImageDraw.Draw(img)

    # Draw the grid
    for week_index in range(total_weeks):
        col = week_index % cols
        row = week_index // cols

        x = start_x + col * (cell_size + gap)
        y = start_y + row * (cell_size + gap)

        # Determine the state of this week
        if week_index < current_week_index:
            # Past week - fill with past color
            draw_day_shape(draw, x, y, cell_size, config.past_color, config.shape, fill=True)
        elif week_index == current_week_index:
            # Current week
            if is_current_week_complete:
                # Week is complete - fill with past color
                draw_day_shape(draw, x, y, cell_size, config.past_color, config.shape, fill=True)
            else:
                # Week in progress - outline with today color
                draw_day_shape(draw, x, y, cell_size, config.today_color, config.shape, fill=False)
        else:
            # Future week - outline with future color
            draw_day_shape(draw, x, y, cell_size, config.future_color, config.shape, fill=False)

    # Draw progress text if enabled
    if config.show_progress:
        # Calculate percentage to 80 years
        percent_to_80 = (age_years / 80.0) * 100
        progress_text = f"{percent_to_80:.1f}% to 80"

        try:
            font = get_font(40, config.font)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), progress_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (WIDTH - text_width) // 2
        text_y = start_y + grid_height + 20

        draw.text((text_x, text_y), progress_text, fill=config.text_color, font=font)

    return img


def generate_standard_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate standard single-column yearly calendar wallpaper.
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 7
    rows = math.ceil(total_cells / cols)

    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    grid_width = (cols * square_size) + ((cols - 1) * gap_size)
    grid_height = (rows * square_size) + ((rows - 1) * gap_size)

    year_font = get_font(42, config.font)
    year_text_height = 50  # Approximate height for 42px font
    year_padding = GRID_UNIT * 2  # 32px padding below grid

    # Calculate available space and center grid vertically
    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = grid_height + year_padding + year_text_height

    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - grid_width) // 2
    start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

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
                    draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                elif day_counter == day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                else:
                    draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

            cell_counter += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2  # Center horizontally
    year_y = start_y + grid_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def generate_split_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate two-column layout (year split into two halves).
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 7
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    cells_per_half = total_cells // 2
    rows_per_half = math.ceil(cells_per_half / cols)

    grid_width = (cols * square_size) + ((cols - 1) * gap_size)
    grid_height = (rows_per_half * square_size) + ((rows_per_half - 1) * gap_size)

    year_font = get_font(42, config.font)
    year_text_height = 50
    year_padding = GRID_UNIT * 2

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = grid_height + year_padding + year_text_height

    horizontal_spacing = 4 * GRID_UNIT
    total_width = 2 * grid_width + horizontal_spacing
    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

    cell_counter = 0
    day_counter = 0

    # Draw first half (left column)
    for row in range(rows_per_half):
        for col in range(cols):
            if cell_counter >= cells_per_half:
                break

            x = start_x + col * (square_size + gap_size)
            y = start_y + row * (square_size + gap_size)

            if cell_counter < jan_1_weekday:
                pass
            else:
                day_counter += 1
                if day_counter < day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                elif day_counter == day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                else:
                    draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

            cell_counter += 1

    # Draw second half (right column)
    start_x_right = start_x + grid_width + horizontal_spacing

    for row in range(rows_per_half):
        for col in range(cols):
            if cell_counter >= total_cells:
                break

            x = start_x_right + col * (square_size + gap_size)
            y = start_y + row * (square_size + gap_size)

            if cell_counter < jan_1_weekday:
                pass
            else:
                day_counter += 1
                if day_counter < day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                elif day_counter == day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                else:
                    draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

            cell_counter += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2
    year_y = start_y + grid_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def generate_quarters_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate four quarters layout (Q1-Q4 in 2x2 grid).
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 7
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    # Define actual calendar quarters: Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec
    quarter_months = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]

    quarter_info = []
    for q_months in quarter_months:
        start_date = datetime(year, q_months[0], 1)
        last_month = q_months[-1]
        days_in_last_month = calendar.monthrange(year, last_month)[1]
        end_date = datetime(year, last_month, days_in_last_month)

        days_in_quarter = (end_date - start_date).days + 1
        start_weekday = (start_date.weekday() + 1) % 7

        cells_needed = start_weekday + days_in_quarter
        rows_needed = math.ceil(cells_needed / cols)

        quarter_info.append({
            'start_date': start_date,
            'end_date': end_date,
            'days': days_in_quarter,
            'start_weekday': start_weekday,
            'cells': cells_needed,
            'rows': rows_needed
        })

    max_rows = max(q['rows'] for q in quarter_info)

    quarter_width = (cols * square_size) + ((cols - 1) * gap_size)
    quarter_height = (max_rows * square_size) + ((max_rows - 1) * gap_size)

    h_spacing = 4 * GRID_UNIT
    v_spacing = 4 * GRID_UNIT

    quarter_font = get_font(32, config.font)
    year_font = get_font(42, config.font)

    # Estimate label width for "Q1" text at 32px (roughly 50px wide)
    label_width = 50
    label_spacing = GRID_UNIT  # 16px spacing between label and grid

    # For labels between grids (Q2, Q4), they should be centered with equal spacing on both sides
    # Spacing between grids = padding + label_width + padding
    side_padding = 2 * GRID_UNIT  # 32px on each side of centered label
    h_spacing_with_label = (2 * side_padding) + label_width  # Total spacing between grids

    # Calculate total width: 2 grids + labels on left of each + spacing between
    # Layout: [label][grid] [spacing with room for label] [label][grid]
    total_width = 2 * quarter_width + h_spacing_with_label + 2 * (label_width + label_spacing)
    total_height = 2 * quarter_height + v_spacing

    year_text_height = 50
    year_padding = GRID_UNIT * 2

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = total_height + year_padding + year_text_height

    # Center the entire construct (labels + grids + spacing)
    construct_start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    grid_start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

    # First grid starts after its label
    first_grid_x = construct_start_x + label_width + label_spacing
    # Second grid starts after first grid + spacing
    second_grid_x = first_grid_x + quarter_width + h_spacing_with_label

    # Positions for each quarter grid
    quarter_grid_positions = [
        (first_grid_x, grid_start_y),
        (second_grid_x, grid_start_y),
        (first_grid_x, grid_start_y + quarter_height + v_spacing),
        (second_grid_x, grid_start_y + quarter_height + v_spacing),
    ]

    for q_idx, (q_x, q_y) in enumerate(quarter_grid_positions):
        q_info = quarter_info[q_idx]

        # Draw label to the left of the grid, aligned with top edge
        quarter_label = f"Q{q_idx + 1}"
        label_x = q_x - label_spacing - label_width
        label_y = q_y  # Align top of text with top of grid
        draw.text((label_x, label_y), quarter_label, fill=config.text_color, font=quarter_font)

        cell_counter = 0
        day_in_quarter = 0

        for row in range(max_rows):
            for col in range(cols):
                if cell_counter >= q_info['cells']:
                    break

                x = q_x + col * (square_size + gap_size)
                y = q_y + row * (square_size + gap_size)

                if cell_counter < q_info['start_weekday']:
                    pass
                else:
                    day_in_quarter += 1

                    actual_date = q_info['start_date'] + timedelta(days=day_in_quarter - 1)
                    actual_day_of_year = actual_date.timetuple().tm_yday

                    if actual_day_of_year < day_of_year:
                        draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                    elif actual_day_of_year == day_of_year:
                        draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                    else:
                        draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

                cell_counter += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2
    year_y = grid_start_y + total_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def generate_thirds_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate three-column layout (year divided into thirds).
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 7
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    cells_per_third = total_cells // 3
    rows_per_third = math.ceil(cells_per_third / cols)

    third_width = (cols * square_size) + ((cols - 1) * gap_size)
    third_height = (rows_per_third * square_size) + ((rows_per_third - 1) * gap_size)

    h_spacing = 3 * GRID_UNIT

    total_width = 3 * third_width + 2 * h_spacing

    year_font = get_font(42, config.font)
    year_text_height = 50
    year_padding = GRID_UNIT * 2

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = third_height + year_padding + year_text_height

    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

    cell_counter = 0
    day_counter = 0

    for third_idx in range(3):
        third_x = start_x + third_idx * (third_width + h_spacing)
        third_cells_drawn = 0

        for row in range(rows_per_third):
            for col in range(cols):
                if cell_counter >= total_cells:
                    break
                if third_cells_drawn >= cells_per_third + 15:
                    break

                x = third_x + col * (square_size + gap_size)
                y = start_y + row * (square_size + gap_size)

                if cell_counter < jan_1_weekday:
                    pass
                else:
                    day_counter += 1
                    if day_counter < day_of_year:
                        draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                    elif day_counter == day_of_year:
                        draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                    else:
                        draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

                cell_counter += 1
                third_cells_drawn += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2
    year_y = start_y + third_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def generate_wide_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate wide grid layout (14 columns - two weeks side-by-side).
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 14  # Double width
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    rows = math.ceil(total_cells / cols)

    grid_width = (cols * square_size) + ((cols - 1) * gap_size)
    grid_height = (rows * square_size) + ((rows - 1) * gap_size)

    year_font = get_font(42, config.font)
    year_text_height = 50
    year_padding = GRID_UNIT * 2

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = grid_height + year_padding + year_text_height

    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - grid_width) // 2
    start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

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
                    draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                elif day_counter == day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                else:
                    draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

            cell_counter += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2
    year_y = start_y + grid_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def generate_months_layout(target_date: datetime, config: StyleConfig = None) -> Image.Image:
    """
    Generate 12-month grid layout (3x4 traditional calendar).
    """
    if config is None:
        config = StyleConfig()

    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    img = Image.new('RGB', (WIDTH, HEIGHT), color=config.bg_color)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT
    cols_per_month = 7

    month_grid_cols = 3
    month_grid_rows = 4

    max_month_rows = 6

    month_width = (cols_per_month * square_size) + ((cols_per_month - 1) * gap_size)
    month_height = (max_month_rows * square_size) + ((max_month_rows - 1) * gap_size)

    month_h_spacing = 3 * GRID_UNIT
    month_v_spacing = 5 * GRID_UNIT

    total_width = (month_grid_cols * month_width) + ((month_grid_cols - 1) * month_h_spacing)
    total_height = (month_grid_rows * month_height) + ((month_grid_rows - 1) * month_v_spacing)

    month_font = get_font(32, config.font)
    year_font = get_font(42, config.font)
    year_text_height = 50
    year_padding = GRID_UNIT * 2

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT
    available_height = HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM) * GRID_UNIT
    total_content_height = total_height + year_padding + year_text_height

    grid_start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    grid_start_y = MARGIN_TOP * GRID_UNIT + (available_height - total_content_height) // 2

    day_counter = 0

    for month_num in range(1, 13):
        month_grid_row = (month_num - 1) // month_grid_cols
        month_grid_col = (month_num - 1) % month_grid_cols

        month_x = grid_start_x + month_grid_col * (month_width + month_h_spacing)
        month_y = grid_start_y + month_grid_row * (month_height + month_v_spacing)

        month_start = datetime(year, month_num, 1)
        days_in_month = calendar.monthrange(year, month_num)[1]
        month_start_weekday = (month_start.weekday() + 1) % 7

        month_name = month_start.strftime("%b")
        draw.text((month_x, month_y - 45), month_name, fill=config.text_color, font=month_font)

        cell_counter = 0
        for week in range(max_month_rows):
            for day in range(cols_per_month):
                x = month_x + day * (square_size + gap_size)
                y = month_y + week * (square_size + gap_size)

                if cell_counter < month_start_weekday:
                    cell_counter += 1
                    continue

                day_in_month = cell_counter - month_start_weekday + 1
                if day_in_month > days_in_month:
                    break

                day_counter += 1

                if day_counter < day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.past_color, config.shape, fill=True)
                elif day_counter == day_of_year:
                    draw_day_shape(draw, x, y, square_size, config.today_color, config.shape, fill=False)
                else:
                    draw_day_shape(draw, x, y, square_size, config.future_color, config.shape, fill=False)

                cell_counter += 1

    # Draw year text centered below the grid
    year_text = str(year)
    bbox = draw.textbbox((0, 0), year_text, font=year_font)
    year_text_width = bbox[2] - bbox[0]
    year_x = (WIDTH - year_text_width) // 2
    year_y = grid_start_y + total_height + year_padding
    draw.text((year_x, year_y), year_text, fill=config.text_color, font=year_font)

    # Draw progress text if enabled
    if config.show_progress:
        progress_pct = int((day_of_year / total_days) * 100)
        progress_text = f"{progress_pct}%"
        progress_font = get_font(28, config.font)
        bbox = draw.textbbox((0, 0), progress_text, font=progress_font)
        progress_width = bbox[2] - bbox[0]
        progress_x = (WIDTH - progress_width) // 2
        progress_y = year_y + year_text_height + GRID_UNIT
        draw.text((progress_x, progress_y), progress_text, fill=config.text_color, font=progress_font)

    return img


def parse_date(date: str = None) -> datetime:
    """Parse date parameter or return today."""
    if date:
        try:
            return datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
    return datetime.now()
