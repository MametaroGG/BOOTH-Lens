import asyncio
from app.services.vector_db import VectorDBService
from app.services.image_processor import ImageProcessor
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    qdrant_url = os.getenv("QDRANT_CLOUD_URL")
    print(f"Connecting to Qdrant Cloud: {qdrant_url}")
    
    vector_db = VectorDBService()
    
    # Force recreation for a clean slate
    print("Recreating collection to ensure clean slate with indices...")
    vector_db.client.delete_collection(vector_db.collection_name)
    vector_db.ensure_collection()
    
    image_processor = ImageProcessor()
    
    print("Starting seed_data...")
    await vector_db.seed_data(image_processor)
    print("Seeding initiated/completed.")

if __name__ == "__main__":
    asyncio.run(main())
