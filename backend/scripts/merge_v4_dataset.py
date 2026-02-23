import os
import glob
import shutil
import yaml

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

v3_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "v3_merged")
zs_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "zero_shot_auto")
v4_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "v4_merged")

def merge_v4():
    print("Starting merge of v3_merged and augmented zero_shot_auto into v4_merged...")
    
    # 1. Read existing v3 classes
    with open(os.path.join(v3_dataset_dir, "data.yaml"), "r", encoding="utf-8") as f:
        v3_data = yaml.safe_load(f)
        
    v4_names = v3_data.get("names", {})
    # Convert keys to int if they aren't
    v4_names = {int(k): v for k, v in v4_names.items()}
    next_new_class_id = max(v4_names.keys()) + 1 if v4_names else 0

    # 2. Define explicit mapping for zero_shot classes to v3 classes
    # Key: zero_shot class name (lowercase), Value: v3 class name (to match against)
    class_mapping_rules = {
        "twintails hair": "twintails hair",
        "ponytail hair": "Ponytail",
        "bob hair": "bob hair",
        "long hair": "long hair",
        "cat ears": "Nekomimi",
        "rabbit ears": "Usagimimi",
        "animal ears": "Kemonomimi",
        "sheep ears": "Hitujimimi",
        "maid outfit": "Meidoutfit",
        "bikini": "bikini",
        "hoodie": "Hoodie",
        "jacket": "Jacket",
        "shorts": "Shorts",
        "glasses": "Glasses",
        "goggles": "Goggles",
        "choker": "Choker",
        "ribbon": "Ribbon",
        "hat": "Hat",
        # New hair types that might overlap with generic 'Hair'?
        # For now we let them be new specific classes to help model distinguish
    }

    # 3. Read zero_shot classes
    zs_classes_file = os.path.join(zs_dataset_dir, "classes.txt")
    if not os.path.exists(zs_classes_file):
        print("Error: zero_shot_auto/classes.txt not found. Did the annotation finish?")
        return

    with open(zs_classes_file, "r", encoding="utf-8") as f:
        zs_classes = [line.strip() for line in f if line.strip()]

    # Map zero_shot class IDs to unified v4 class IDs
    zs_to_v4_id_map = {}
    
    for zs_id, zs_name in enumerate(zs_classes):
        # Determine if it maps to an existing class
        target_v3_name = class_mapping_rules.get(zs_name.lower(), zs_name)
        mapped_id = None
        
        # Check if target name (or original zs_name) already exists in v4_names
        for k, v in v4_names.items():
            if v.lower() == target_v3_name.lower():
                mapped_id = k
                break
                    
        if mapped_id is not None:
            zs_to_v4_id_map[zs_id] = mapped_id
        else:
            # Create a new class
            zs_to_v4_id_map[zs_id] = next_new_class_id
            v4_names[next_new_class_id] = zs_name
            next_new_class_id += 1

    print("Class ID Mapping created:")
    for zs_id, v4_id in zs_to_v4_id_map.items():
        print(f"  ZS[{zs_id}] '{zs_classes[zs_id]}' -> V4[{v4_id}] '{v4_names.get(v4_id)}'")

    # 4. Create v4 directories
    os.makedirs(os.path.join(v4_dataset_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(v4_dataset_dir, "labels"), exist_ok=True)

    # 5. Copy v3 data to v4 (baseline)
    v3_images = glob.glob(os.path.join(v3_dataset_dir, "images", "*.jpg"))
    print(f"Copying {len(v3_images)} images from v3_merged...")
    for img_path in v3_images:
        shutil.copy2(img_path, os.path.join(v4_dataset_dir, "images", os.path.basename(img_path)))
        
        # copy label if exists
        label_path = os.path.join(v3_dataset_dir, "labels", os.path.basename(img_path).replace(".jpg", ".txt"))
        if os.path.exists(label_path):
            shutil.copy2(label_path, os.path.join(v4_dataset_dir, "labels", os.path.basename(label_path)))

    # 6. Merge augmented zero_shot data into v4
    zs_labels = glob.glob(os.path.join(zs_dataset_dir, "labels", "*.txt"))
    print(f"Merging {len(zs_labels)} augmented zero-shot annotations...")
    
    merged_count = 0
    new_count = 0
    
    for zs_label_path in zs_labels:
        base_name = os.path.basename(zs_label_path)
        v4_label_path = os.path.join(v4_dataset_dir, "labels", base_name)
        img_name = base_name.replace(".txt", ".jpg")
        
        # Read zero-shot label lines and remap IDs
        mapped_lines = []
        with open(zs_label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    old_id = int(parts[0])
                    new_id = zs_to_v4_id_map.get(old_id, old_id)
                    mapped_lines.append(f"{new_id} {' '.join(parts[1:])}")

        if not mapped_lines:
            continue

        if os.path.exists(v4_label_path):
            # Already exists? We append, but carefully. 
            # In Phase 3, we might have re-found same things. 
            # Let's just append for now to maximize boxes.
            with open(v4_label_path, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(mapped_lines) + "\n")
            merged_count += 1
        else:
            with open(v4_label_path, "w", encoding="utf-8") as f:
                f.write("\n".join(mapped_lines) + "\n")
            
            # Must copy the image over
            zs_img_path = os.path.join(zs_dataset_dir, "images", img_name)
            if os.path.exists(zs_img_path):
                shutil.copy2(zs_img_path, os.path.join(v4_dataset_dir, "images", img_name))
            new_count += 1

    print(f"Merged {merged_count} existing images with expanded tags.")
    print(f"Added {new_count} entirely new images to the dataset.")
    print(f"Total v4 dataset size: {len(glob.glob(os.path.join(v4_dataset_dir, 'images', '*.jpg')))} images.")

    # 7. Write new data.yaml
    final_yaml = {
        "path": v4_dataset_dir.replace("\\", "/"),
        "train": "images",
        "val": "images",
        "test": None,
        "nc": len(v4_names),
        "names": v4_names
    }
    
    with open(os.path.join(v4_dataset_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(final_yaml, f, sort_keys=False, allow_unicode=True)
        
    print(f"Successfully generated v4_merged dataset with {len(v4_names)} classes.")

if __name__ == "__main__":
    merge_v4()
