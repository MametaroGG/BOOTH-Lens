import os
import random
import glob
import shutil
from ultralytics import YOLO
from pathlib import Path
from tqdm import tqdm

def find_best_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "runs", "detect", "train2", "weights", "best.pt"),
        os.path.join(base_dir, "..", "runs", "detect", "train2", "weights", "best.pt"),
        os.path.join(base_dir, "runs", "detect", "train", "weights", "best.pt"),
        os.path.join(base_dir, "..", "runs", "detect", "train", "weights", "best.pt"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def auto_annotate(num_samples=1000, confidence_threshold=0.6):
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    model_path = find_best_model()
    if not model_path:
        print("Error: best.pt model not found! Please ensure it exists.")
        return

    print(f"Loading YOLO model from: {model_path}")
    model = YOLO(model_path)

    raw_images_dir = os.path.join(backend_dir, "scraper", "data", "raw_images")
    output_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "auto_generated")
    images_out_dir = os.path.join(output_dataset_dir, "images")
    labels_out_dir = os.path.join(output_dataset_dir, "labels")

    os.makedirs(images_out_dir, exist_ok=True)
    os.makedirs(labels_out_dir, exist_ok=True)

    # Get all jpg images
    all_images = glob.glob(os.path.join(raw_images_dir, "*.jpg"))
    if not all_images:
        print(f"No images found in {raw_images_dir}")
        return

    print(f"Found {len(all_images)} raw images.")
    
    # Shuffle and pick num_samples
    random.shuffle(all_images)
    samples = all_images[:num_samples]
    
    print(f"Starting auto-annotation for {len(samples)} images...")
    
    successful_annotated = 0

    for img_path in tqdm(samples):
        filename = os.path.basename(img_path)
        img_name, ext = os.path.splitext(filename)
        
        try:
            results = model(img_path, conf=confidence_threshold, verbose=False)
            
            # If nothing was detected above threshold, skip saving this image
            # Or you might want to save it as empty background. For now, we only save if detected.
            has_detections = False
            label_lines = []
            
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls)
                    # YOLO normalized coordinates: center_x center_y width height
                    # xywhn is normalized 0-1
                    x, y, w, h = box.xywhn[0]
                    label_lines.append(f"{cls_id} {float(x)} {float(y)} {float(w)} {float(h)}")
                    has_detections = True
            
            if has_detections:
                # 1. Copy image
                dest_img = os.path.join(images_out_dir, filename)
                shutil.copy2(img_path, dest_img)
                
                # 2. Save label
                label_path = os.path.join(labels_out_dir, f"{img_name}.txt")
                with open(label_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(label_lines) + "\n")
                    
                successful_annotated += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Auto-annotation complete! {successful_annotated} images successfully extracted to {output_dataset_dir}")

if __name__ == "__main__":
    # Test run with 1000 images
    auto_annotate(num_samples=1000, confidence_threshold=0.6)
