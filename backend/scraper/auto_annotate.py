import os
import json
import logging
import time
import base64
import requests
import re
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY not found in .env")
    exit(1)

# Define Classes
CLASSES = [
    "T-shirt",
    "Shirt",
    "Hoodie",
    "Jacket_Coat",
    "Skirt",
    "Pants_Shorts",
    "Dress",
    "Swimsuit_Underwear",
    "Uniform",
    "Ponytail",
    "Twin-tails",
    "Hair_Other",
    "Shoes_Boots",
    "Accessory",
    "Other_Outfit"
]
CLASS_TO_ID = {cls.lower(): i for i, cls in enumerate(CLASSES)}

def get_yolo_format(box, img_width, img_height):
    ymin, xmin, ymax, xmax = box
    ymin, xmin, ymax, xmax = ymin/1000, xmin/1000, ymax/1000, xmax/1000
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    width = xmax - xmin
    height = ymax - ymin
    return x_center, y_center, width, height

def auto_annotate():
    dataset_dir = "data/yolo_dataset/images"
    if not os.path.exists(dataset_dir):
        logging.error(f"Directory {dataset_dir} not found.")
        return

    # Ensure classes.txt exists and matches our list
    classes_path = os.path.join(dataset_dir, "classes.txt")
    with open(classes_path, "w", encoding='utf-8') as f:
        f.write("\n".join(CLASSES) + "\n")

    image_files = [f for f in os.listdir(dataset_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    logging.info(f"Processing {len(image_files)} images for Multi-Class Annotation via REST API...")

    # Use Gemini 2.5 Pro for best reasoning
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"

    for i, img_file in enumerate(image_files):
        img_path = os.path.join(dataset_dir, img_file)
        label_file = os.path.join(dataset_dir, os.path.splitext(img_file)[0] + ".txt")
        
        if os.path.exists(label_file) and img_file != "classes.txt":
            continue

        meta_file = os.path.join(dataset_dir, os.path.splitext(img_file)[0] + "_meta.txt")
        context_info = ""
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f: context_info = f.read()

        logging.info(f"[{i+1}/{len(image_files)}] Analyzing Multi-Class: {img_file}")
        
        try:
            with open(img_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')

            prompt_text = (
                "You are an expert computer vision system ASSISTED by product metadata. Analyze this image to find ALL distinct 3D character clothing items, hairstyles, and accessories.\n"
                f"=== METADATA (Title, Description, Tags) ===\n{context_info}\n===========================================\n"
                "CRITICAL INSTRUCTION: Read the METADATA above first. Use it to understand EXACTLY what the creator is selling (e.g., if it says 'parka', look for a Hoodie. If it says 'skirt', look for a Skirt. If it mentions a hairstyle like 'twin tails', look for Twin-tails).\n\n"
                f"You MUST classify each found item STRICTLY into one of the following exact categories: {', '.join(CLASSES)}.\n"
                "First, think step-by-step: 'Based on the metadata, this product is X. In the image, X is located at the top/bottom. I also see Y and Z.'\n"
                "Then, for EACH valid item you found from the class list, provide its class and a STRICTLY TIGHT bounding box that wraps ONLY that specific item.\n"
                "Output the final results in the following format exactly, one item per line:\n"
                "ITEM: [Class Name], BOX: [ymin, xmin, ymax, xmax]\n"
                "where coordinates are normalized integers from 0 to 1000. Example:\n"
                "ITEM: Skirt, BOX: [500, 200, 850, 800]\n"
                "ITEM: T-shirt, BOX: [200, 220, 520, 780]\n"
                "Ensure the class name exactly matches the list provided."
            )

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt_text},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_data}}
                    ]
                }]
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            res_json = response.json()

            if "candidates" in res_json:
                text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Regex to find all ITEM: ..., BOX: [...] matches
                matches = re.finditer(r'ITEM:\s*([A-Za-z0-9_-]+)\s*,\s*BOX:\s*\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', text)
                
                boxes_found = []
                from PIL import Image
                with Image.open(img_path) as img: w, h = img.size

                for match in matches:
                    cls_name = match.group(1).lower()
                    if cls_name in CLASS_TO_ID:
                        box = [int(n) for n in match.groups()[1:]]
                        xc, yc, rw, rh = get_yolo_format(box, w, h)
                        boxes_found.append(f"{CLASS_TO_ID[cls_name]} {xc:.6f} {yc:.6f} {rw:.6f} {rh:.6f}")
                    else:
                        logging.warning(f"  Unknown class predicted: {match.group(1)}")
                
                if boxes_found:
                    with open(label_file, 'w', encoding='utf-8') as lf:
                        lf.write("\n".join(boxes_found) + "\n")
                    logging.info(f"  SUCCESS: {img_file} => {len(boxes_found)} items mapped.")
                else:
                    logging.warning(f"  PARSE FAILED or no items: {text}")
            else:
                logging.error(f"  API ERROR: {json.dumps(res_json)}")

            time.sleep(1.0) # Rate limit safety

        except Exception as e:
            logging.error(f"  Error: {e}")

if __name__ == "__main__":
    auto_annotate()
