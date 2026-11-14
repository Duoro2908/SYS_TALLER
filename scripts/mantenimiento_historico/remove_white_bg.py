from PIL import Image
import os

def remove_white_bg(input_path, output_path, tolerance=30):
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # Check if the pixel is close to white
        # White is (255, 255, 255)
        if item[0] >= 255 - tolerance and item[1] >= 255 - tolerance and item[2] >= 255 - tolerance:
            # Change to transparent
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Saved {output_path}")

base_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\1a095a4f-1b5f-4151-8f57-b384a3bf6d33"
out_dir = r"C:\Users\Alexander\OneDrive\Music\Documents\Taller CR\static\img"

remove_white_bg(os.path.join(base_dir, "media__1788959765864.png"), os.path.join(out_dir, "chispero_denso.png"), tolerance=40)
remove_white_bg(os.path.join(base_dir, "media__1788960496288.png"), os.path.join(out_dir, "chispero_ngk.png"), tolerance=40)
remove_white_bg(os.path.join(base_dir, "media__1788960582180.png"), os.path.join(out_dir, "chispero_champion.png"), tolerance=40)

print("Images processed.")
