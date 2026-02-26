import os
import json
import asyncio
import logging
import hashlib
import uuid
import requests
import io
import torch
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, PayloadSchemaType
from transformers import CLIPModel, CLIPImageProcessor
from PIL import Image
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_stable_uuid(text: str):
    hash_obj = hashlib.md5(text.encode('utf-8'))
    return str(uuid.UUID(hash_obj.hexdigest()))

async def main():
    load_dotenv()
    qdrant_url = os.getenv("QDRANT_CLOUD_URL")
    qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=30.0)
    collection_name = "booth_items"
    
    # 1. Load CLIP Model
    logging.info("Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-base-patch32")
    logging.info(f"Loaded CLIP on {device}.")

    def get_embedding(img: Image.Image):
        inputs = processor(images=[img], return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            
        if isinstance(outputs, torch.Tensor):
            features = outputs
        elif hasattr(outputs, "image_embeds"):
            features = outputs.image_embeds
        elif hasattr(outputs, "pooler_output"):
            features = outputs.pooler_output
        elif isinstance(outputs, (list, tuple)):
            features = outputs[0]
        else:
            try:
                features = outputs[0]
            except:
                features = outputs
                
        features = features / features.norm(p=2, dim=-1, keepdim=True)
        return features.cpu().numpy()[0].tolist()

    # 2. Get existing UUIDs from Qdrant
    logging.info("Fetching existing IDs from Qdrant to skip...")
    existing_ids = set()
    next_page = None
    while True:
        records, next_page = client.scroll(
            collection_name=collection_name, 
            limit=5000, 
            with_payload=False, 
            with_vectors=False,
            offset=next_page
        )
        for r in records:
            existing_ids.add(r.id)
        logging.info(f"Fetched {len(existing_ids)} IDs so far...")
        if next_page is None: break

    logging.info(f"Total existing IDs in Qdrant: {len(existing_ids)}")

    # 3. Process metadata
    metadata_path = "scraper/data/popular_items_full.jsonl"
    scraper_dir = "scraper"
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)
    
    added_count = 0
    skipped_count = 0
    error_count = 0

    logging.info(f"Processing {total_lines} items...")
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            if (line_idx + 1) % 100 == 0:
                logging.info(f"Progress: {line_idx + 1}/{total_lines} items | Added: {added_count} | Skipped: {skipped_count} | Errors: {error_count}")
            
            try:
                item = json.loads(line.strip())
                if not item.get("images") or not item.get("url"):
                    continue
                
                for img_rel_path in item["images"]:
                    point_id = get_stable_uuid(img_rel_path)
                    
                    if point_id in existing_ids:
                        skipped_count += 1
                        continue
                        
                    # Needs embedding and upsert
                    try:
                        is_url = img_rel_path.startswith("http://") or img_rel_path.startswith("https://")
                        
                        if is_url:
                            resp = requests.get(img_rel_path, timeout=10)
                            if resp.status_code != 200: continue
                            img_data = io.BytesIO(resp.content)
                            img = Image.open(img_data).convert("RGB")
                            thumbnail_url = img_rel_path
                        else:
                            img_path = os.path.join(scraper_dir, img_rel_path)
                            if not os.path.exists(img_path):
                                filename = os.path.basename(img_rel_path)
                                img_path = os.path.join(scraper_dir, "raw_images", filename)
                            if not os.path.exists(img_path):
                                continue
                            
                            img = Image.open(img_path).convert("RGB")
                            filename = os.path.basename(img_path)
                            thumbnail_url = f"/api/images/{filename}"

                        vector = get_embedding(img)
                        payload = {
                            "title": item.get("title", "Unknown"),
                            "price": item.get("price", "Unknown"),
                            "shopName": item.get("shop", "Unknown"),
                            "boothUrl": item.get("url", "#"),
                            "thumbnailUrl": thumbnail_url,
                            "category": item.get("category", "Unknown"),
                            "avatars": item.get("avatars", []),
                            "colors": item.get("colors", [])
                        }

                        client.upsert(
                            collection_name=collection_name,
                            points=[PointStruct(id=point_id, vector=vector, payload=payload)]
                        )
                        existing_ids.add(point_id)
                        added_count += 1
                    except Exception as ie:
                        logging.error(f"Error on image {img_rel_path}: {ie}")
                        error_count += 1
            except Exception as e:
                logging.error(f"Error reading item line: {e}")

    logging.info(f"FINISHED. Total added: {added_count}, Skipped: {skipped_count}, Errors: {error_count}")

if __name__ == "__main__":
    asyncio.run(main())
