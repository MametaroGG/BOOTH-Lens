import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

device = 'cpu'
print("Loading model...")
model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').to(device)
processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

img = Image.new('RGB', (224, 224), color=(128, 64, 200))
inputs = processor(images=img, return_tensors='pt').to(device)

with torch.no_grad():
    outputs = model.get_image_features(**inputs)

print(f'Type: {type(outputs)}')
print(f'Is Tensor: {isinstance(outputs, torch.Tensor)}')

if isinstance(outputs, torch.Tensor):
    print(f'Shape: {outputs.shape}')
    norm = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
    print(f'SUCCESS: Normalization worked! Shape: {norm.shape}')
else:
    print(f'Attributes: {[a for a in dir(outputs) if not a.startswith("_")]}')
    # Try to find a tensor
    for attr in dir(outputs):
        if not attr.startswith("_"):
            val = getattr(outputs, attr)
            if isinstance(val, torch.Tensor):
                print(f'Found tensor at attr "{attr}": shape={val.shape}')
