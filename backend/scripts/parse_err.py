import json

with open("err.txt", "r", encoding="utf-8") as f:
    f.readline() # pass 200
    data = json.loads(f.readline())

print("Top 20 Detections:")
for i, x in enumerate(data.get("detections", [])):
    if x["confidence"] > 0.45:
        print(f"[{i:02d}] {x['class']} ({x['confidence']:.2f})")
