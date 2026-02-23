import json
import urllib.request
try:
    response = urllib.request.urlopen("http://127.0.0.1:8000/")
    data = json.loads(response.read().decode('utf-8'))
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
except Exception as e:
    with open("status.json", "w", encoding="utf-8") as f:
        f.write(str(e))
