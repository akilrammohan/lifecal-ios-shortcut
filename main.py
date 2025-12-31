from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import calendar
import math

# iPhone 15 / 15 Pro dimensions
WIDTH = 1179
HEIGHT = 2556

# Grid system: all measurements in multiples of 16px
GRID_UNIT = 16

# Margins (in grid units)
MARGIN_LEFT = 4    # 64px
MARGIN_RIGHT = 4   # 64px
MARGIN_TOP = 4     # 64px
MARGIN_BOTTOM = 10 # 160px

# Colors
BG_COLOR = '#1a1a1a'
PAST_DAY_COLOR = '#ffffff'
TODAY_COLOR = '#F56B3F'
FUTURE_DAY_COLOR = '#404040'
TEXT_COLOR = '#ffffff'


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_days_in_year(year: int) -> int:
    """Get total days in a year (365 or 366)."""
    return 366 if is_leap_year(year) else 365


def generate_standard_layout(target_date: datetime) -> Image.Image:
    """
    Generate standard single-column yearly calendar wallpaper.
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

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

    try:
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        year_font = ImageFont.load_default()

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

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def generate_split_layout(target_date: datetime) -> Image.Image:
    """
    Generate two-column layout (year split into two halves).
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
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

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT

    horizontal_spacing = 4 * GRID_UNIT
    total_width = 2 * grid_width + horizontal_spacing
    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2

    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    start_y = grid_bottom_y - grid_height

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
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                elif day_counter == day_of_year:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                else:
                    draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

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
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                elif day_counter == day_of_year:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                else:
                    draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

            cell_counter += 1

    try:
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        year_font = ImageFont.load_default()

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def generate_quarters_layout(target_date: datetime) -> Image.Image:
    """
    Generate four quarters layout (Q1-Q4 in 2x2 grid).
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
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

    total_width = 2 * quarter_width + h_spacing
    total_height = 2 * quarter_height + v_spacing

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT

    grid_start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    grid_start_y = grid_bottom_y - total_height

    quarter_positions = [
        (grid_start_x, grid_start_y),
        (grid_start_x + quarter_width + h_spacing, grid_start_y),
        (grid_start_x, grid_start_y + quarter_height + v_spacing),
        (grid_start_x + quarter_width + h_spacing, grid_start_y + quarter_height + v_spacing),
    ]

    try:
        quarter_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        quarter_font = ImageFont.load_default()
        year_font = ImageFont.load_default()

    for q_idx, (q_x, q_y) in enumerate(quarter_positions):
        q_info = quarter_info[q_idx]

        quarter_label = f"Q{q_idx + 1}"
        draw.text((q_x, q_y - 28), quarter_label, fill=TEXT_COLOR, font=quarter_font)

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
                        draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                    elif actual_day_of_year == day_of_year:
                        draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                    else:
                        draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

                cell_counter += 1

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def generate_thirds_layout(target_date: datetime) -> Image.Image:
    """
    Generate three-column layout (year divided into thirds).
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
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

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT

    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    start_y = grid_bottom_y - third_height

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
                        draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                    elif day_counter == day_of_year:
                        draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                    else:
                        draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

                cell_counter += 1
                third_cells_drawn += 1

    try:
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        year_font = ImageFont.load_default()

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def generate_wide_layout(target_date: datetime) -> Image.Image:
    """
    Generate wide grid layout (14 columns - two weeks side-by-side).
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday
    total_days = get_days_in_year(year)

    jan_1 = datetime(year, 1, 1)
    jan_1_weekday = (jan_1.weekday() + 1) % 7
    total_cells = jan_1_weekday + total_days

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    SQUARE_UNITS = 1
    GAP_UNITS = 1
    cols = 14  # Double width
    square_size = SQUARE_UNITS * GRID_UNIT
    gap_size = GAP_UNITS * GRID_UNIT

    rows = math.ceil(total_cells / cols)

    grid_width = (cols * square_size) + ((cols - 1) * gap_size)
    grid_height = (rows * square_size) + ((rows - 1) * gap_size)

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT

    start_x = MARGIN_LEFT * GRID_UNIT + (available_width - grid_width) // 2
    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    start_y = grid_bottom_y - grid_height

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

    try:
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        year_font = ImageFont.load_default()

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def generate_months_layout(target_date: datetime) -> Image.Image:
    """
    Generate 12-month grid layout (3x4 traditional calendar).
    """
    year = target_date.year
    day_of_year = target_date.timetuple().tm_yday

    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
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

    available_width = WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * GRID_UNIT

    grid_start_x = MARGIN_LEFT * GRID_UNIT + (available_width - total_width) // 2
    grid_bottom_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT)
    grid_start_y = grid_bottom_y - total_height

    try:
        month_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        year_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        month_font = ImageFont.load_default()
        year_font = ImageFont.load_default()

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
        draw.text((month_x, month_y - 28), month_name, fill=TEXT_COLOR, font=month_font)

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
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=PAST_DAY_COLOR)
                elif day_counter == day_of_year:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=TODAY_COLOR)
                else:
                    draw.rectangle([x, y, x + square_size, y + square_size], outline=FUTURE_DAY_COLOR, width=2)

                cell_counter += 1

    year_text = str(year)
    year_x = MARGIN_LEFT * GRID_UNIT
    year_y = HEIGHT - (MARGIN_BOTTOM * GRID_UNIT) + (GRID_UNIT * 2)
    draw.text((year_x, year_y), year_text, fill=TEXT_COLOR, font=year_font)

    return img


def parse_date(date: str = None) -> datetime:
    """Parse date parameter or return today."""
    if date:
        try:
            return datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
    return datetime.now()
