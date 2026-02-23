import json
import os

path = 'backend/scraper/data/metadata.jsonl'
if not os.path.exists(path):
    print("Metadata file not found.")
    exit(1)

total = 0
likes_gt_1000 = 0
with_images = 0
no_images = 0

with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            item = json.loads(line)
            total += 1
            if item.get("likes", 0) >= 1000:
                likes_gt_1000 += 1
            if item.get("images") and len(item.get("images")) > 0:
                with_images += 1
            else:
                no_images += 1
        except:
            continue

print(f"Total items: {total}")
print(f"Items with likes >= 1000: {likes_gt_1000}")
print(f"Items with images: {with_images}")
print(f"Items with no images: {no_images}")
