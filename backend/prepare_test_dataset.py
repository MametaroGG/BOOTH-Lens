import os
import random
import shutil
import glob

# Paths
SOURCE_DIR = "scraper/data/raw_images"
DEST_IMG_DIR = "yolo_dataset/test_v1/images"
DEST_LBL_DIR = "yolo_dataset/test_v1/labels"

# Ensure directories exist
os.makedirs(DEST_IMG_DIR, exist_ok=True)
os.makedirs(DEST_LBL_DIR, exist_ok=True)

# Get all images
all_images = glob.glob(os.path.join(SOURCE_DIR, "*.jpg"))
print(f"Total images found: {len(all_images)}")

# Select 50 random images
if len(all_images) > 50:
    selected_images = random.sample(all_images, 50)
else:
    selected_images = all_images

print(f"Selecting {len(selected_images)} images for testing...")

# Copy images
for img_path in selected_images:
    filename = os.path.basename(img_path)
    dest_path = os.path.join(DEST_IMG_DIR, filename)
    shutil.copy2(img_path, dest_path)

print("Done! Images copied to:", DEST_IMG_DIR)
