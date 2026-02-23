import os
import glob
import random
import shutil
import torch
from PIL import Image
from tqdm import tqdm
from transformers import Owlv2Processor, Owlv2ForObjectDetection

# ---------------------------------------------------------------------
# フェーズ2: トレンドのアバター服飾タグリスト（AI提案）
# ※これらのキーワード（英語）をテキストプロンプトとしてゼロショットAIに投げて枠を探させます。
# ---------------------------------------------------------------------
TEXT_PROMPTS = [
    "gothic dress",
    "cyberpunk clothes",
    "techwear",
    "maid outfit",
    "swimsuit",
    "bikini",
    "school uniform",
    "casual wear",
    "frill skirt",
    "hoodie",
    "jacket",
    "shorts",
    "twintails hair",
    "ponytail hair",
    "side ponytail hair",
    "braids hair",
    "short hair",
    "bob hair",
    "long hair",
    "straight hair",
    "curly hair",
    "cat ears",     # nekomimi
    "rabbit ears",  # usagimimi
    "animal ears",  # kemonomimi
    "sheep ears",
    "fox ears",
    "horns",
    "hair clip",
    "headset",
    "halo",
    "crown",
    "glasses",
    "goggles",
    "choker",
    "ribbon",
    "hat",
]

# BOOTHのユーザーが使うであろうタグ名と、データセット内での一貫性を保つため、
# もし見つかった場合は以下のID（または新規ID）としてyoloデータセットにマッピングします。
# ※今回は簡単のため、見つかった単語のインデックスを独自の一時的なクラスIDとして付与し、
# あとで統合データセットを作るときに data.yaml を自動更新する仕組みにします。

def perform_zero_shot_annotation(num_samples=1000, confidence_threshold=0.1):
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load Owlv2 model and processor (powerful open-vocabulary object detector)
    # We use owlv2-base-patch16-ensemble as it has good zero-shot accuracy
    model_id = "google/owlv2-base-patch16-ensemble"
    print(f"Loading {model_id} ...")
    try:
        processor = Owlv2Processor.from_pretrained(model_id)
        model = Owlv2ForObjectDetection.from_pretrained(model_id).to(device)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have internet access to download the weights on first run.")
        return

    raw_images_dir = os.path.join(backend_dir, "scraper", "data", "raw_images")
    output_dataset_dir = os.path.join(backend_dir, "yolo_dataset", "zero_shot_auto")
    images_out_dir = os.path.join(output_dataset_dir, "images")
    labels_out_dir = os.path.join(output_dataset_dir, "labels")

    os.makedirs(images_out_dir, exist_ok=True)
    os.makedirs(labels_out_dir, exist_ok=True)

    all_images = glob.glob(os.path.join(raw_images_dir, "*.jpg"))
    if not all_images:
        print("No raw images found.")
        return

    random.shuffle(all_images)
    samples = all_images[:num_samples]
    
    print(f"Starting zero-shot annotation for {len(samples)} images against {len(TEXT_PROMPTS)} tags...")
    
    successful_annotated = 0

    for img_path in tqdm(samples):
        filename = os.path.basename(img_path)
        img_name, ext = os.path.splitext(filename)
        
        try:
            image = Image.open(img_path).convert("RGB")
            
            # owl vit expects prompts formatted slightly specifically
            # format: "a photo of an object" or just "object" -> "a photo of a [item]" works best
            texts = [[f"a photo of a {prompt}" for prompt in TEXT_PROMPTS]]
            
            inputs = processor(text=texts, images=image, return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Target image sizes (height, width) to rescale bounding boxes back to original size
            target_sizes = torch.tensor([image.size[::-1]]).to(device)
            results = processor.image_processor.post_process_object_detection(outputs=outputs, target_sizes=target_sizes, threshold=confidence_threshold)
            
            # Retrieve predictions for the first image
            i = 0
            text = texts[i]
            # No threshold filter here to see best raw scores
            results_raw = processor.image_processor.post_process_object_detection(outputs=outputs, target_sizes=target_sizes, threshold=0.0)
            boxes, scores, labels = results_raw[i]["boxes"], results_raw[i]["scores"], results_raw[i]["labels"]

            if len(scores) > 0:
                print(f"[{filename}] Max score: {scores.max().item():.3f} for label '{TEXT_PROMPTS[labels[scores.argmax()].item()]}'")
            else:
                print(f"[{filename}] No boxes generated at all.")
                
            has_detections = False
            label_lines = []
            
            # Apply our actual custom threshold
            for box, score, label in zip(boxes, scores, labels):
                if score.item() < confidence_threshold:
                    continue
                box = [round(j, 2) for j in box.tolist()]
                # box is [xmin, ymin, xmax, ymax]
                x_min, y_min, x_max, y_max = box
                
                img_w, img_h = image.size
                
                # YOLO format: cx, cy, w, h normalized
                cx = ((x_min + x_max) / 2) / img_w
                cy = ((y_min + y_max) / 2) / img_h
                w = (x_max - x_min) / img_w
                h = (y_max - y_min) / img_h
                
                # clamp to 0-1
                cx = max(0, min(cx, 1))
                cy = max(0, min(cy, 1))
                w = max(0, min(w, 1))
                h = max(0, min(h, 1))
                
                cls_id = label.item() # This corresponds to the index in TEXT_PROMPTS
                
                label_lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
                has_detections = True
            
            if has_detections:
                dest_img = os.path.join(images_out_dir, filename)
                shutil.copy2(img_path, dest_img)
                
                label_path = os.path.join(labels_out_dir, f"{img_name}.txt")
                with open(label_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(label_lines) + "\n")
                    
                successful_annotated += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Zero-shot auto-annotation complete! {successful_annotated} images successfully annotated.")
    
    # Save the custom classes.txt so we know what they map to
    with open(os.path.join(output_dataset_dir, "classes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(TEXT_PROMPTS) + "\n")

if __name__ == "__main__":
    # Run on 1000 images with expanded tags for quality over quantity in this iteration
    perform_zero_shot_annotation(num_samples=1000, confidence_threshold=0.1)
