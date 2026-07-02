# BookMyShow Movie Notifier

BookMyShow Movie Notifier watches a BookMyShow movie listing and sends an ntfy alert when a new theatre is added for prebooking.

It is built for one simple job:

- open the BookMyShow page
- detect when a new theatre appears
- notify you on your phone

## Why I made this

On 02-07-2026 I wanted to watch *Spider-Man: Brand New Day*, which releases on 30-07-2026. The only theatre available for prebooking in my city was around 40km away from my place, so I built this tool to notify me on my phone when a new theatre gets added on BookMyShow for the first-day show.

I’m a very big Spider-Man fan, so yes, this was a completely normal and definitely not obsessive project.

You can use it too if you want phone notifications when a movie suddenly gets more prebooking options.

If you read the whole thing, love ya :)

See yaa

## Features

- Automatic monitoring with randomized check intervals
- Headless or visible Chromium support
- ntfy push notifications
- GUI launcher for easy use

## Requirements

- Python 3.12+
- Internet access for BookMyShow and ntfy
- Playwright installed

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install
```

## Configuration

Create a `.env` file and set:

```env
BOOKMYSHOW_URL=https://in.bookmyshow.com/movies/chennai/spider-man-brand-new-day-epiq-3d/buytickets/ET00505581/20260730
CHECK_INTERVAL_MIN=30
CHECK_INTERVAL_MAX=60
HEADLESS=false
NTFY_URL=https://ntfy.sh/movie
LOG_LEVEL=INFO
```

If you want a fixed interval, set `CHECK_INTERVAL_MIN` and `CHECK_INTERVAL_MAX` to the same value.

## Run

```powershell
python runme.py
```

or:

```powershell
python main.py
```

## Testing

```powershell
pytest
```

## Notes

- The watcher compares theatres by name.
- The GUI starts monitoring automatically.
- Notifications use the configured BookMyShow URL as the click target.
