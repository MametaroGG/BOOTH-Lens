from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio

from app.db import init_db
from app.routers.search import get_vector_db
from app.services.image_processor import ImageProcessor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite DB
    init_db()
    
    # Start background seeding for VectorDB
    # processor = ImageProcessor() 
    # vector_db = get_vector_db()
    # asyncio.create_task(vector_db.seed_data(processor))
    
    yield
    # Cleanup if needed

from app.routers import search, subscription, admin

app = FastAPI(lifespan=lifespan)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images (search results)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: scraper/data is at the same level as app, inside backend
SCRAPER_DATA_DIR = os.path.join(BASE_DIR, "scraper", "data", "raw_images")

# Ensure directory exists to avoid errors
if os.path.exists(SCRAPER_DATA_DIR):
    app.mount("/api/images", StaticFiles(directory=SCRAPER_DATA_DIR), name="images")

app.include_router(search.router, prefix="/api")
app.include_router(subscription.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "backend running", "db": "sqlite"}

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("GLOBAL EXCEPTION:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "error": str(exc)})
