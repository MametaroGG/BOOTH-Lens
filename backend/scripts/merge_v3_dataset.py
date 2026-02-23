import os
import glob
import shutil
import yaml

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

v2_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "v2_merged")
zs_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "zero_shot_auto")
v3_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "v3_merged")

def merge_v3():
    print("Starting merge of v2_merged and zero_shot_auto into v3_merged...")
    
    # 1. Read existing v2 classes
    with open(os.path.join(v2_dataset_dir, "data.yaml"), "r", encoding="utf-8") as f:
        v2_data = yaml.safe_load(f)
        
    v2_names = v2_data.get("names", {})
    # Convert keys to int if they aren't
    v2_names = {int(k): v for k, v in v2_names.items()}
    next_new_class_id = max(v2_names.keys()) + 1 if v2_names else 0

    # 2. Define explicit mapping for zero_shot classes to v2 classes
    # Key: zero_shot class name (lowercase), Value: v2 class name (to match against)
    class_mapping_rules = {
        "maid outfit": "Meidoutfit",
        "bikini": "bikini",
        "hoodie": "Hoodie",
        "jacket": "Jacket",
        "shorts": "Shorts",
        "ponytail hair": "Ponytail",
        "cat ears": "Nekomimi",
        "rabbit ears": "Usagimimi",
        "animal ears": "Kemonomimi",
        "glasses": "Glasses",
        "goggles": "Goggles",
        "choker": "Choker",
        "ribbon": "Ribbon"
    }

    # 3. Read zero_shot classes
    zs_classes = []
    with open(os.path.join(zs_dataset_dir, "classes.txt"), "r", encoding="utf-8") as f:
        zs_classes = [line.strip() for line in f if line.strip()]

    # Map zero_shot class IDs to unified v3 class IDs
    zs_to_v3_id_map = {}
    
    for zs_id, zs_name in enumerate(zs_classes):
        # Determine if it maps to an existing class
        target_v2_name = class_mapping_rules.get(zs_name.lower())
        mapped_id = None
        
        if target_v2_name:
            # Find the ID in v2_names
            for k, v in v2_names.items():
                if v.lower() == target_v2_name.lower():
                    mapped_id = k
                    break
                    
        if mapped_id is not None:
            zs_to_v3_id_map[zs_id] = mapped_id
        else:
            # Create a new class
            zs_to_v3_id_map[zs_id] = next_new_class_id
            v2_names[next_new_class_id] = zs_name
            next_new_class_id += 1

    print("Class ID Mapping created:")
    for zs_id, v3_id in zs_to_v3_id_map.items():
        print(f"  ZS[{zs_id}] '{zs_classes[zs_id]}' -> V3[{v3_id}] '{v2_names.get(v3_id)}'")

    # 4. Create v3 directories
    os.makedirs(os.path.join(v3_dataset_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(v3_dataset_dir, "labels"), exist_ok=True)

    # 5. Copy v2 data to v3 (baseline)
    v2_images = glob.glob(os.path.join(v2_dataset_dir, "images", "*.jpg"))
    print(f"Copying {len(v2_images)} images from v2_merged...")
    for img_path in v2_images:
        shutil.copy2(img_path, os.path.join(v3_dataset_dir, "images", os.path.basename(img_path)))
        
        # copy label if exists
        label_path = img_path.replace("images", "labels").replace(".jpg", ".txt")
        if os.path.exists(label_path):
            shutil.copy2(label_path, os.path.join(v3_dataset_dir, "labels", os.path.basename(label_path)))

    # 6. Merge zero_shot data into v3
    zs_labels = glob.glob(os.path.join(zs_dataset_dir, "labels", "*.txt"))
    print(f"Merging {len(zs_labels)} zero-shot annotations...")
    
    merged_count = 0
    new_count = 0
    
    for zs_label_path in zs_labels:
        base_name = os.path.basename(zs_label_path)
        v3_label_path = os.path.join(v3_dataset_dir, "labels", base_name)
        img_name = base_name.replace(".txt", ".jpg")
        
        # Read zero-shot label lines and remap IDs
        mapped_lines = []
        with open(zs_label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    old_id = int(parts[0])
                    new_id = zs_to_v3_id_map.get(old_id, old_id)
                    mapped_lines.append(f"{new_id} {' '.join(parts[1:])}")

        if not mapped_lines:
            continue

        if os.path.exists(v3_label_path):
            # The image was already in v2 (e.g. face was annotated). Append the new labels!
            with open(v3_label_path, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(mapped_lines) + "\n")
            merged_count += 1
        else:
            # Brand new image annotated by zero-shot that wasn't previously in the dataset
            with open(v3_label_path, "w", encoding="utf-8") as f:
                f.write("\n".join(mapped_lines) + "\n")
            
            # Must copy the image over
            zs_img_path = os.path.join(zs_dataset_dir, "images", img_name)
            if os.path.exists(zs_img_path):
                shutil.copy2(zs_img_path, os.path.join(v3_dataset_dir, "images", img_name))
            new_count += 1

    print(f"Merged {merged_count} existing images with new tags.")
    print(f"Added {new_count} entirely new images to the dataset.")
    print(f"Total v3 dataset size: {len(glob.glob(os.path.join(v3_dataset_dir, 'images', '*.jpg')))} images.")

    # 7. Write new data.yaml
    final_yaml = {
        "path": v3_dataset_dir.replace("\\", "/"),
        "train": "images",
        "val": "images",
        "test": None,
        "nc": len(v2_names),
        "names": v2_names
    }
    
    with open(os.path.join(v3_dataset_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(final_yaml, f, sort_keys=False, allow_unicode=True)
        
    print(f"Successfully generated v3_merged dataset with {len(v2_names)} classes.")

if __name__ == "__main__":
    merge_v3()
