import os
import json
import time

METADATA_PATH = "data/metadata.jsonl"
IMAGES_DIR = "data/raw_images"

def count_progress():
    try:
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                item_count = sum(1 for line in f)
        else:
            item_count = 0

        if os.path.exists(IMAGES_DIR):
            image_count = len([name for name in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, name))])
        else:
            image_count = 0

        print(f"Items Collected: {item_count} / 1000 (Target)")
        print(f"Images Saved:   {image_count}")
        print("-" * 30)

    except Exception as e:
        print(f"Error checking progress: {e}")

if __name__ == "__main__":
    print("Monitoring Scraping Progress... (Ctrl+C to stop)")
    while True:
        count_progress()
        time.sleep(5)  # Update every 5 seconds
