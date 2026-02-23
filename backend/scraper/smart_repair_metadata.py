import os
import json
import logging
from playwright.sync_api import sync_playwright
from booth_scraper import BoothScraper

logging.basicConfig(level=logging.INFO)

def smart_repair():
    scraper = BoothScraper()
    # Speed up: Monkeypatch image download to do nothing
    scraper.download_image = lambda *args, **kwargs: True
    
    metadata_path = 'data/metadata.jsonl'
    yolo_dir = 'data/yolo_dataset/images'
    
    if not os.path.exists(yolo_dir):
        logging.error(f"Directory {yolo_dir} not found.")
        return

    # 1. Build Title -> URL map from metadata.jsonl
    title_to_url = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    d = json.loads(line)
                    title_to_url[d['title']] = d['url']
                except: pass
    
    # 2. Get all target meta files
    meta_files = [f for f in os.listdir(yolo_dir) if f.endswith('_meta.txt')]
    logging.info(f"Found {len(meta_files)} meta files to repair in {yolo_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, meta_file in enumerate(meta_files):
            file_path = os.path.join(yolo_dir, meta_file)
            
            # Read current title
            current_title = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                line = f.readline()
                if line.startswith("Title: "):
                    current_title = line.replace("Title: ", "").strip()
            
            if not current_title:
                logging.warning(f"Could not read title from {meta_file}")
                continue
                
            url = title_to_url.get(current_title)
            if not url:
                logging.warning(f"URL not found for title: {current_title}")
                continue
                
            logging.info(f"[{i+1}/{len(meta_files)}] Updating {meta_file} for: {current_title}")
            
            try:
                # Re-scrape with fixed logic
                scraper.process_item(url, page=page)
                
                # Get the latest data from metadata.jsonl
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    good_data = json.loads(lines[-1])
                
                # Update the file IN-PLACE
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {good_data.get('title')}\n")
                    f.write(f"Tags: {', '.join(good_data.get('tags', []))}\n")
                    f.write(f"Desc: {good_data.get('description', '')[:500]}...\n")
                
                logging.info(f"  Successfully updated {meta_file}")
                
            except Exception as e:
                logging.error(f"  Failed to update {meta_file}: {e}")

        browser.close()

if __name__ == "__main__":
    smart_repair()
