# Yearly Calendar iOS Wallpaper

API endpoint that generates yearly calendar wallpapers. Use with iOS Shortcuts to auto-update your lock screen with your progress through the year.

<img src="https://wallpaper.akilr.com/standard" alt="Calendar Example" width="300">

Inspired by [this tweet by @luismbat](https://x.com/luismbat/status/2006002189479932247).

## Routes

**Base URL:** `https://wallpaper.akilr.com`

All routes return PNG (1179×2556px).

- `/standard` - Single column layout
- `/split` - Two columns (year split in half)
- `/quarters` - Four quarters (Q1-Q4) in 2×2 grid with labels
- `/thirds` - Three columns
- `/wide` - 14 columns (two weeks side-by-side)
- `/months` - 12-month calendar in 3×4 grid

## Customization

Add query parameters to customize your wallpaper:

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `date` | Target date | today | `2025-12-31` |
| `bg` | Background color | `1a1a1a` | `000000` |
| `past` | Past days fill | `ffffff` | `cccccc` |
| `today` | Today highlight | `F56B3F` | `ff0000` |
| `future` | Future outline | `404040` | `666666` |
| `text` | Text color | `ffffff` | `aaaaaa` |
| `shape` | Day shape | `square` | `circle`, `rounded` |
| `progress` | Show year % | off | `true` |
| `font` | Font style | `sans` | `serif`, `mono` |

**Example URLs:**
```
/quarters?shape=circle&progress=true
/standard?bg=000000&today=ff5555&font=mono
/months?past=cccccc&future=333333&shape=rounded
```

## iOS Shortcut Setup

1. **Create Shortcut**: Open Shortcuts app → New Shortcut
2. **Add Actions**:
   - "Get contents of URL" → `https://wallpaper.akilr.com/quarters` (or your preferred layout with customizations)
   - "Set Wallpaper" → Choose "Lock Screen"
3. **IMPORTANT**: Tap the "Set Wallpaper" action → tap the arrow (→) to show options → **disable "Crop to Subject"**
   - This prevents iOS from automatically cropping/resizing the wallpaper
4. **Automate**: Go to Automation tab → New Automation → Time of Day → 6:00 AM → Run your shortcut

That's it! Your wallpaper will update every morning.

## Planned Additions

- Full life calendar (80-year lifespan, takes your birthday)

## Credits

- Inspired by [@luismbat](https://x.com/luismbat/status/2006002189479932247)
- Deployed at [wallpaper.akilr.com](https://wallpaper.akilr.com)
