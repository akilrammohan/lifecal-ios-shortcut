# Calendar Wallpapers for iOS

API endpoints that generate calendar wallpapers for iOS. Auto-update your lock screen with your progress through the year or through life.

<img src="https://wallpaper.akilr.com/standard" alt="Calendar Example" width="300">

Inspired by [this tweet by @luismbat](https://x.com/luismbat/status/2006002189479932247).

## Routes

**Base URL:** `https://wallpaper.akilr.com`

All routes return PNG (1179×2556px).

### Yearly Calendars
Track your progress through the current year. Updates daily.

- `/standard` - Single column layout
- `/split` - Two columns (year split in half)
- `/quarters` - Four quarters (Q1-Q4) in 2×2 grid with labels
- `/thirds` - Three columns
- `/wide` - 14 columns (two weeks side-by-side)
- `/months` - 12-month calendar in 3×4 grid

**Example:** `https://wallpaper.akilr.com/quarters?shape=circle&progress=true`

### Life Calendar
Track your progress through life. 52 weeks × 80+ years grid. Updates weekly.

- `/life?birthday=YYYY-MM-DD` - Life in weeks (requires birthday parameter)

**Example:** `https://wallpaper.akilr.com/life?birthday=1990-01-15&progress=true&shape=circle`

### Customization
Customize colors, shapes, fonts, and more via query strings. See [CUSTOMIZATION.md](CUSTOMIZATION.md).

## iOS Shortcut Setup

1. **Create Shortcut**: Open Shortcuts app → New Shortcut
2. **Add Actions**:
   - "Get contents of URL" → `https://wallpaper.akilr.com/quarters` (or your preferred layout with customizations)
   - "Set Wallpaper" → Choose "Lock Screen"
3. **IMPORTANT**: Tap the "Set Wallpaper" action → tap the arrow (→) to show options → **disable "Crop to Subject"**
   - This prevents iOS from automatically cropping/resizing the wallpaper
4. **Automate**: Go to Automation tab → New Automation → Time of Day → 6:00 AM → Run your shortcut

That's it! Your wallpaper will update every morning.

## Credits

- Inspired by [@luismbat](https://x.com/luismbat/status/2006002189479932247)
- Deployed at [wallpaper.akilr.com](https://wallpaper.akilr.com)
