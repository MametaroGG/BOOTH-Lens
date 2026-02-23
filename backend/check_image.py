import requests
url = "http://127.0.0.1:8001/api/images/5957830_9.jpg"
try:
    response = requests.get(url, timeout=10)
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Content-Length: {response.headers.get('Content-Length')}")
    print(f"Headers: {response.headers}")
except Exception as e:
    print(f"Error: {e}")
