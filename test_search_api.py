import requests
import os

BASE_URL = "http://localhost:8000"

def test_search():
    print("Testing /api/search...")
    image_path = "backend/yolo_dataset/test_v1/images/1336133_2.jpg"
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(f"{BASE_URL}/api/search", files=files)
            if response.status_code == 200:
                print("Search Success!")
                data = response.json()
                print(f"Found {len(data.get('results', []))} results.")
                # print(data)
            else:
                print(f"Search Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Search Error: {e}")

def test_opt_out():
    print("\nTesting /api/opt-out...")
    payload = {"shopUrl": "https://test-shop.booth.pm"}
    try:
        response = requests.post(f"{BASE_URL}/api/opt-out", json=payload)
        if response.status_code == 200:
            print("Opt-out Success!")
            print(response.json())
        else:
            print(f"Opt-out Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Opt-out Error: {e}")

if __name__ == "__main__":
    test_search()
    test_opt_out()
