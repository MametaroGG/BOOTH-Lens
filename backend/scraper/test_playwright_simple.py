from playwright.sync_api import sync_playwright
import sys

def test_playwright():
    print("Starting Playwright test...")
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            print("Creating context...")
            context = browser.new_context()
            print("Creating page...")
            page = context.new_page()
            print("Navigating to BOOTH...")
            page.goto("https://booth.pm/ja", wait_until="networkidle", timeout=30000)
            print(f"Page title: {page.title()}")
            browser.close()
            print("Success!")
    except Exception as e:
        print(f"Playwright test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_playwright()
