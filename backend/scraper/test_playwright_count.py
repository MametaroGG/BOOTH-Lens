from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include')
    time.sleep(3)
    try:
        page.locator('a:has-text("はい"), button:has-text("はい")').first.click(timeout=3000)
        time.sleep(3)
    except: pass
    page.wait_for_selector('li.item-card')
    print('Wait successful!')
    cards = page.locator('li.item-card')
    print('Cards count:', cards.count())
