import asyncio
import os
import uuid
from prisma import Prisma
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from PIL import Image
import requests
import io
import torch
from transformers import CLIPProcessor, CLIPModel

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "booth_items"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Sample Data
SAMPLE_ITEMS = [
    {
        "title": "幽狐族の娘「桔梗」専用【3D衣装モデル】Royal Dress",
        "price": 2000,
        "shopName": "Mame-Shop",
        "boothUrl": "https://booth.pm/ja/items/1234567",
        "thumbnailUrl": "https://images.booth.pm/c/cc495213-9799-4d69-90bc-2c70034a7429/18a29a43-6c7e-4b72-9e8d-8a5840d892d1/thumbnail_600x600.png"
    },
    {
        "title": "【萌専用】ゴスロリメイド服",
        "price": 1800,
        "shopName": "Alice-Atelier",
        "boothUrl": "https://booth.pm/ja/items/2345678",
        "thumbnailUrl": "https://images.booth.pm/c/7951d3b4-4b52-4e8a-8a58-8a8b1c1d1e1f/1a2b3c4d-5e6f-7a8b-9c0d-1e1f2a3b4c5d/thumbnail_600x600.png"
    }
]

async def seed():
    prisma = Prisma()
    await prisma.connect()
    
    # Local mode: no server needed
    qdrant = QdrantClient(path="qdrant_local")
    
    # Initialize CLIP model for embedding generation
    print("Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    # Ensure Qdrant collection
    print(f"Ensuring Qdrant collection: {COLLECTION_NAME}")
    collections = qdrant.get_collections()
    if not any(c.name == COLLECTION_NAME for c in collections.collections):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )

    for item in SAMPLE_ITEMS:
        print(f"Processing: {item['title']}")
        
        # 1. Download image and generate embedding
        try:
            response = requests.get(item['thumbnailUrl'], headers=HEADERS, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            inputs = processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            
            # Robustly handle different CLIP output formats
            if hasattr(outputs, "image_embeds"):
                features = outputs.image_embeds
            else:
                features = outputs
            
            # Normalize and convert to list
            features = features / features.norm(p=2, dim=-1, keepdim=True)
            vector = features.cpu().numpy()[0].tolist()
            
            # 2. Save to PostgreSQL via Prisma
            # First, ensure shop exists
            shop = await prisma.shop.upsert(
                where={'url': f"https://{item['shopName'].lower()}.booth.pm"},
                data={
                    'create': {
                        'name': item['shopName'],
                        'url': f"https://{item['shopName'].lower()}.booth.pm"
                    },
                    'update': {'name': item['shopName']}
                }
            )
            
            # Create product
            product = await prisma.product.create(
                data={
                    'shopId': shop.id,
                    'title': item['title'],
                    'price': item['price'],
                    'thumbnailUrl': item['thumbnailUrl']
                }
            )
            
            # 3. Save to Qdrant
            vector_id = str(uuid.uuid4())
            qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=vector_id,
                        vector=vector,
                        payload={
                            "productId": product.id,
                            "title": item['title'],
                            "price": item['price'],
                            "shopName": item['shopName'],
                            "boothUrl": item['boothUrl'],
                            "thumbnailUrl": item['thumbnailUrl']
                        }
                    )
                ]
            )
            
            # Link vectorId back to DB image if we were storing images specifically
            # For MVP, we use the vector payload for display
            
            print(f"Successfully seeded: {item['title']}")
            
        except Exception as e:
            print(f"Error seeding {item['title']}: {e}")

    await prisma.disconnect()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
