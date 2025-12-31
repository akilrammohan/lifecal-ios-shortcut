# Yearly Calendar iOS Wallpaper

API endpoint that generates yearly calendar wallpapers. Use with iOS Shortcuts to auto-update your lock screen with your progress through the year.

<img src="https://wallpaper.akilr.com/standard" alt="Calendar Example" width="300">

Inspired by [this tweet by @luismbat](https://x.com/luismbat/status/2006002189479932247).

## Routes

**Base URL:** `https://wallpaper.akilr.com`

All routes accept optional `?date=YYYY-MM-DD` parameter. Returns JPEG (1179×2556px).

- `/standard` - Single column layout
- `/split` - Two columns (year split in half)
- `/quarters` - Four quarters (Q1-Q4) in 2×2 grid with labels
- `/thirds` - Three columns
- `/wide` - 14 columns (two weeks side-by-side)
- `/months` - 12-month calendar in 3×4 grid

## iOS Shortcut Setup

1. **Create Shortcut**: Open Shortcuts app → New Shortcut
2. **Add Actions**:
   - "Get contents of URL" → `https://wallpaper.akilr.com/quarters` (or your preferred layout)
   - "Set Wallpaper" → Choose "Lock Screen"
3. **Automate**: Go to Automation tab → New Automation → Time of Day → 6:00 AM → Run your shortcut

That's it! Your wallpaper will update every morning.

## Planned Additions

- More styling options: colors, shapes, themes
- Customizable color schemes
- Full life calendar (80-year lifespan, takes your birthday)
- Different shape styles (circles, rounded squares, etc.)

## Credits

- Inspired by [@luismbat](https://x.com/luismbat/status/2006002189479932247)
- Deployed at [wallpaper.akilr.com](https://wallpaper.akilr.com)
