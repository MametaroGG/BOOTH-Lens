from playwright.sync_api import sync_playwright
import time
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled'],
    )
    context = browser.new_context(
        user_agent=USER_AGENT,
        locale='ja-JP',
        timezone_id='Asia/Tokyo',
    )
    page = context.new_page()
    page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    
    page.goto('https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include')
    time.sleep(3)
    try:
        page.locator('a:has-text("はい"), button:has-text("はい")').first.click(timeout=3000)
    except: pass
    time.sleep(3)
    
    try:
        page.wait_for_selector('li.item-card', timeout=5000)
    except Exception as e:
        print("Wait for selector timed out!")
        print(page.title())
        
    cards = page.locator('li.item-card')
    print('Cards count:', cards.count())
