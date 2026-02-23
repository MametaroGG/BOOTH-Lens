import json
import logging
import time
from booth_scraper import BoothScraper

def process_target_batch():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    with open('target_urls.json', 'r', encoding='utf-8') as f:
        urls = json.load(f)
    
    scraper = BoothScraper(data_dir="data")
    logging.info(f"Starting batch process for {len(urls)} URLs...")
    
    for i, url in enumerate(urls):
        logging.info(f"[{i+1}/{len(urls)}] Processing: {url}")
        try:
            # We use Requests-based scraping for detail pages for stability
            scraper.process_item(url, page=None, likes=0) # Likes will be re-detected if possible or just left 0
            time.sleep(1.5) # Be polite to Booth
        except Exception as e:
            logging.error(f"Failed to process {url}: {e}")

if __name__ == "__main__":
    process_target_batch()
