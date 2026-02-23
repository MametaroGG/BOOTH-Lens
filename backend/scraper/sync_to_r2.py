import os
import json
import logging
import time
from tqdm import tqdm
from booth_scraper import BoothScraper
from PIL import Image
import io

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync_r2_final.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def sync_to_r2():
    scraper = BoothScraper()
    if not scraper.r2_enabled:
        logging.error("R2 is not enabled in .env. Please check your configuration.")
        return

    metadata_path = os.path.join("data", "metadata.jsonl")
    temp_metadata_path = os.path.join("data", "metadata_synced_final.jsonl")
    
    if not os.path.exists(metadata_path):
        logging.error(f"Metadata file not found: {metadata_path}")
        return

    # Count lines for progress bar
    total_items = 0
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for _ in f: total_items += 1

    logging.info(f"Starting FINAL synchronization of {total_items} items to R2 with FORCED RESIZING...")

    with open(metadata_path, 'r', encoding='utf-8') as f_in, \
         open(temp_metadata_path, 'w', encoding='utf-8') as f_out:
        
        for line in tqdm(f_in, total=total_items, desc="Syncing items"):
            try:
                item = json.loads(line.strip())
                updated_images = []
                
                # Each item may have multiple images
                for img_val in item.get("images", []):
                    # 1. Determine local path even if it's already an R2 URL in metadata
                    local_path = None
                    if img_val.startswith("http") and scraper.r2_public_url in img_val:
                        # Reconstruct local path from R2 URL
                        # URL: https://.../data/raw_images/123_0.jpg -> PATH: data/raw_images/123_0.jpg
                        # We need to handle os.sep correctly
                        relative_path = img_val.replace(f"{scraper.r2_public_url}/", "").replace("/", os.sep)
                        local_path = relative_path
                    elif not img_val.startswith("http"):
                        local_path = img_val
                    
                    # 2. Process local file with compression
                    if local_path and os.path.exists(local_path):
                        try:
                            with Image.open(local_path) as img:
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                # Resize to max 800x800
                                img.set_format = 'JPEG'
                                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                                
                                img_byte_arr = io.BytesIO()
                                img.save(img_byte_arr, format='JPEG', quality=85)
                                compressed_bytes = img_byte_arr.getvalue()

                            r2_key = local_path.replace(os.sep, '/')
                            scraper.s3_client.put_object(
                                Bucket=scraper.r2_bucket,
                                Key=r2_key,
                                Body=compressed_bytes,
                                ContentType='image/jpeg'
                            )
                            r2_url = f"{scraper.r2_public_url}/{r2_key}"
                            updated_images.append(r2_url)
                            # logging.info(f"OK: {local_path} ({len(compressed_bytes)/1024:.1f} KB)")
                        except Exception as e:
                            logging.error(f"Failed to process {local_path}: {e}")
                            updated_images.append(img_val)
                    else:
                        # If image is just a BOOTH URL (should not happen with existing metadata items usually)
                        # or if local file is missing, keep original
                        updated_images.append(img_val)

                # Update the item and save
                item["images"] = updated_images
                f_out.write(json.dumps(item, ensure_ascii=False) + "\n")
                
            except Exception as e:
                logging.error(f"Error processing item: {e}")
                f_out.write(line)

    # Replace old metadata with new one
    os.replace(temp_metadata_path, metadata_path)
    logging.info("FINAL Synchronization complete. All images resized and uploaded.")

if __name__ == "__main__":
    sync_to_r2()
