import logging
import os
import json
import time
import requests
import io
from PIL import Image
from playwright.sync_api import sync_playwright
from booth_scraper import BoothScraper

# Reuse BoothScraper logic for metadata saving and R2 upload
class RobustBoothScraper(BoothScraper):
    def crawl_target_popular(self, target_url, min_likes=1000, max_pages=10):
        logging.info(f"--- [RobustScraper] Starting crawl: {target_url} ---")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=self.headers["User-Agent"])
            
            all_target_urls = []
            
            # --- Phase 1: Collect Item URLs from Search Pages ---
            for page_num in range(1, max_pages + 1):
                separator = "&" if "?" in target_url else "?"
                url = f"{target_url}{separator}page={page_num}"
                logging.info(f"Fetching search results page {page_num}: {url}")
                
                page = context.new_page()
                try:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(2000)
                    
                    cards = page.locator(".item-card")
                    card_count = cards.count()
                    
                    if card_count == 0:
                        logging.warning("No more items found.")
                        page.close()
                        break
                        
                    found_on_page = 0
                    for i in range(card_count):
                        card = cards.nth(i)
                        
                        # Detect likes
                        likes = 0
                        try:
                            # Try the specific selector found by browser subagent
                            likes_loc = card.locator(".item-card__likes, .js-wishlist-count, .shop__text--link50").first
                            if likes_loc.count() > 0:
                                likes_text = likes_loc.inner_text()
                                import re
                                nums = re.findall(r'[\d,]+', likes_text)
                                if nums:
                                    likes = int(nums[0].replace(',', ''))
                        except:
                            pass
                            
                        if likes < min_likes:
                            # In popular sort, if we hit items < 1000 likes consistently, we might be done
                            # But lets just skip for now
                            continue
                            
                        # Try multiple common link selectors
                        link_loc = card.locator(".item-card__title-anchor--multiline, .item-card__title a, a.item-card__title").first
                        if link_loc.count() == 0:
                            # Fallback: any link inside the card that looks like an item link
                            link_loc = card.locator("a[href*='/items/']").first
                            
                        if link_loc.count() > 0:
                            item_url = link_loc.get_attribute("href")
                            if item_url:
                                if not item_url.startswith("http"):
                                    from urllib.parse import urljoin
                                    item_url = urljoin(self.base_url, item_url)
                                
                                # FORCE re-processing for the targeted crawl to ensure we get 'likes' metadata and images
                                all_target_urls.append((item_url, likes))
                                found_on_page += 1
                                logging.info(f"  - Found: {item_url} ({likes} likes)")
                        else:
                            logging.warning(f"  - Could not find link for card {i}")
                    
                    logging.info(f"Page {page_num}: Found {found_on_page} items with >= {min_likes} likes.")
                    page.close()
                    
                    if found_on_page == 0 and page_num > 1:
                        # If we find nothing on a page (sorted by popularity), we might have reached the end of highly liked items
                        logging.info("Reached end of 1000+ likes items (Popularity sorted).")
                        # break # Optional: Uncomment if we are confident in the sort
                except Exception as e:
                    logging.error(f"Error on search page {page_num}: {e}")
                    if not page.is_closed(): page.close()
            
            browser.close()
            
            # --- Phase 2: Process Each Item Individually ---
            logging.info(f"Total NEW items to process: {len(all_target_urls)}")
            
            for i, (item_url, likes) in enumerate(all_target_urls):
                logging.info(f"[{i+1}/{len(all_target_urls)}] Processing: {item_url} ({likes} likes)")
                try:
                    # We create a new browser/page for each item OR in small batches to avoid TargetClosed errors
                    # For simplicity, we'll use requests for the detail page as it's often more stable 
                    # unless it's heavily protected. Booth detail pages are usually searchable with BS4.
                    self.process_item(item_url, page=None, likes=likes)
                    self.processed_urls.add(item_url)
                    time.sleep(1) # Be polite
                except Exception as ex:
                    logging.error(f"Failed to process {item_url}: {ex}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = RobustBoothScraper(data_dir="data")
    target = "https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include&sort=popular"
    scraper.crawl_target_popular(target, min_likes=1000, max_pages=30) # Scrape up to 30 search pages
