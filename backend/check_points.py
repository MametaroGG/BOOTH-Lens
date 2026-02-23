import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLOUD_URL")
qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
collection_name = "booth_items"

try:
    count = client.count(collection_name)
    print(f"Total points in collection '{collection_name}': {count.count}")
except Exception as e:
    print(f"Error: {e}")
