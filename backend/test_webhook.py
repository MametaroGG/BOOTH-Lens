import requests
import time
import sqlite3
import os

BASE_URL = "http://127.0.0.1:8001"
DB_PATH = "prisma/dev.db"

def wait_for_server():
    for _ in range(60):
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

def test_webhook_accessibility():
    url = f"{BASE_URL}/api/subscription/webhook"
    
    print(f"Testing Webhook Availability: {url}")
    try:
        # Send empty payload without signature - should fail with 400
        resp = requests.post(url, json={})
        if resp.status_code == 400:
            print("Webhook Endpoint is Reachable (Got expected 400 Bad Request)")
        else:
            print(f"Unexpected Status: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Request Error: {e}")

def test_db_accessibility():
    print(f"Testing DB Access: {DB_PATH}")
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            # Just verify we can query sqlite_master
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='User';")
            result = cursor.fetchone()
            if result:
                 print("DB Connection Success: 'User' table found.")
            else:
                 print("DB Connection Success but 'User' table NOT found.")
            conn.close()
        except Exception as e:
            print(f"DB Connection Failed: {e}")
    else:
        print(f"DB File Not Found at {DB_PATH}")

if __name__ == "__main__":
    if wait_for_server():
        test_webhook_accessibility()
        test_db_accessibility()
