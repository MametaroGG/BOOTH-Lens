from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny
import os
import json
import asyncio
import logging
import hashlib
import uuid
import requests
import io
from typing import List, Optional
from PIL import Image
from .image_processor import ImageProcessor

# Global helper for Stable UUID
def get_stable_uuid(text: str):
    hash_obj = hashlib.md5(text.encode('utf-8'))
    return str(uuid.UUID(hash_obj.hexdigest()))

class VectorDBService:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        qdrant_url = os.getenv("QDRANT_CLOUD_URL")
        qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            logging.info("Connected to Qdrant Cloud.")
        else:
            self.client = QdrantClient(":memory:")
            logging.info("Connected to Local Qdrant (:memory:).")
            
        self.collection_name = "booth_items"
        self.vector_size = 512
        self.ensure_collection()
        
        # Indexing state
        self.indexing_status = {
            "total": 0,
            "current": 0,
            "is_complete": False,
            "last_item": None
        }
        
        # Determine paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.metadata_path = os.path.join(self.base_dir, "scraper", "data", "popular_items_full.jsonl")
        self.scraper_dir = os.path.join(self.base_dir, "scraper")

    def ensure_collection(self):
        from qdrant_client.http.models import PayloadSchemaType
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            # Create indices on initialization
            fields = ["shopName", "category", "avatars", "colors"]
            for field in fields:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field,
                        field_schema=PayloadSchemaType.KEYWORD,
                        wait=True
                    )
                except Exception as e:
                    logging.error(f"Failed to create index for {field}: {e}")

    async def seed_data(self, image_processor: ImageProcessor):
        logging.info("--- [VectorDB] Starting background seeding ---")
        if not os.path.exists(self.metadata_path):
            logging.warning(f"--- [VectorDB] No metadata.jsonl found at {self.metadata_path} ---")
            self.indexing_status["is_complete"] = True
            return

        processed_urls = set()
        
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                total_lines = sum(1 for _ in f)
            self.indexing_status["total"] = total_lines
            
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                count = 0
                img_count = 0
                for line in f:
                    try:
                        await asyncio.sleep(0) # Yield to event loop
                        item = json.loads(line.strip())
                        count += 1
                        self.indexing_status["current"] = count
                        
                        if not item.get("images") or not item.get("url"):
                            continue
                        
                        if item["url"] in processed_urls:
                            continue
                        processed_urls.add(item["url"])

                        for img_rel_path in item["images"]:
                            try:
                                await asyncio.sleep(0.01) # Throttle
                                
                                is_url = img_rel_path.startswith("http://") or img_rel_path.startswith("https://")
                                
                                if is_url:
                                    resp = requests.get(img_rel_path, timeout=10)
                                    if resp.status_code != 200:
                                        logging.warning(f"Failed to fetch remote image: {img_rel_path}")
                                        continue
                                    img_data = io.BytesIO(resp.content)
                                    img = Image.open(img_data).convert("RGB")
                                    filename = img_rel_path.split("/")[-1]
                                    thumbnail_url = img_rel_path
                                else:
                                    img_path = os.path.join(self.scraper_dir, img_rel_path)
                                    if not os.path.exists(img_path):
                                        filename = os.path.basename(img_rel_path)
                                        img_path = os.path.join(self.scraper_dir, "raw_images", filename)
                                    
                                    if not os.path.exists(img_path):
                                        continue

                                    img = Image.open(img_path).convert("RGB")
                                    filename = os.path.basename(img_path)
                                    thumbnail_url = f"/api/images/{filename}"

                                vector = image_processor.get_embedding(img)
                                
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
                                point_id = get_stable_uuid(img_rel_path)

                                self.client.upsert(
                                    collection_name=self.collection_name,
                                    points=[PointStruct(
                                        id=point_id,
                                        vector=vector,
                                        payload=payload
                                    )]
                                )
                                img_count += 1
                            except Exception as img_e:
                                logging.error(f"Error indexing image {img_rel_path}: {img_e}")
                        
                        self.indexing_status["last_item"] = f"{item.get('title')}"
                        
                    except Exception as e:
                        logging.error(f"line error: {e}")
                        
        except Exception as e:
            logging.error(f"Seeding fatal error: {e}")
        
        self.indexing_status["is_complete"] = True
        logging.info(f"--- [VectorDB] Seeding complete. {img_count} images indexed. ---")

    def search_similar(self, vector: List[float], limit: int = 10, offset: int = 0, excluded_shops: set = None, category: str = None, avatars: List[str] = None, colors: List[str] = None):
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue, MatchAny
        
        query_filter = None
        conditions = []
        must_not_conditions = []
        
        if excluded_shops:
            for excluded in excluded_shops:
                must_not_conditions.append(FieldCondition(key="shopName", match=MatchValue(value=excluded)))
                
        if category:
            conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))
            
        if avatars:
            for avatar in avatars:
                conditions.append(FieldCondition(key="avatars", match=MatchAny(any=[avatar])))
                
        if colors:
            for color in colors:
                conditions.append(FieldCondition(key="colors", match=MatchAny(any=[color])))
                
        if conditions or must_not_conditions:
            query_filter = Filter(must=conditions if conditions else None, must_not=must_not_conditions if must_not_conditions else None)

        # Retrieve more candidates for deduplication using query_points API
        raw_results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=query_filter,
            limit=limit * 3, 
            with_payload=True
        ).points

        # Deduplicate by unique boothUrl
        unique_results = []
        seen_urls = set()
        for hit in raw_results:
            url = hit.payload.get("boothUrl")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(hit)
            if len(unique_results) >= limit:
                break
        
        return unique_results
