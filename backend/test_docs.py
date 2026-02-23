import requests

try:
    resp = requests.get('http://localhost:8000/docs')
    print("Docs Status:", resp.status_code)
except Exception as e:
    print("Docs error:", e)

try:
    resp = requests.get('http://localhost:8000/openapi.json')
    print("OpenAPI Status:", resp.status_code)
except Exception as e:
    print("OpenAPI error:", e)
