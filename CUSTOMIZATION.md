# Customization

Add query parameters to any route URL.

## Parameters

| Param | Description | Default | Values |
|-------|-------------|---------|--------|
| `date` | Target date (yearly calendars only) | today | `YYYY-MM-DD` |
| `birthday` | Your birthday (**required** for `/life`) | - | `YYYY-MM-DD` |
| `bg` | Background color | `1a1a1a` | 6-char hex |
| `past` | Past days/weeks fill color | `ffffff` | 6-char hex |
| `today` | Current day/week outline color | `F56B3F` | 6-char hex |
| `future` | Future days/weeks outline color | `404040` | 6-char hex |
| `text` | Text color | `ffffff` | 6-char hex |
| `shape` | Indicator shape | `square` | `circle`, `rounded` |
| `progress` | Show progress (yearly: %, life: % to 80) | off | `true` |
| `font` | Font style | `sans` | `serif`, `mono` |

## Examples

### Yearly Calendars
```
/quarters?shape=circle&progress=true
/standard?bg=000000&today=ff5555&font=mono
/months?shape=rounded&past=cccccc&date=2025-12-31
```

### Life Calendar
```
/life?birthday=1990-01-15&progress=true
/life?birthday=1985-06-20&shape=circle&bg=0a0a0a
/life?birthday=2000-03-10&progress=true&today=00ff00
```
