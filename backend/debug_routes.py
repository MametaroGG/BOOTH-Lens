import requests
import json

try:
    url = "http://127.0.0.1:8002/openapi.json"
    response = requests.get(url)
    if response.status_code == 200:
        schema = response.json()
        print("Registered Paths:")
        for path in schema.get("paths", {}):
            print(f"- {path}")
    else:
        print(f"Failed to fetch openapi.json. Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
