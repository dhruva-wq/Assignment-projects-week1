from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_default_timeout(15000)   # NEW: fail after 15s with a clear message instead of hanging

    try:
        # ---- Navigation + Typing + Waiting (Bing instead of Google) ----
        page.goto("https://www.bing.com")
        page.screenshot(path="bing.png")

        page.fill("[name='q']", "Playwright")      # works for input or textarea
        page.press("[name='q']", "Enter")
        page.wait_for_selector("#b_results")        # Bing's results container
        page.screenshot(path="search_results.png")

        # ---- Extracting the data ----
        print(f"Page title: {page.title()}")

        # ---- Navigation (AccuWeather) ----
        page.goto("https://www.accuweather.com/", wait_until="domcontentloaded")
        page.screenshot(path="accuweather.png")

        # ---- Clicking ----
        page.get_by_role("link", name="Advertising").first.click()
        page.wait_for_load_state("domcontentloaded")
        page.screenshot(path="Advertising.png")

    finally:
        browser.close()   # NEW: always runs, even if a step above failsf