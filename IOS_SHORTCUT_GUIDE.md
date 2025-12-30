# iOS Shortcut Setup Guide

## Overview
This guide walks you through creating an iOS Shortcut that automatically updates your lock screen wallpaper with the yearly calendar every day.

---

## Step 1: Deploy the API Endpoint

You need to deploy the FastAPI endpoint to a public URL. Choose one option below:

### Option A: Vercel (Recommended - Free)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Create `vercel.json` in project root:
   ```json
   {
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Your API URL will be something like: `https://lifecal-ios-shortcut.vercel.app`

### Option B: Railway (Easy Deploy)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select this repo
4. Railway will auto-detect Python and deploy
5. Get your public URL from the deployment

### Option C: Fly.io (Good Performance)

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Create `fly.toml` in project root:
   ```toml
   app = "lifecal-calendar"
   primary_region = "sjc"

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
   ```

3. Deploy:
   ```bash
   fly launch
   fly deploy
   ```

---

## Step 2: Test Your Deployed API

Once deployed, test it in your browser:

```
https://your-api-url.com/calendar?date=2025-12-30
```

You should see the calendar PNG image.

---

## Step 3: Create the iOS Shortcut

### Manual Setup (iOS Shortcuts App)

1. Open the **Shortcuts** app on your iPhone

2. Tap the **+** button to create a new shortcut

3. Add the following actions in order:

   **Action 1: Get Current Date**
   - Search for "Current Date"
   - Add "Current Date" action

   **Action 2: Format Date**
   - Search for "Format Date"
   - Add "Format Date" action
   - Set format to "Custom"
   - Enter format: `yyyy-MM-dd`

   **Action 3: Get Contents of URL**
   - Search for "Get Contents of URL"
   - Add "Get Contents of URL" action
   - Set URL to: `https://YOUR-API-URL.com/calendar?date=FORMATTED_DATE`
   - Tap on "Formatted Date" to insert the variable from Action 2

   **Action 4: Set Wallpaper**
   - Search for "Set Wallpaper"
   - Add "Set Wallpaper" action
   - Set to "Lock Screen" only (or both if you want)
   - Toggle "Show Preview" OFF (for automatic updates)

4. Name your shortcut: "Update Calendar Wallpaper"

5. Tap "Done"

---

## Step 4: Set Up Daily Automation

1. Go to the **Automation** tab in Shortcuts app

2. Tap **+** to create a new automation

3. Select **Time of Day**

4. Set time to **6:00 AM** (or your preferred time)

5. Set repeat to **Daily**

6. Tap **Next**

7. Tap **Add Action** → Search for your shortcut name: "Update Calendar Wallpaper"

8. **IMPORTANT**: Toggle OFF "Ask Before Running" and "Notify When Run"
   - This ensures it runs silently every morning

9. Tap **Done**

---

## Step 5: Test It

1. Run the shortcut manually first to test
2. Grant permissions when prompted (Photos, Network access)
3. Check your lock screen - you should see the calendar!

---

## Customization Options

### Change Image Dimensions

Edit `main.py` line 33-34 to match your iPhone model:

```python
# iPhone 14 Pro / 15 Pro
WIDTH = 1179
HEIGHT = 2556

# iPhone 14 Plus / 15 Plus
WIDTH = 1290
HEIGHT = 2796

# iPhone SE
WIDTH = 750
HEIGHT = 1334
```

### Change Colors

Edit `main.py` lines 37-40:

```python
BG_COLOR = '#1a1a1a'  # Background
PAST_DAY_COLOR = '#ffffff'  # Filled squares
FUTURE_DAY_COLOR = '#333333'  # Empty square outlines
TEXT_COLOR = '#ffffff'  # Text
```

### Change Grid Size

Edit `main.py` lines 52-53:

```python
square_size = 10  # Size of each square
spacing = 14  # Space between squares
```

---

## Troubleshooting

**Shortcut fails to run:**
- Check your API URL is correct and publicly accessible
- Ensure you granted all permissions
- Check "Shortcuts" app → Settings → Advanced → Allow Running Scripts

**Image doesn't update:**
- Make sure "Ask Before Running" is OFF in automation
- Check automation is enabled
- Try running shortcut manually first

**Wrong date showing:**
- API uses current date automatically
- Make sure your iPhone's time zone is correct

**Image looks wrong on lock screen:**
- Adjust WIDTH and HEIGHT in code to match your exact iPhone model

---

## API Endpoints Reference

**GET /**
- Returns API info

**GET /calendar**
- Query params: `date` (optional, format: YYYY-MM-DD)
- Returns: PNG image
- Example: `/calendar?date=2025-12-30`

---

## Notes

- The shortcut runs locally on your phone but fetches the image from your API
- Each request generates a fresh image (takes ~100ms)
- API includes 1-hour cache headers for efficiency
- Works with both regular years (365 days) and leap years (366 days)
- Year is automatically displayed in bottom left corner
