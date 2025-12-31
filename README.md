# Yearly Calendar iOS Wallpaper

An iOS Shortcut-powered daily wallpaper that displays your progress through the year as a visual grid of days.

## What It Does

- Shows all 365 days of the year as a grid (366 for leap years)
- Automatically fills in squares for days that have passed
- Updates your iPhone lock screen wallpaper every morning
- Displays the current year in the bottom left corner
- **6 different layout styles** to choose from

## Layout Styles

Choose from 6 different layouts to customize your wallpaper:

1. **Standard** (`/standard`) - Single column layout with all days in one vertical grid
2. **Split** (`/split`) - Two-column layout with the year split into two halves
3. **Quarters** (`/quarters`) - Four quarters (Q1-Q4) in a 2×2 grid with labels on the left
4. **Thirds** (`/thirds`) - Three-column layout dividing the year into thirds
5. **Wide** (`/wide`) - Wide grid layout with 14 columns (two weeks side-by-side)
6. **Months** (`/months`) - Traditional 12-month calendar in a 3×4 grid

## Design

Inspired by [this tweet by @luismbat](https://x.com/luismbat/status/2006002189479932247) showing a yearly progress calendar.

**Visual Style:**
- Dark gray/almost black background
- White filled squares for completed days
- Orange square for current day
- Empty outlined squares for future days
- Minimal text labels (32px for labels, 42px for year)
- iPhone-optimized dimensions (1179×2556px)

## How It Works

1. **FastAPI Backend**: Generates calendar images on-demand
2. **iOS Shortcut**: Fetches daily image and sets as wallpaper
3. **Daily Automation**: Runs automatically every morning

## Quick Start

### 1. Local Testing

```bash
# Run the server locally
uv run uvicorn main:app --reload

# Visit in browser
open http://localhost:8000/standard
```

### 2. Deploy to Production

See [IOS_SHORTCUT_GUIDE.md](./IOS_SHORTCUT_GUIDE.md) for detailed deployment options:
- Vercel (recommended)
- Railway
- Fly.io

Or feel free to just use my deployed endpoint at https://wallpaper.akilr.com!

Sub that URL in for whatever the iOS setup guide says (or deploy your own if you want?)

### 3. Set Up iOS Shortcut

Follow the step-by-step guide in [IOS_SHORTCUT_GUIDE.md](./IOS_SHORTCUT_GUIDE.md)

## Project Structure

```
.
├── main.py                  # FastAPI app with image generation
├── pyproject.toml           # Python dependencies (managed by uv)
├── README.md                # This file
└── IOS_SHORTCUT_GUIDE.md    # Complete setup instructions
```

## Requirements

- Python 3.11+
- FastAPI
- Pillow
- uvicorn

All managed via `uv` package manager.

## API Endpoints

**GET /**
- Returns API info and available layouts

**GET /{layout}**
- Layouts: `standard`, `split`, `quarters`, `thirds`, `wide`, `months`
- Query params: `date` (optional, format: YYYY-MM-DD)
- Returns: PNG image (1179×2556px)
- Example: `/quarters?date=2025-12-30`

If no date is provided, uses current date.

## Customization

Edit `main.py` to customize:
- Image dimensions (WIDTH, HEIGHT constants)
- Colors (BG_COLOR, PAST_DAY_COLOR, TODAY_COLOR, etc.)
- Grid size and spacing (GRID_UNIT, MARGIN constants)
- Font sizes (get_font() calls)

## Features

- ✅ 6 different layout styles (standard, split, quarters, thirds, wide, months)
- ✅ Handles leap years automatically (366 days)
- ✅ Dynamic image generation (no pre-rendered images needed)
- ✅ Year display in bottom left
- ✅ iPhone wallpaper optimized dimensions (1179×2556px)
- ✅ Efficient caching headers
- ✅ Clean, minimal aesthetic

## Example

<img src="https://wallpaper.akilr.com/standard" alt="Calendar Example" width="300">

Live calendar image showing the standard layout (updates automatically with today's date).

The image shows:
- **White squares**: Days that have passed
- **Orange square**: Current day
- **Gray outlined squares**: Future days
- **Year text**: Bottom left corner

## License

MIT

## Credits

Inspired by [this tweet by @luismbat](https://x.com/luismbat/status/2006002189479932247) showing a yearly calendar iOS Shortcut implementation.
