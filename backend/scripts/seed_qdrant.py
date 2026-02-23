import os
import uuid
import torch
from PIL import Image
import requests
import io
from transformers import CLIPProcessor, CLIPModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Configuration
COLLECTION_NAME = "booth_items"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Sample Data
SAMPLE_ITEMS = [
    {
        "title": "幽狐族の娘「桔梗」専用【3D衣装モデル】Royal Dress",
        "price": 2000,
        "shopName": "Mame-Shop",
        "boothUrl": "https://booth.pm/ja/items/1234567",
        "thumbnailUrl": "https://picsum.photos/seed/royal_dress/600/600"
    },
    {
        "title": "【萌専用】ゴスロリメイド服",
        "price": 1800,
        "shopName": "Alice-Atelier",
        "boothUrl": "https://booth.pm/ja/items/2345678",
        "thumbnailUrl": "https://picsum.photos/seed/maid_goth/600/600"
    }
]

def seed_qdrant_only():
    print("--- [DEBUG] Starting Simplified Seeding (Qdrant Only) ---")
    
    # Initialize CLIP
    print("Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    # Initialize Qdrant Local
    qdrant = QdrantClient(path="qdrant_local")
    
    # Ensure collection
    collections = qdrant.get_collections()
    if not any(c.name == COLLECTION_NAME for c in collections.collections):
        print(f"Creating collection: {COLLECTION_NAME}")
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )

    for item in SAMPLE_ITEMS:
        print(f"Processing: {item['title']}")
        try:
            # 1. Download image
            response = requests.get(item['thumbnailUrl'], headers=HEADERS, timeout=15)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # 2. Get embedding
            inputs = processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            
            # Extract tensor robustly
            if hasattr(outputs, "image_embeds"):
                features = outputs.image_embeds
            elif hasattr(outputs, "pooler_output"):
                features = outputs.pooler_output
            else:
                features = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
            
            features = features / features.norm(p=2, dim=-1, keepdim=True)
            vector = features.cpu().numpy()[0].tolist()
            
            # 3. Save to Qdrant
            qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "title": item['title'],
                            "price": item['price'],
                            "shopName": item['shopName'],
                            "boothUrl": item['boothUrl'],
                            "thumbnailUrl": item['thumbnailUrl']
                        }
                    )
                ]
            )
            print(f"  -> Successfully seeded into Qdrant payload")
            
        except Exception as e:
            print(f"  -> ERROR seeding {item['title']}: {e}")

    print("--- [DEBUG] Seeding Complete ---")

if __name__ == "__main__":
    seed_qdrant_only()
