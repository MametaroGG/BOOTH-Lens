import asyncio
import logging
from app.services.vector_db import VectorDBService

logging.basicConfig(level=logging.DEBUG)

async def main():
    service = VectorDBService()
    vector = [0.1] * 512
    try:
        from qdrant_client.http.models import Filter
        # Pass a totally empty filter, or None
        print("Calling query_points...")
        res = service.client.query_points(
            collection_name=service.collection_name,
            query=vector,
            limit=5
        )
        print("SUCCESS!")
        print(res.points)
    except Exception as e:
        print("ERROR:")
        print(repr(e))

if __name__ == "__main__":
    asyncio.run(main())
