"""Daily Report Bot (NSE sector performance) - Social Eagle Assignment 1

Flow:
  1. Open Chrome -> NSE sector-watch page -> copy the page text
  2. Parse the sectoral index rows (Nifty IT, Nifty Bank, ...)
  3. Open Excel -> new workbook -> type the daily report row
        [Date & Time | Fetched Data (best/worst sector) | Comment]
     plus a sector-wise table underneath
  4. Save as daily_report_YYYY-MM-DD.xlsx
  5. Screenshot the final sheet

Setup:  pip install pyautogui pyperclip
Run:    python daily_report_bot.py
Do not touch the mouse/keyboard while it runs. Fail-safe: slam the mouse into
the top-left corner to abort.
"""
import os
import re
import sys
import time
from datetime import datetime

import pyautogui
import pyperclip

# ---------- Settings ----------
# Page that lists all NSE sectoral indices: name, value, change, change %, prev close.
# Open it in Chrome once yourself to confirm the table is visible before running.
URL = "https://www.geojit.com/equity/sector-watch/NSE/Nifty-Bank/26753"

PAGE_LOAD_WAIT = 10    # seconds for Chrome to open and load the page
EXCEL_OPEN_WAIT = 10   # seconds for Excel to start
SAVE_DIALOG_WAIT = 3
SAVE_FINISH_WAIT = 3
MIN_SECTORS = 5        # fewer rows than this = the copy/parse failed

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

now = datetime.now()
TIMESTAMP = now.strftime("%Y-%m-%d %H:%M:%S")
DATE_STR = now.strftime("%Y-%m-%d")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(OUT_DIR, f"daily_report_{DATE_STR}.xlsx")
SHOT_PATH = os.path.join(OUT_DIR, f"daily_report_{DATE_STR}.png")

# "Nifty Metal 10,347.45 105.60 1.03 10,241.85"  (name, value, change, change %, prev close)
ROW_PATTERN = re.compile(
    r"(Nifty [A-Za-z&. ]+?)\s+"
    r"(\d[\d,]*\.\d+)\s+"
    r"(-?\d[\d,]*\.\d+)\s+"
    r"(-?\d+\.\d+)\s+"
    r"(\d[\d,]*\.\d+)"
)


# ---------- Helpers ----------
def open_app(name):
    """Open an app through the Windows Run dialog (Win+R)."""
    pyautogui.hotkey("win", "r")
    time.sleep(1)
    pyautogui.write(name, interval=0.03)
    pyautogui.press("enter")


def to_float(text):
    return float(text.replace(",", ""))


def parse_sectors(text):
    """Pull sector rows out of the copied page text. Returns a list of dicts."""
    sectors = {}
    for name, value, change, pct, prev in ROW_PATTERN.findall(text):
        sectors[name.strip()] = {
            "name": name.strip(),
            "value": to_float(value),
            "change": to_float(change),
            "pct": to_float(pct),
            "prev": to_float(prev),
        }
    return sorted(sectors.values(), key=lambda s: s["pct"], reverse=True)


def fetch_sectors():
    """Open Chrome, copy all page text, parse it. Retries if the page was slow."""
    pyperclip.copy("")  # clear clipboard so we can tell if the copy worked
    open_app(f"chrome {URL}")
    time.sleep(PAGE_LOAD_WAIT)

    sectors = []
    for attempt in range(1, 4):
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        time.sleep(1)
        sectors = parse_sectors(pyperclip.paste())
        if len(sectors) >= MIN_SECTORS:
            break
        print(f"Only {len(sectors)} sectors found (attempt {attempt}/3). Waiting for page...")
        time.sleep(5)

    if len(sectors) < MIN_SECTORS:
        sys.exit("Could not read the sector table from Chrome. Check the URL/page layout.")

    pyautogui.hotkey("ctrl", "w")  # close the tab
    return sectors


def summarise(sectors):
    """Return (fetched-data summary, comment) built from the parsed sectors."""
    best, worst = sectors[0], sectors[-1]
    up = sum(1 for s in sectors if s["pct"] > 0)
    summary = (
        f"{len(sectors)} sectors | Best: {best['name']} ({best['pct']:+.2f}%) | "
        f"Worst: {worst['name']} ({worst['pct']:+.2f}%)"
    )
    if up >= len(sectors) * 0.65:
        mood = "Broad-based rally, positive market breadth"
    elif up <= len(sectors) * 0.35:
        mood = "Broad-based selling, cautious sentiment"
    else:
        mood = "Mixed market, stock-specific and sector rotation"
    comment = f"{mood} ({up}/{len(sectors)} sectors up)"
    return summary, comment


def sector_table_text(sectors):
    """Tab-separated block so one paste fills many cells."""
    lines = ["Sector\tIndex Value\tChange\tChange %\tPrev Close"]
    for s in sectors:
        lines.append(f"{s['name']}\t{s['value']}\t{s['change']}\t{s['pct']}\t{s['prev']}")
    return "\n".join(lines)


def fill_excel(summary, comment, sectors):
    """Open Excel, create a blank workbook, type the report row + sector table."""
    open_app("excel")
    time.sleep(EXCEL_OPEN_WAIT)
    pyautogui.hotkey("ctrl", "n")  # blank workbook from the start screen
    time.sleep(3)
    pyautogui.hotkey("win", "up")  # maximize so the screenshot shows the sheet
    time.sleep(1)

    # Row 1: headers (Tab moves right, Enter returns to column A on the next row)
    for header in ("Date & Time", "Fetched Data", "Comment"):
        pyautogui.write(header)
        pyautogui.press("tab")
    pyautogui.press("enter")

    # Row 2: the daily report row (summary/comment pasted to handle special characters)
    pyautogui.write(TIMESTAMP)
    pyautogui.press("tab")
    pyperclip.copy(summary)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("tab")
    pyperclip.copy(comment)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

    # Row 5 onwards: sector-wise table (cursor is on A3, move down 2 rows)
    pyautogui.press("down", presses=2)
    pyperclip.copy(sector_table_text(sectors))
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    # Auto-fit column widths so everything is visible in the screenshot
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("alt", "h")
    pyautogui.press("o")
    pyautogui.press("i")
    pyautogui.hotkey("ctrl", "home")


def save_excel():
    pyautogui.press("f12")  # opens the classic Save As dialog
    time.sleep(SAVE_DIALOG_WAIT)
    pyautogui.write(XLSX_PATH, interval=0.02)
    pyautogui.press("enter")
    time.sleep(SAVE_FINISH_WAIT)


def take_screenshot():
    time.sleep(1)
    pyautogui.screenshot(SHOT_PATH)


# ---------- Main ----------
def main():
    print("Starting in 5 seconds. Don't touch the mouse or keyboard...")
    time.sleep(5)

    sectors = fetch_sectors()
    summary, comment = summarise(sectors)
    print("Fetched:", summary)
    print("Comment:", comment)

    fill_excel(summary, comment, sectors)
    save_excel()
    take_screenshot()

    print(f"Done!\n  Excel:      {XLSX_PATH}\n  Screenshot: {SHOT_PATH}")


if __name__ == "__main__":
    main()