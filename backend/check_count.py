import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLOUD_URL")
qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
collection_name = "booth_items"

try:
    collection_info = client.get_collection(collection_name)
    print(f"Collection Name: {collection_name}")
    print(f"Points Count: {collection_info.points_count}")
    print(f"Status: {collection_info.status}")
except Exception as e:
    print(f"Error: {e}")
