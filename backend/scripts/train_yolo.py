from ultralytics import YOLO
import os

def train_model():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_yaml = os.path.join(backend_dir, "yolo_dataset", "v3_merged", "data.yaml")
    
    # We can start training from the current best model to fine-tune it
    model_path = os.path.join(backend_dir, "runs", "detect", "runs", "detect", "train_v2_auto", "weights", "best.pt")
    if not os.path.exists(model_path):
        model_path = "yolo11n.pt" # Fallback to base model
        print("Existing best.pt not found, starting over from yolo11n.pt")
    else:
        print(f"Fine-tuning from existing model: {model_path}")

    model = YOLO(model_path)
    
    # Train the model
    # We use a small number of epochs for the first test run
    print("Starting YOLO training...")
    # NOTE: imgsz=1024 because the original images are 1024x1024 and we want fine details.
    # Adjust batch size based on GPU VRAM. 4 or 8 is usually safe for 1024px on consumer GPUs.
    results = model.train(
        data=data_yaml,
        epochs=30,      # test with 30 epochs
        imgsz=1024,
        batch=4,
        device='cpu',       # Changed from 0 to 'cpu' since CUDA is not configured
        project="runs/detect",
        name="train_v3_auto",
        exist_ok=True
    )
    
    print("Training completed!")

if __name__ == "__main__":
    train_model()
