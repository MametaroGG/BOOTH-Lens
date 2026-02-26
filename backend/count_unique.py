import json

metadata_path = "scraper/data/popular_items_full.jsonl"
unique_images = set()
total_entries = 0

with open(metadata_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            images = data.get("images", [])
            for img in images:
                unique_images.add(img)
                total_entries += 1
        except:
            pass

print(f"Total Image Entries: {total_entries}")
print(f"Unique Image Paths: {len(unique_images)}")
