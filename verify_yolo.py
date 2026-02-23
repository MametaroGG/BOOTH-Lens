from ultralytics import YOLO
import glob
import os

# Load the best model
# Note: Adjust the path if training saved to a different run directory (e.g., train2, train3)
# We will use a glob pattern to find the latest run
runs = glob.glob('runs/detect/train*')
latest_run = max(runs, key=os.path.getmtime)
model_path = os.path.join(latest_run, 'weights', 'best.pt')

print(f"Loading model from: {model_path}")
model = YOLO(model_path)

# Test on a few images from the test set
test_images = glob.glob('backend/yolo_dataset/test_v1/images/*.jpg')[:3]

if not test_images:
    print("No test images found.")
else:
    print(f"Testing on {len(test_images)} images...")
    results = model(test_images)

    for i, r in enumerate(results):
        print(f"\nImage: {test_images[i]}")
        for box in r.boxes:
            print(f"  - Class: {model.names[int(box.cls)]}, Conf: {float(box.conf):.2f}")
