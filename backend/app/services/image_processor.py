from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import io

class ImageProcessor:
    def __init__(self):
        # Initialize CLIP
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_embedding(self, image: Image.Image):
        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.clip_model.get_image_features(**inputs)
        
        # Robustly handle different CLIP output formats
        if hasattr(outputs, "image_embeds"):
            image_features = outputs.image_embeds
        elif hasattr(outputs, "pooler_output"):
            image_features = outputs.pooler_output
        elif isinstance(outputs, (list, tuple)):
            image_features = outputs[0]
        else:
            image_features = outputs

        # Final check: must be a tensor
        if not isinstance(image_features, torch.Tensor):
            try:
                image_features = outputs[0]
            except:
                raise Exception(f"Failed to extract tensor from {type(outputs)}")
            
        # Normalize
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0].tolist()

    def get_text_embedding(self, text: str):
        """
        Generate embedding for text query.
        """
        inputs = self.clip_processor(text=text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.clip_model.get_text_features(**inputs)
            
        # Robustly handle different CLIP output formats
        if hasattr(outputs, "text_embeds"):
            text_features = outputs.text_embeds
        elif hasattr(outputs, "pooler_output"):
            text_features = outputs.pooler_output
        elif isinstance(outputs, (list, tuple)):
            text_features = outputs[0]
        else:
            text_features = outputs

        # Final check: must be a tensor
        if not isinstance(text_features, torch.Tensor):
            try:
                text_features = outputs[0]
            except:
                raise Exception(f"Failed to extract tensor from {type(outputs)}")
            
        # Normalize
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        return text_features.cpu().numpy()[0].tolist()

