import os
import io
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resize_existing_images(directory, max_size=(800, 800), quality=85):
    """
    Resizes all existing images in the given directory to the specified max_size
    and re-saves them as optimized JPEG files.
    """
    if not os.path.exists(directory):
        logging.error(f"Directory {directory} not found.")
        return

    # Gather all image files
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    total = len(files)
    
    if total == 0:
        logging.info("No images found to process.")
        return

    logging.info(f"Found {total} images. Starting resize process...")
    processed = 0
    skipped = 0
    errors = 0

    for filename in files:
        filepath = os.path.join(directory, filename)
        try:
            # Check file size (optional optimization: skip if already very small, e.g. < 50KB)
            orig_size_kb = os.path.getsize(filepath) / 1024.0

            img = Image.open(filepath)
            
            # Skip if already small and is a JPEG
            if img.width <= max_size[0] and img.height <= max_size[1] and img.format == 'JPEG' and orig_size_kb < 150:
                skipped += 1
                continue
                
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Resize (maintains aspect ratio, max bounds = max_size)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to memory buffer to check new size
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=quality)
            new_data = img_byte_arr.getvalue()
            
            # Overwrite original file
            with open(filepath, 'wb') as f:
                f.write(new_data)
                
            processed += 1
            if processed % 100 == 0:
                logging.info(f"Processed {processed}/{total} images...")
                
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            errors += 1

    logging.info(f"--- Process Complete ---")
    logging.info(f"Successfully resized & compressed: {processed} images")
    logging.info(f"Skipped (already optimized): {skipped} images")
    logging.info(f"Errors: {errors} images")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "data", "raw_images")
    
    # Run the resizing process
    resize_existing_images(target_dir)
