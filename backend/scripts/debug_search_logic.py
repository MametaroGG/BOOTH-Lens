import asyncio
import io
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from qdrant_client import QdrantClient, models

# Mock the setup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

try:
    print("Loading model...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    qdrant = QdrantClient(":memory:")
    print("Model loaded.")

    # Create dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    # Run logic from search_standalone.py
    print("Processing image...")
    inputs = processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    
    print(f"Features type: {type(features)}")
    
    # Test normalization
    features = features / features.norm(p=2, dim=-1, keepdim=True)
    vector = features.cpu().numpy()[0].tolist()
    print(f"Vector length: {len(vector)}")
    
    # Test Qdrant search
    print("Searching Qdrant...")
    results = qdrant.search(
        collection_name="booth_items",
        query_vector=vector,
        limit=10
    )
    print("Search complete (empty result expected).")

except Exception as e:
    import traceback
    traceback.print_exc()
