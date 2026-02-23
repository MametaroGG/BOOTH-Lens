import logging
import asyncio
from playwright.sync_api import sync_playwright
from booth_scraper import BoothScraper

logging.basicConfig(level=logging.INFO)

def test_full_process():
    scraper = BoothScraper()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Item with many tags and clear description
        url = 'https://booth.pm/ja/items/4294026'
        scraper.process_item(url, page=page)
        browser.close()

    # Verify the last line in metadata.jsonl
    import json
    with open('data/metadata.jsonl', 'r', encoding='utf-8') as f:
        line = f.readlines()[-1]
        data = json.loads(line)
        print("\n--- TEST RESULT ---")
        print(f"Title: {data.get('title')}")
        print(f"Tags: {data.get('tags')}")
        print(f"Desc (len): {len(data.get('description', ''))}")
        if data.get('tags'):
            print("SUCCESS: Tags found!")
        else:
            print("FAILURE: Tags still empty.")

if __name__ == "__main__":
    test_full_process()
