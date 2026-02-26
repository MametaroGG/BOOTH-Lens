import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLOUD_URL")
qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
collection_name = "booth_items"

booth_url = "https://booth.pm/ja/items/7930714"
print(f"Checking Qdrant for boothUrl: {booth_url}")

try:
    records, next_page = client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="boothUrl",
                    match=MatchValue(value=booth_url)
                )
            ]
        ),
        limit=50,
        with_payload=True,
        with_vectors=False
    )

    print(f"Found {len(records)} records")
    for record in records:
        print(f"ID: {record.id}, Payload Title: {record.payload.get('title')}, Image URL: {record.payload.get('thumbnailUrl')}")
except Exception as e:
    print(f"Error checking Qdrant: {e}")

# If the above fails, let's just do a manual scan of the first few thousand to see
print("\n--- Manual Scan ---")
try:
    records, _ = client.scroll(collection_name=collection_name, limit=5000, with_payload=True, with_vectors=False)
    found = 0
    for r in records:
        if "7930714" in r.payload.get("boothUrl", ""):
            print(f"Found by manual scan: ID: {r.id}, Payload Title: {r.payload.get('title')}")
            found += 1
    if found == 0:
        print("Not found in the first 5000 items.")
except Exception as e:
    pass
