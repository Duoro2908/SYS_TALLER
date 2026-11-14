import ssl
import urllib.request
import os

# Patch SSL to allow downloading the model without certificate verification errors
ssl._create_default_https_context = ssl._create_unverified_context

from rembg import remove
from PIL import Image

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        input_img = Image.open(input_path)
        # remove background using rembg
        output_img = remove(input_img)
        output_img.save(output_path, "PNG")
        print(f"Saved cleanly to {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    base_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\1a095a4f-1b5f-4151-8f57-b384a3bf6d33"
    out_dir = r"C:\Users\Alexander\OneDrive\Music\Documents\Taller CR\static\img"
    
    process_image(os.path.join(base_dir, "media__1788959765864.png"), os.path.join(out_dir, "chispero_denso.png"))
    process_image(os.path.join(base_dir, "media__1788960496288.png"), os.path.join(out_dir, "chispero_ngk.png"))
    process_image(os.path.join(base_dir, "media__1788960582180.png"), os.path.join(out_dir, "chispero_champion.png"))
    
    print("All images processed with rembg.")
