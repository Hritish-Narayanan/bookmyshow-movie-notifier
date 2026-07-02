# BookMyShow Movie Notifier

BookMyShow Movie Notifier watches a BookMyShow movie listing and sends an ntfy alert when a new theatre is added for prebooking.

It is built for one simple job:

- open the BookMyShow page
- detect when a new theatre appears
- notify you on your phone

## Why I made this

sooooo on 02-07-2026 i wanted to watch the spiderman brand new day movie
which releases on 30-07-2026 
andddd the movie was available to prebook 
only on one theatre in my city which is around 40km away from my place and so..... 

me being me

i made a program which will notify me on my phone if a new theatre is available to prebook in bookmyshow for the first day show of spiderman brand new day

i cant help but im a very big fan of spiderman
hehehehe

you can use this program if you wanna get a notification when you wanna prebook for a movie  

if you did read the whole paragraph where i was yapping the whole time
love ya
:)

see yaa

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
