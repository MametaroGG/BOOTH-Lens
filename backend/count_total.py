import json

metadata_path = "scraper/data/popular_items_full.jsonl"
total_items = 0
total_images = 0

with open(metadata_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            total_items += 1
            total_images += len(data.get("images", []))
        except:
            pass

print(f"Total Items: {total_items}")
print(f"Total Images: {total_images}")
