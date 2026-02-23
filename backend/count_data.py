import json
from collections import Counter
import os

metadata_path = "scraper/data/metadata.jsonl"
categories = {
    "3Dキャラクター": "3D Characters",
    "3D衣装": "3D Costumes",
    "3D装飾品": "3D Accessories",
    "3D小道具": "3D Props",
    "3Dテクスチャ": "3D Textures"
}

category_counts = Counter()
total = 0

if os.path.exists(metadata_path):
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                # Naive category detection based on URL or title could be hard if not saved.
                # However, the scraper saves items sequentially.
                # We can try to infer from the 'url' if it contains the category, but booth item URLs are just ids.
                # We might not be able to know the category easily from metadata alone unless we fetch it.
                # But wait, we can't easily distinguish.
                
                # Actually, let's just count total for now.
                total += 1
            except:
                pass

print(f"Total items: {total}")
# Since we can't easily know the category of existing items without re-fetching, 
# I will explain the logic based on the code:
# The code collects 200 NEW items per category run.
