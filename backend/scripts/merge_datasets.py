import os
import shutil
import yaml
from pathlib import Path

def merge_datasets():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manual_dir = os.path.join(backend_dir, "yolo_dataset", "test_v1")
    auto_dir = os.path.join(backend_dir, "yolo_dataset", "auto_generated")
    merged_dir = os.path.join(backend_dir, "yolo_dataset", "v2_merged")
    
    # Create merged dirs
    merged_images = os.path.join(merged_dir, "images")
    merged_labels = os.path.join(merged_dir, "labels")
    os.makedirs(merged_images, exist_ok=True)
    os.makedirs(merged_labels, exist_ok=True)
    
    files_copied = 0
    
    # Copy manual data
    manual_images = os.path.join(manual_dir, "images")
    manual_labels = os.path.join(manual_dir, "labels")
    for filename in os.listdir(manual_images):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Image
            src_img = os.path.join(manual_images, filename)
            dst_img = os.path.join(merged_images, filename)
            shutil.copy2(src_img, dst_img)
            
            # Label
            label_name = os.path.splitext(filename)[0] + ".txt"
            src_label = os.path.join(manual_labels, label_name)
            if os.path.exists(src_label):
                dst_label = os.path.join(merged_labels, label_name)
                shutil.copy2(src_label, dst_label)
            files_copied += 1
            
    # Copy auto data
    auto_images = os.path.join(auto_dir, "images")
    auto_labels = os.path.join(auto_dir, "labels")
    for filename in os.listdir(auto_images):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Ensure no overwrite (in case of overlap)
            if os.path.exists(os.path.join(merged_images, filename)):
                continue
                
            src_img = os.path.join(auto_images, filename)
            dst_img = os.path.join(merged_images, filename)
            shutil.copy2(src_img, dst_img)
            
            label_name = os.path.splitext(filename)[0] + ".txt"
            src_label = os.path.join(auto_labels, label_name)
            if os.path.exists(src_label):
                dst_label = os.path.join(merged_labels, label_name)
                shutil.copy2(src_label, dst_label)
            files_copied += 1
            
    print(f"Merged dataset created with {files_copied} images at {merged_dir}")
    
    # Create data.yaml
    with open(os.path.join(manual_dir, "data.yaml"), "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    data["path"] = merged_dir.replace("\\", "/")
    data["train"] = "images"
    data["val"] = "images"  # We use the same for validation just for simplicity here, or you could split.
    
    with open(os.path.join(merged_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)
        
    print("Created v2_merged/data.yaml")

if __name__ == "__main__":
    merge_datasets()
