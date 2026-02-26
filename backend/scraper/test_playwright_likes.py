from playwright.sync_api import sync_playwright
import time
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include')
    time.sleep(3)
    try:
        page.locator('a:has-text("はい"), button:has-text("はい")').first.click(timeout=3000)
        time.sleep(3)
    except: pass
    
    page.wait_for_selector('li.item-card')
    cards = page.locator('li.item-card')
    card_count = cards.count()
    print('Cards found:', card_count)
    
    page_qualifying = 0
    for i in range(min(5, card_count)):
        card = cards.nth(i)
        
        # --- Extract likes ---
        likes = 0
        try:
            likes_parent = card.locator('[class*="shop__text--link"]').first
            if likes_parent.count() > 0:
                likes_div = likes_parent.locator('.typography-14').first
                if likes_div.count() > 0:
                    likes_text = likes_div.inner_text()
                    nums = re.findall(r'[\d,]+', likes_text)
                    if nums:
                        likes = int(nums[0].replace(',', ''))
        except Exception as e:
            print("Like extraction error:", e)
            
        print(f"Card {i} likes: {likes}")
