import requests
import os

# Create a small dummy image for testing if it doesn't exist
test_image = "test_image.jpg"
if not os.path.exists(test_image):
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(test_image)

url = 'http://localhost:8000/api/search'
files = {'file': open(test_image, 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
