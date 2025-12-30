# Yearly Calendar iOS Wallpaper

An iOS Shortcut-powered daily wallpaper that displays your progress through the year as a visual grid of days.

## What It Does

- Shows all 365 days of the year as a grid (366 for leap years)
- Automatically fills in squares for days that have passed
- Updates your iPhone lock screen wallpaper every morning
- Displays the current year in the bottom left corner

## Design

Inspired by [Life Calendar by @waitbutwny](https://waitbutwhy.com/2014/05/life-weeks.html), adapted for a yearly view instead of lifetime view.

**Visual Style:**
- Dark gray/almost black background
- White filled squares for completed days
- Empty outlined squares for future days
- Minimal text labels
- iPhone-optimized dimensions

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
open http://localhost:8000/calendar
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
- Returns API info and usage instructions

**GET /calendar**
- Query params: `date` (optional, format: YYYY-MM-DD)
- Returns: PNG image (1170×2532px by default)
- Example: `/calendar?date=2025-12-30`

If no date is provided, uses current date.

## Customization

Edit `main.py` to customize:
- Image dimensions (lines 33-34)
- Colors (lines 37-40)
- Grid size (lines 52-53)
- Text labels (lines 76-77)

## Features

- ✅ Handles leap years automatically (366 days)
- ✅ Dynamic image generation (no pre-rendered images needed)
- ✅ Year display in bottom left
- ✅ iPhone wallpaper optimized dimensions
- ✅ Efficient caching headers
- ✅ Clean, minimal aesthetic

## Example Images

**Early in the year (Jan 15):**
- Only 15 filled squares, rest empty

**Late in the year (Dec 30):**
- 364 filled squares, 1 empty

**Leap year:**
- 53 rows instead of 52 to accommodate 366 days

## License

MIT

## Credits

Inspired by Tim Urban's [Life Calendar](https://waitbutwhy.com/2014/05/life-weeks.html) and Luis Batalha's iOS Shortcut implementation.
