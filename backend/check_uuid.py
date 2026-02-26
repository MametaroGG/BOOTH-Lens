import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import hashlib
import uuid

def get_stable_uuid(text: str):
    hash_obj = hashlib.md5(text.encode('utf-8'))
    return str(uuid.UUID(hash_obj.hexdigest()))

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLOUD_URL")
qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
collection_name = "booth_items"

img_url = "https://pub-58c88b0828f94fbf9796d64362584259.r2.dev/data/raw_images/7930714_0.webp"
point_id = get_stable_uuid(img_url)

print(f"Checking Qdrant for point ID: {point_id} (generated from {img_url})")

try:
    records = client.retrieve(
        collection_name=collection_name,
        ids=[point_id],
        with_payload=True,
        with_vectors=False
    )
    
    print(f"Found {len(records)} records")
    for r in records:
        print(f"ID: {r.id}, Payload Title: {r.payload.get('title')}")
except Exception as e:
    print(f"Error checking Qdrant: {e}")
