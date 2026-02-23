import requests
try:
    response = requests.post('http://localhost:8000/api/text-search', json={"query": "test"})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Response text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
