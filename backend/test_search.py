import requests

url = "http://127.0.0.1:8000/api/search"
files = {'file': open('test_img.jpg', 'rb')}
try:
    response = requests.post(url, files=files)
    print("Status:", response.status_code)
    print("Response json:", response.json())
except Exception as e:
    print("Error:", e)
