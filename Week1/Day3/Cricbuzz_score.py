"""Capture a live cricket score from Cricbuzz with Playwright (sync API).

Run headed first (watch it work):   python cricbuzz_score.py
Then headless (confirm it still works): python cricbuzz_score.py --headless
"""
import sys

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

URL = "https://www.cricbuzz.com/"

# YOUR TURN: inspect the live score on Cricbuzz (right-click -> Inspect), test the
# selector in the browser console with document.querySelector("..."), then paste it here.
SELECTOR = ".team-score"

TIMEOUT_MS = 15000                    # max time to wait for the score to appear
HEADLESS = "--headless" in sys.argv   # python cricbuzz_score.py --headless


def main():
    if not SELECTOR:
        sys.exit("Set SELECTOR at the top of the file first (inspect the score on Cricbuzz).")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        try:
            page.goto(URL, wait_until="domcontentloaded")

            score_el = page.locator(SELECTOR).first   # .first in case several matches exist
            try:
                score_el.wait_for(state="visible", timeout=TIMEOUT_MS)   # waits for the element, no sleep()
                print(score_el.inner_text().strip())
            except PlaywrightTimeout:
                # No live match (or the site is slow): say so instead of crashing
                print("No live score found within "
                      f"{TIMEOUT_MS // 1000}s - there may be no match in progress.")

            page.screenshot(path="score.png")
            print("saved score.png")
        finally:
            browser.close()


if __name__ == "__main__":
    main()