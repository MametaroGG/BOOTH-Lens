import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
from ..services.image_processor import ImageProcessor
from ..services.vector_db import VectorDBService
from ..middleware import check_search_limit
from ..db import get_db_connection

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    avatars: Optional[List[str]] = None
    colors: Optional[List[str]] = None

from functools import lru_cache

# Dependency to get services
@lru_cache()
def get_image_processor():
    return ImageProcessor()

@lru_cache()
def get_vector_db():
    return VectorDBService()

@router.post("/search")
async def search_image(
    file: UploadFile = File(...),
    image_processor: ImageProcessor = Depends(get_image_processor),
    vector_db: VectorDBService = Depends(get_vector_db),
    user = Depends(check_search_limit) # Enforce limit
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 1. Get embedding for the whole image (MVP approach)
        vector = image_processor.get_embedding(image)
        
        # 2. Search in Qdrant with opt-out filter
        conn = get_db_connection()
        excluded_shops = set()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM Shop WHERE optOut = 1")
            rows = cursor.fetchall()
            for row in rows:
                excluded_shops.add(row['name'])
        finally:
            conn.close()

        results = vector_db.search_similar(vector, excluded_shops=excluded_shops)
        
        return {
            "results": [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "payload": hit.payload
                } for hit in results
            ]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
