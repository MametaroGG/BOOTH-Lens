import requests
import glob
import os

# Assuming backend is running on localhost:8000
API_URL = "http://localhost:8000/api/detect"

def test_api():
    # Find a test image
    images = glob.glob("backend/yolo_dataset/test_v1/images/*.jpg")
    if not images:
        print("No test images found.")
        return

    test_image_path = images[0]
    print(f"Testing API with image: {test_image_path}")

    try:
        with open(test_image_path, "rb") as f:
            files = {"file": ("image.jpg", f, "image/jpeg")}
            response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to API: {e}")
        print("Is the backend server running on port 8000?")

if __name__ == "__main__":
    test_api()
