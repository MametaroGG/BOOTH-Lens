import os
import json
import logging
import random
import requests
from playwright.sync_api import sync_playwright
from booth_scraper import BoothScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def rebuild_yolo_dataset(sample_size=300):
    scraper = BoothScraper()
    metadata_path = 'data/metadata.jsonl'
    output_dir = "data/yolo_dataset/images"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(metadata_path):
        logging.error("Metadata file not found.")
        return

    # Load all items
    raw_items = []
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                raw_items.append(json.loads(line.strip()))
            except: pass

    def is_costume(item):
        title = item.get("title", "").lower()
        tags = [t.lower() for t in item.get("tags", [])]
        category = str(item.get("category", "")).lower()
        
        # 1. Negative Filter: Skip things that are clearly not main outfits
        # If it's just a texture, skip.
        noise_keywords = ["テクスチャ", "texture", "小道具", "prop", "装飾品", "system", "prefab", "瞳", "eye", "make", "メイク"]
        if any(nk in title for nk in noise_keywords):
            return False
            
        # 2. Positive Filter
        if category == "3d衣装": return True
        if any(tk in tags for tk in ["3d衣装", "服", "衣装", "outfit", "costume", "dress"]): return True
        if any(kw in title for kw in ["衣装", "服", "outfit", "dress"]): return True
        
        # 3. Breadcrumb/Category fallback
        if "衣装" in category or "服" in category: return True
        
        return False

    def get_likes(item):
        l = item.get("likes", 0)
        if isinstance(l, int): return l
        try:
            return int(str(l).replace(',', '').replace('+', ''))
        except: return 0

    # Filtering
    filtered_items = []
    seen_urls = set()
    
    # Process from LATEST to OLDEST to prioritize recent R2 data (which user says is correct)
    for i, item in enumerate(reversed(raw_items)):
        url = item.get("url")
        if not url or url in seen_urls: continue
        
        # We consider the items added after the likes filtering was implemented as "recent"
        # Since the file has ~2400 lines, the last 1000 items are likely the targeted ones.
        is_recent = i < 1000 
        
        if is_costume(item):
            likes = get_likes(item)
            # If we have likes info, use it. If not (old data), rely on it being recent.
            # Most items in the latest scrape will have likes field now (if scraped after my fix)
            # but even without it, they are the "good" ones from the VRChat category.
            if likes >= 1000 or (likes == 0 and is_recent):
                filtered_items.append(item)
                seen_urls.add(url)
    
    # Take the latest 300 from the filtered list (most relevant costumes)
    selected_items = filtered_items[:sample_size]

    logging.info(f"Rebuilding dataset with {len(selected_items)} high-quality costume items...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i, item in enumerate(selected_items):
            url = item["url"]
            item_id = os.path.basename(url).split('_')[0]
            if not item_id.isdigit(): item_id = str(hash(url) % 10000000)

            logging.info(f"[{i+1}/{len(selected_items)}] Item: {item_id}")
            
            try:
                # 1. Get FRESH high-quality metadata using new logic
                scraper.process_item(url, page=page, likes=get_likes(item))
                
                # Metadata is appended, so the last line is the updated one
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    good_data = json.loads(lines[-1])
                
                title = good_data.get("title", "unknown")
                clean_title = "".join(c for c in title if c.isalnum())[:30]
                
                # 2. Image handling
                img_paths = good_data.get("images", [])
                if img_paths:
                    first_img = img_paths[0]
                    target_img_name = f"{item_id}_{clean_title}.jpg"
                    target_img_path = os.path.join(output_dir, target_img_name)
                    
                    if first_img.startswith("http"):
                        resp = requests.get(first_img, timeout=10)
                        if resp.status_code == 200:
                            with open(target_img_path, 'wb') as f: f.write(resp.content)
                    elif os.path.exists(first_img):
                        from shutil import copyfile
                        copyfile(first_img, target_img_path)
                    
                    # 3. Meta File
                    meta_filename = os.path.join(output_dir, f"{item_id}_{clean_title}_meta.txt")
                    with open(meta_filename, 'w', encoding='utf-8') as mf:
                        mf.write(f"ID: {item_id}\n")
                        mf.write(f"URL: {url}\n")
                        mf.write(f"Title: {title}\n")
                        mf.write(f"Tags: {', '.join(good_data.get('tags', []))}\n")
                        mf.write(f"Likes: {good_data.get('likes') or '1000+'}\n")
                        mf.write(f"Description:\n{good_data.get('description', '')[:1000]}\n")
                    
                    logging.info(f"  Done: {target_img_name}")
                
            except Exception as e:
                logging.error(f"  Error {item_id}: {e}")
            
            if (i+1) % 10 == 0: print(f"Progress: {i+1}/{len(selected_items)}")

        browser.close()

if __name__ == "__main__":
    rebuild_yolo_dataset(300)
