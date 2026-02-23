import os
import json
import logging
import random
from playwright.sync_api import sync_playwright
from booth_scraper import BoothScraper

logging.basicConfig(level=logging.INFO)

def repair():
    scraper = BoothScraper()
    metadata_path = 'data/metadata.jsonl'
    
    if not os.path.exists(metadata_path):
        logging.error("No metadata.jsonl found.")
        return

    # Load all items and filter for those with high likes or specific conditions
    # For speed, we'll just take the LATEST 500 items and sample 300 from them
    # as they are more likely to be relevant.
    all_items = []
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                all_items.append(json.loads(line))
            except: pass
    
    # Take high-like items (re-evaluating from raw description if needed, or just items with >1000 likes recorded)
    # Actually, let's just take unique URLs
    urls = list(set([item['url'] for item in all_items if 'booth.pm' in item.get('url', '')]))
    
    # Sample 300
    if len(urls) > 300:
        sampled_urls = random.sample(urls, 300)
    else:
        sampled_urls = urls

    logging.info(f"Repairing metadata for {len(sampled_urls)} items using Playwright...")

    target_dir = 'data/yolo_dataset/images'
    os.makedirs(target_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # We need to temporarily monkeypatch the save_metadata to not mess up the main file
        # or just let it append, it's fine.
        
        for i, url in enumerate(sampled_urls):
            logging.info(f"[{i+1}/{len(sampled_urls)}] Fetching: {url}")
            try:
                # This will update debug_item.html and download images, and append to metadata.jsonl
                scraper.process_item(url, page=page)
                
                # After process_item, the latest line in metadata.jsonl is the good one
                # We extract it to create the _meta.txt for this item
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    good_data = json.loads(lines[-1])
                
                # Use the first image for the YOLO image (as per extract_yolo_train.py logic)
                # But extract_yolo_train.py already downloaded images.
                # Here we just want to ensure _meta.txt is updated.
                
                item_id = os.path.basename(url).split('_')[0]
                meta_filename = os.path.join(target_dir, f"{item_id}_meta.txt")
                
                with open(meta_filename, 'w', encoding='utf-8') as mf:
                    mf.write(f"Title: {good_data.get('title')}\n")
                    mf.write(f"Tags: {', '.join(good_data.get('tags', []))}\n")
                    mf.write(f"Desc: {good_data.get('description', '')[:500]}...\n")
                
            except Exception as e:
                logging.error(f"Failed to repair {url}: {e}")
            
            # Simple rate limit
            if i % 10 == 0:
                print(f"Progress: {i}/{len(sampled_urls)}")

        browser.close()

if __name__ == "__main__":
    repair()
