import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import traceback

load_dotenv("../.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')

def test():
    img_path = "data/yolo_dataset/images/3805932_衣装モデルチャイナ服.jpg"
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    img = Image.open(img_path)
    print(f"Image: {img.size} {img.format}")

    print("--- Test 1: Simple image ---")
    try:
        response = model.generate_content(img)
        print(f"Success! {response.text}")
    except:
        print(f"Fail 1: {traceback.format_exc()}")

    print("--- Test 2: List [text, image] ---")
    try:
        response = model.generate_content(["What is this?", img])
        print(f"Success! {response.text}")
    except:
        print(f"Fail 2: {traceback.format_exc()}")

if __name__ == "__main__":
    test()
