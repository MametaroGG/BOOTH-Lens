from ultralytics import YOLO
import os

def train_model_v4():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_yaml = os.path.join(backend_dir, "yolo_dataset", "v4_merged", "data.yaml")
    
    # Fine-tune from the v3 model (latest auto-trained model)
    model_path = os.path.join(backend_dir, "runs", "detect", "train_v3_auto", "weights", "best.pt")
    
    if not os.path.exists(model_path):
        # Fallback to the previous one if v3 failed or hasn't run
        model_path = os.path.join(backend_dir, "runs", "detect", "train_v2_auto", "weights", "best.pt")
        
    if not os.path.exists(model_path):
        model_path = "yolo11n.pt"
        print("Previous best.pt models not found, starting from base yolo11n.pt")
    else:
        print(f"Fine-tuning from existing model: {model_path}")

    model = YOLO(model_path)
    
    print("Starting Phase 3 (v4) YOLO training with expanded knowledge...")
    # Using 50 epochs to allow the model more sessions to distinguish similar labels
    results = model.train(
        data=data_yaml,
        epochs=50,      
        imgsz=1024,
        batch=4,
        device='cpu',
        project="runs/detect",
        name="train_v4_refinement",
        exist_ok=True
    )
    
    print("Training Completed for v4 refinement!")

if __name__ == "__main__":
    train_model_v4()
