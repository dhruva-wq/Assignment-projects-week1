from playwright.sync_api import sync_playwright
from datetime import datetime

print("Starting the Playwright automation script...")
print(f"Script started at: {datetime.now()}")

#Daily Weather Report Bot

#Chromium --> Weather Website --> Extract the report --> Take Screenshot -->Final text file with the report
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_default_timeout(15000)   # fail after 15s with a clear message instead of hanging

    try:
        # ---- Navigation + Typing + Waiting (Bing instead of Google) ----
        page.goto("https://www.bing.com")
        page.wait_for_timeout(2000)                # NEW: 2s pause
        page.screenshot(path="bing.png")
        page.wait_for_timeout(2000)                # NEW

        page.fill("[name='q']", "Playwright")      # works for input or textarea
        page.wait_for_timeout(2000)                # NEW
        page.press("[name='q']", "Enter")
        page.wait_for_selector("#b_results")        # Bing's results container
        page.wait_for_timeout(2000)                # NEW
        page.screenshot(path="search_results.png")
        page.wait_for_timeout(2000)                # NEW

        # ---- Extracting the data ----
        print(f"Page title: {page.title()}")

        # ---- Navigation (AccuWeather) ----
        page.goto("https://www.accuweather.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)                # NEW
        page.screenshot(path="accuweather.png")
        page.wait_for_timeout(2000)                # NEW

        # ---- Clicking ----
        page.get_by_role("link", name="Advertising").first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)                # NEW
        page.screenshot(path="Advertising.png")

    finally:
        browser.close()   # always runs, even if a step above fails
print(f"Script completed at: {datetime.now()}")