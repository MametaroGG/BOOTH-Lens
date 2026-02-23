from playwright.sync_api import sync_playwright
import logging

def debug_selectors():
    target_url = "https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include&sort=popular"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(target_url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        cards = page.locator("li.item-card")
        count = cards.count()
        print(f"Found {count} cards.")
        
        if count > 0:
            first_card = cards.nth(0)
            html = first_card.inner_html()
            with open("card_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Dumped first card HTML to card_debug.html")
            
            # Test selectors
            likes_loc = first_card.locator(".shop__text--link50, .js-wishlist-count, .item-card__likes").first
            print(f"Likes locator count: {likes_loc.count()}")
            if likes_loc.count() > 0:
                print(f"Likes text: '{likes_loc.inner_text()}'")
            
            link_loc = first_card.locator("a[href*='/items/']").first
            print(f"Link locator count: {link_loc.count()}")
            if link_loc.count() > 0:
                print(f"Link href: {link_loc.get_attribute('href')}")
        
        browser.close()

if __name__ == "__main__":
    debug_selectors()
