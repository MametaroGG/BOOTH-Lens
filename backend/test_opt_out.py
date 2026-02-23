import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def wait_for_server():
    for _ in range(10):
        try:
            resp = requests.get(BASE_URL)
            if resp.status_code == 200:
                print("Server is up!")
                return True
        except:
            pass
        time.sleep(1)
    print("Server failed to start.")
    return False

def test_opt_out():
    url = f"{BASE_URL}/api/opt-out"
    shop_url = "https://mame-shop.booth.pm/"
    
    print(f"Testing Opt-out for: {shop_url}")
    try:
        resp = requests.post(url, json={"shopUrl": shop_url})
        if resp.status_code == 200:
            print("Opt-out Success:", resp.json())
        else:
            print("Opt-out Failed:", resp.status_code, resp.text)
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    if wait_for_server():
        test_opt_out()
