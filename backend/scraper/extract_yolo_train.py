import os
import json
import random
import requests
import logging
from tqdm import tqdm
from PIL import Image
import io

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_yolo_data(sample_size=200, output_dir="data/yolo_dataset"):
    metadata_path = os.path.join("data", "metadata.jsonl")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    if not os.path.exists(metadata_path):
        logging.error("Metadata file not found.")
        return

    # Load all items
    items = []
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            items.append(json.loads(line.strip()))

    # Filter: Costumes/Clothing only (if tags exist)
    # We prioritize high-like items as they represent high-quality assets
    target_items = [item for item in items if item.get("images")]
    
    # Shuffle and pick sample
    if len(target_items) > sample_size:
        selected_items = random.sample(target_items, sample_size)
    else:
        selected_items = target_items

    logging.info(f"Extracting {len(selected_items)} items for YOLO annotation...")

    for i, item in enumerate(tqdm(selected_items, desc="Downloading for YOLO")):
        title = item.get("title", f"item_{i}")
        # Take only the first image of each item for annotation to maximize variety
        image_url = item["images"][0]
        
        # Determine target filename
        ext = ".jpg" # Most are processed as JPEG 85
        filename = f"{i:04d}_{"".join(c for c in title if c.isalnum())[:30]}{ext}"
        target_path = os.path.join(images_dir, filename)

        try:
            if image_url.startswith("http"):
                resp = requests.get(image_url, timeout=10)
                if resp.status_code == 200:
                    with open(target_path, 'wb') as f:
                        f.write(resp.content)
            elif os.path.exists(image_url):
                # If it's a local path
                from shutil import copyfile
                copyfile(image_url, target_path)
            
            # Save a companion text file with metadata for reference during annotation
            # (Optional, but helps to know what we are looking at)
            with open(os.path.join(images_dir, f"{i:04d}_meta.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"Tags: {', '.join(item.get('tags', []))}\n")
                f.write(f"Desc: {item.get('description', '')[:200]}...\n")

        except Exception as e:
            logging.error(f"Failed to extract {title}: {e}")

    logging.info(f"Extraction complete. Images are in: {images_dir}")
    logging.info("Next Step: Use labelImg to annotate these images.")

if __name__ == "__main__":
    # Adjust sample_size as needed (e.g., 500 for a solid start)
    extract_yolo_data(sample_size=300)
