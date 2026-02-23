import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLOUD_URL")
qdrant_api_key = os.getenv("QDRANT_CLOUD_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
collection_name = "booth_items"

fields = ["shopName", "category", "avatars", "colors"]

for field in fields:
    print(f"Creating index for {field}...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
            wait=True
        )
        print(f"Successfully created index for {field}.")
    except Exception as e:
        print(f"Failed to create index for {field}: {e}")

print("Done.")
