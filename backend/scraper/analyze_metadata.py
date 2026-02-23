import json
import os

def analyze():
    metadata_path = 'data/metadata.jsonl'
    if not os.path.exists(metadata_path):
        print("Metadata not found.")
        return

    def get_likes(i):
        l = i.get('likes', 0)
        if isinstance(l, int): return l
        if not l: return 0
        try:
            return int(str(l).replace(',', '').replace('+', ''))
        except:
            return 0

    stats = {
        'total': 0,
        'categories': {},
        'likes_ge_1000': 0,
        'costume_and_likes': 0,
        'vrc_tag_and_likes': 0
    }

    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                stats['total'] += 1
                cat = item.get('category', 'None')
                stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
                
                likes = get_likes(item)
                tags = item.get('tags', [])
                
                is_high_like = likes >= 1000
                is_costume = cat == '3D衣装'
                is_vrc = 'VRChat' in tags
                
                if is_high_like: stats['likes_ge_1000'] += 1
                if is_costume and is_high_like: stats['costume_and_likes'] += 1
                if is_vrc and is_high_like: stats['vrc_tag_and_likes'] += 1
            except: pass

    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    analyze()
