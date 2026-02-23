import os
import time
import json
import logging
import requests
import boto3
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import io
from PIL import Image
from playwright.sync_api import sync_playwright

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BoothScraper:
    def __init__(self, data_dir="data"):
        self.base_url = "https://booth.pm"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # Ensure data_dir is relative to CWD if not absolute
        self.data_dir = data_dir
        self.images_dir = os.path.join(data_dir, "raw_images")
        self.metadata_path = os.path.join(data_dir, "metadata.jsonl")
        self.processed_urls = self.load_processed_urls()

        # Cloudflare R2 Configuration
        self.r2_enabled = os.getenv("R2_ACCESS_KEY_ID") is not None
        logging.info(f"Checking R2 config: R2_ACCESS_KEY_ID exists? {self.r2_enabled}")
        
        if self.r2_enabled:
            self.r2_bucket = os.getenv("R2_BUCKET_NAME")
            self.r2_public_url = os.getenv("R2_PUBLIC_DEV_URL", "").rstrip("/")
            endpoint_url = os.getenv("R2_ENDPOINT_URL")
            logging.info(f"R2 Config: Bucket={self.r2_bucket}, Endpoint={endpoint_url}")
            
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
                    region_name='auto'
                )
                logging.info("Boto3 R2 client initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Boto3 R2 client: {e}")
                self.r2_enabled = False
        else:
            self.s3_client = None
            logging.info("Cloudflare R2 is DISABLED. Images will be saved locally.")
            os.makedirs(self.images_dir, exist_ok=True)

    def load_processed_urls(self):
        """Loads already processed URLs from the metadata file."""
        urls = set()
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if "url" in data:
                                urls.add(data["url"])
                        except:
                            continue
                logging.info(f"Loaded {len(urls)} already processed URLs.")
            except Exception as e:
                logging.error(f"Failed to load existing metadata: {e}")
        return urls
    
    def sleep_random(self, min_sec=3, max_sec=6):
        """Sleep for a random duration to avoid rate limiting."""
        duration = random.uniform(min_sec, max_sec)
        logging.info(f"Sleeping for {duration:.2f} seconds...")
        time.sleep(duration)

    def crawl_category(self, category_url, max_items=100):
        """Crawls a specific category URL for items using Playwright."""
        logging.info(f"Starting crawl for category: {category_url}")
        
        items_collected = 0
        page_num = 1
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=self.headers["User-Agent"])
            page = context.new_page()
            
            while items_collected < max_items:
                # Handle URLs that already have query parameters
                separator = "&" if "?" in category_url else "?"
                url = f"{category_url}{separator}page={page_num}"
                logging.info(f"Fetching page {page_num} with Playwright: {url}")
                
                try:
                    # Navigate and wait for content
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    # Extra wait for safety (some items load via JS)
                    page.wait_for_timeout(2000)
                    content = page.content()
                    
                    # Debug: Save HTML
                    with open("debug.html", "w", encoding="utf-8") as f:
                        f.write(content)

                    # Use Playwright's locator to find item cards for more dynamic interaction if needed
                    cards = page.locator("li.item-card")
                    card_count = cards.count()
                    
                    if card_count == 0:
                        logging.warning(f"No items found on page {page_num} or end of results.")
                        break
                    
                    logging.info(f"Found {card_count} items on page {page_num}")
                    
                    for i in range(card_count):
                        if items_collected >= max_items:
                            break
                        
                        card = cards.nth(i)
                        
                        # --- Filter by Likes > 1000 ---
                        likes = 0
                        try:
                            # Wait a bit for the card's dynamic content to settle if needed
                            # card.scroll_into_view_if_needed()
                            
                            # 1. Broadly get all text from the card
                            card_full_text = card.inner_text()
                            
                            # Log all numbers found in the card for debugging
                            import re
                            all_nums = re.findall(r'[\d,]+', card_full_text)
                            logging.info(f"Card {i} Raw Text: '{card_full_text.replace(os.linesep, ' ')}' | Numbers found: {all_nums}")
                            
                            # 2. Try to find the specific element first
                            likes_loc = card.locator(".item-card__likes, .js-wishlist-count, .icon-wishlist, .icon-heart, .count, .shop__text--link50").first
                            likes_text = ""
                            if likes_loc.count() > 0:
                                likes_text = likes_loc.evaluate("e => e.innerText || e.textContent || (e.nextSibling ? e.nextSibling.textContent : '')")
                                logging.info(f"Card {i} Specific Locator Text: '{likes_text}'")
                            
                            # Extract numbers from the specific element first
                            nums = re.findall(r'[\d,]+', likes_text)
                            if nums:
                                likes = int(nums[0].replace(',', ''))
                            
                            # 3. Fallback: If still 0, use the last number in the card (heuristic)
                            if likes == 0 and all_nums:
                                # Often the last number is the likes, or the one before it is the price.
                                # Let's try to be smart - the largest number is probably the price, 
                                # the next significant one might be likes.
                                # But items under 1000 yen might confuse this.
                                clean_nums = [int(n.replace(',', '')) for n in all_nums]
                                if len(clean_nums) > 1:
                                    # Pick the smallest non-zero number (as a safe heuristic for likes vs price)
                                    likes = min([n for n in clean_nums if n > 0])
                                else:
                                    likes = clean_nums[0]

                            logging.info(f"Card {i} FINAL Like Detection: {likes}")
                        except Exception as le:
                            logging.warning(f"Error detecting likes for card {i}: {le}")

                        link_loc = card.locator("div.item-card__title a")
                        title = link_loc.inner_text() if link_loc.count() > 0 else "Unknown"
                        
                        if likes < 1000:
                            logging.info(f"Skipping: {likes} likes (Title: {title[:25]}...)")
                            continue
                            
                        item_url = link_loc.get_attribute("href")
                        if not item_url:
                            continue
                            
                        if not item_url.startswith("http"):
                             item_url = urljoin(self.base_url, item_url)

                        if item_url in self.processed_urls:
                            logging.info(f"Skipping: Already processed {item_url}")
                            continue

                        logging.info(f"Processing NEW item: {item_url} with {likes} likes")
                        self.process_item(item_url, page=page, likes=likes)
                        self.processed_urls.add(item_url)
                        items_collected += 1
                        self.sleep_random(1, 2)
                    
                    page_num += 1
                    self.sleep_random()

                except Exception as e:
                    logging.error(f"Error on page {page_num}: {e}")
                    self.sleep_random(5, 10)
            
            browser.close()

    def process_item(self, item_url, page=None, likes=0):
        """Extracts metadata and downloads image from an item page."""
        logging.info(f"Processing item: {item_url}")
        try:
            content = ""
            if page:
                try:
                    # Navigate to item detail page
                    page.goto(item_url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1000) # Small wait for dynamic content
                    content = page.content()
                except Exception as pg_e:
                    logging.error(f"Playwright detail page navigation failed: {pg_e}")
                    resp = requests.get(item_url, headers=self.headers, timeout=10)
                    content = resp.text
            else:
                resp = requests.get(item_url, headers=self.headers, timeout=10)
                if resp.status_code != 200:
                    logging.warning(f"Skipping item {item_url}: Status {resp.status_code}")
                    return
                content = resp.text

            # Debug: Save Item HTML
            with open("debug_item.html", "w", encoding="utf-8") as f:
                f.write(content)

            soup = BeautifulSoup(content, "lxml")
            
            # Selectors for Item Detail Page (Based on debug_item.html)
            
            # Title: <h2 class="font-bold ...">
            title_tag = soup.select_one("h2.font-bold")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
            # Shop Name: Inside header, link with span
            shop_tag = soup.select_one("header a[href*='booth.pm'] span")
            shop_name = shop_tag.get_text(strip=True) if shop_tag else "Unknown"
            
            # Price: Robustly from data attribute in #items div or JSON-LD
            items_div = soup.select_one("div#items")
            raw_price = items_div["data-product-price"] if items_div and items_div.has_attr("data-product-price") else "0"
            
            # Detect variations from JSON-LD
            has_variations = False
            try:
                script_tag = soup.find("script", type="application/ld+json")
                if script_tag:
                    ld_data = json.loads(script_tag.string)
                    offers = ld_data.get("offers", {})
                    if offers.get("@type") == "AggregateOffer":
                        low = float(offers.get("lowPrice", 0))
                        high = float(offers.get("highPrice", 0))
                        if high > low:
                            has_variations = True
            except Exception as ld_e:
                logging.debug(f"JSON-LD price check failed: {ld_e}")

            price = f"¥ {raw_price}"
            if has_variations:
                price += "～"

            # Main Images: <img class="market-item-detail-item-image" ...>
            image_tags = soup.select("img.market-item-detail-item-image")
            image_paths = []
            
            if image_tags:
                for i, img in enumerate(image_tags):
                    image_url = img.get("data-origin") or img.get("src")
                    if not image_url:
                        continue
                        
                    # Filename: itemID_index.jpg
                    image_filename = f"{os.path.basename(item_url).split('_')[0]}_{i}.jpg"
                    # Simple sanitization
                    image_filename = "".join([c for c in image_filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
                    
                    save_path = os.path.join(self.images_dir, image_filename)
                    if self.download_image(image_url, save_path, is_r2=self.r2_enabled):
                        if self.r2_enabled:
                            # For R2, store the full public URL or a format vector_db can recognize as a URL
                            # location (save_path) is used as the key in R2
                            r2_url = f"{self.r2_public_url}/{save_path.replace(os.sep, '/')}"
                            image_paths.append(r2_url)
                        else:
                            image_paths.append(save_path)
                    
                    # Be polite, don't hammer the server for images of the same item too fast
                    time.sleep(0.5)
            else:
                logging.warning(f"No images found for {item_url}")

            # --- New Feature: AI Training Data Extraction ---
            text_content = (title + " " + " ".join([p.text for p in soup.find_all(['p', 'div'])])).lower()
            
            # Description
            # Create a dedicated soup for text extraction to avoid sidebar interference
            desc_soup = BeautifulSoup(content, "lxml")
            for sidebar in desc_soup.select("aside, .sidebar, .shop-info, .gift-button, .cart-button, [class*='sidebar'], .market-item-detail-sidebar"):
                sidebar.decompose()

            desc_tag = desc_soup.select_one("div.market-item-detail-description") or \
                       desc_soup.select_one("div.js-market-item-detail-description") or \
                       desc_soup.select_one("div.typography-16") or \
                       desc_soup.select_one("div.markdown-body")
            
            description = ""
            if desc_tag:
                description = desc_tag.get_text(separator='\n', strip=True)
                # Filter out sidebar-like text if detected
                if "ギフト" in description and len(description) < 100:
                    description = ""
            
            if not description:
                # Fallback to general content area
                for div in desc_soup.find_all("div", class_="typography-16"):
                    if len(div.text) > 100:
                        description = div.get_text(separator='\n', strip=True)
                        break
            
            # Tags: Find the heading "タグ" (Tags) and get links in that section
            tags = []
            # More flexible heading search
            tag_heading = soup.find(["h1", "h2", "h3"], string=lambda x: x and "タグ" in x)
            if not tag_heading:
                # If exact string search fails, try searching by text content
                for h in soup.find_all(["h2", "h3"]):
                    if "タグ" in h.get_text():
                        tag_heading = h
                        break
            
            if tag_heading:
                # Search for tags in the container following the heading
                tag_container = tag_heading.find_next("div")
                if tag_container:
                    tag_elements = tag_container.select("a[href*='/search/'], a[href*='tags%5B%5D=']")
                    for t in tag_elements:
                        tag_text = t.get_text(strip=True)
                        if not tag_text:
                            img = t.find("img")
                            if img: tag_text = img.get("alt", "").strip()
                        if tag_text and tag_text not in tags and "で検索" not in tag_text:
                            tags.append(tag_text)
            
            # Fallback for tags if the heading method fails
            if not tags:
                tag_elements = soup.select("a.icon-tag-base, a.icon-tag, li.item-tag a, a[href*='/search/'], a[href*='tags%5B%5D=']")
                for t in tag_elements:
                    txt = t.get_text(strip=True)
                    if not txt:
                        img = t.find("img")
                        if img: txt = img.get("alt", "").strip()
                    if txt and txt not in tags and "検索" not in txt:
                        tags.append(txt)
            
            # Variation Names (for precise Avatar matching in training)
            variation_elements = soup.select("div.variation-name") or soup.select("div[class*='variation-name']") 
            variation_names = list(set([v.get_text(strip=True) for v in variation_elements if v.get_text(strip=True)]))

            # 1. Category extraction
            category = "Unknown"
            breadcrumb = soup.select("nav[aria-label=breadcrumb] ol li a")
            if breadcrumb and len(breadcrumb) > 1:
               category = breadcrumb[-1].get_text(strip=True)
            elif "3d" in text_content or "vrc" in text_content or "avatar" in text_content:
               category = "3D Asset"

            # 2. Avatar extraction (Common VRChat Avatars)
            target_avatars = [
                "マヌカ", "桔梗", "セレスティア", "萌", "森羅", "瑞希", "ライム", "シフォン", 
                "ウルフェリア", "薄荷", "京狐", "狛乃", "水瀬", "ユリスフィア", "エミスティア", 
                "杏里", "彼方", "アル", "サクヤ", "ナユ", "真冬"
            ]
            found_avatars = []
            
            # Check variation names directly since they often contain the avatar name
            for avatar in target_avatars:
                if any(avatar in v_name for v_name in variation_names) or avatar in title:
                    found_avatars.append(avatar)
            
            # If still empty, check full text
            if not found_avatars:
                for avatar in target_avatars:
                    if avatar in text_content:
                        found_avatars.append(avatar)
                        
            # 3. Color extraction
            target_colors = ["black", "white", "red", "blue", "green", "yellow", "pink", "purple", "brown", "gray", "黒", "白", "赤", "青", "緑", "黄", "ピンク", "紫", "茶", "グレー", "水色", "モノクロ"]
            found_colors = []
            for color in target_colors:
                if color in title.lower() or any(color in v_name.lower() for v_name in variation_names):
                    found_colors.append(color)

            item_data = {
                "url": item_url,
                "title": title,
                "shop": shop_name,
                "price": price,
                "images": image_paths,
                "category": category,
                "likes": likes,
                "avatars": list(set(found_avatars)),
                "colors": list(set(found_colors)),
                "description": description,
                "tags": tags,
                "variation_names": variation_names
            }

            self.save_metadata(item_data)
            logging.info(f"Saved: {title} ({price}) - {len(image_paths)} images")

        except Exception as e:
            logging.error(f"Error processing item {item_url}: {e}")
            self.sleep_random(5, 10)   

    def save_metadata(self, item_data):
        """Appends item metadata to the JSONL file."""
        try:
            with open(self.metadata_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(item_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Failed to save metadata: {e}")

    def download_image(self, url, location, is_r2=False):
        """Downloads an image, resizes it to a max of 800x800, and saves to local disk OR R2."""
        try:
            # Check existence first if local
            if not is_r2 and os.path.exists(location):
                return True
                
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # --- Resize and compress image using PIL ---
                try:
                    img = Image.open(io.BytesIO(response.content))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    # Resize to max 800x800 (maintains aspect ratio)
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=85)
                    img_bytes = img_byte_arr.getvalue()
                except Exception as img_e:
                    logging.warning(f"Failed to resize image {url}, using original: {img_e}")
                    img_bytes = response.content
                # ---------------------------------------------

                if is_r2:
                    try:
                        # Upload byte stream directly to R2
                        self.s3_client.put_object(
                            Bucket=self.r2_bucket,
                            Key=location.replace(os.sep, '/'), # Ensure forward slashes for R2 keys
                            Body=img_bytes,
                            ContentType='image/jpeg'
                        )
                        logging.info(f"Successfully uploaded to R2: {location}")
                    except Exception as r2_e:
                        logging.error(f"R2 Upload Error for {location}: {r2_e}")
                        # Fallback: keep on local disk if upload fails
                        with open(location, 'wb') as f:
                            f.write(img_bytes)
                        return False
                else:
                    # Save to local disk
                    with open(location, 'wb') as f:
                        f.write(img_bytes)
                return True
            else:
                logging.warning(f"Failed to download image {url}: Status {response.status_code}")
        except Exception as e:
            logging.error(f"download_image error {url}: {e}")
        return False

if __name__ == "__main__":
    # If running from backend root, save to scraper/data
    if os.path.exists("scraper"):
        scraper = BoothScraper(data_dir="scraper/data")
    else:
        scraper = BoothScraper()
    
    target_categories = [
        "https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85?type=digital&tags%5B%5D=VRChat&adult=include",
    ]

    for i, category_url in enumerate(target_categories):
        logging.info(f"--- Starting crawl for Category {i+1}/{len(target_categories)}: {category_url} ---")
        scraper.crawl_category(category_url, max_items=500) # Increased max_items as filtering by likes > 1000 will discard many
        scraper.sleep_random(10, 20) # Long pause between categories
