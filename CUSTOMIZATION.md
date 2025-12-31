# Customization

Add query parameters to any route URL.

## Parameters

| Param | Description | Default | Values |
|-------|-------------|---------|--------|
| `date` | Target date | today | `YYYY-MM-DD` |
| `bg` | Background | `1a1a1a` | 6-char hex |
| `past` | Past days | `ffffff` | 6-char hex |
| `today` | Today | `F56B3F` | 6-char hex |
| `future` | Future days | `404040` | 6-char hex |
| `text` | Text | `ffffff` | 6-char hex |
| `shape` | Day shape | `square` | `circle`, `rounded` |
| `progress` | Year % | off | `true` |
| `font` | Font | `sans` | `serif`, `mono` |

## Examples

```
/quarters?shape=circle&progress=true
/standard?bg=000000&today=ff5555&font=mono
/months?shape=rounded&past=cccccc
```
