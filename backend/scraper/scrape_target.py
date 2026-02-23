import logging
import os
from booth_scraper import BoothScraper

# Configure logging to be more visible for this specific run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_targeted_scrape():
    # Initialize scraper relative to this script's location
    # Assumes we are in backend/scraper/
    scraper = BoothScraper(data_dir="data")
    
    target_url = "https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?tags%5B%5D=VRChat&adult=include&sort=popular"
    
    logging.info(f"--- Starting TARGETED scrape for: {target_url} ---")
    logging.info("Criteria: Likes > 1000, Category: 3D Clothing, Tag: VRChat")
    
    # We want "all" items, but let's start with a high limit like 300 
    # since we are only taking ones with > 1000 likes.
    # The default sort is popular, so 1000+ likes items will be at the front.
    scraper.crawl_category(target_url, max_items=300)
    
    logging.info("--- Targeted scrape completed ---")

if __name__ == "__main__":
    run_targeted_scrape()
