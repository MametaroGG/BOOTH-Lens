from qdrant_client import QdrantClient
import inspect

print("Checking Qdrant Client methods...")
client = QdrantClient(":memory:")
print(f"Client type: {type(client)}")
print("Available attributes:")
attrs = [a for a in dir(client) if not a.startswith("_")]
print(attrs)

if hasattr(client, 'search'):
    print(f"Method 'search' EXISTS. Signature: {inspect.signature(client.search)}")
else:
    print("Method 'search' MISSING.")

if hasattr(client, 'query_points'):
    print(f"Method 'query_points' EXISTS. Signature: {inspect.signature(client.query_points)}")
else:
    print("Method 'query_points' MISSING.")

if hasattr(client, 'search_points'):
    print(f"Method 'search_points' EXISTS. Signature: {inspect.signature(client.search_points)}")
