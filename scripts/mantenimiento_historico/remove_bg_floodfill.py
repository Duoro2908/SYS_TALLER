import sys
import os
from PIL import Image

def remove_white_bg_floodfill(input_path, output_path, tolerance=15):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # The start pixel is (0,0)
    bg_color = pixels[0, 0]
    
    # We only care about RGB distance
    def is_similar(p1, p2, tol):
        return abs(p1[0] - p2[0]) <= tol and abs(p1[1] - p2[1]) <= tol and abs(p1[2] - p2[2]) <= tol

    # Find all contiguous background pixels using BFS
    visited = set()
    queue = [(0, 0)]
    
    # Also start from all 4 corners to be safe, if they are similar to bg_color
    corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
    for c in corners:
        if is_similar(pixels[c], bg_color, tolerance):
            queue.append(c)

    to_clear = set()

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if is_similar(pixels[x, y], bg_color, tolerance):
            to_clear.add((x, y))
            # Check neighbors
            if x > 0: queue.append((x-1, y))
            if x < width - 1: queue.append((x+1, y))
            if y > 0: queue.append((x, y-1))
            if y < height - 1: queue.append((x, y+1))

    # Apply transparency
    for x, y in to_clear:
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)

    img.save(output_path, "PNG")
    print(f"Saved {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\1a095a4f-1b5f-4151-8f57-b384a3bf6d33"
    out_dir = r"C:\Users\Alexander\OneDrive\Music\Documents\Taller CR\static\img"
    
    remove_white_bg_floodfill(os.path.join(base_dir, "media__1788959765864.png"), os.path.join(out_dir, "chispero_denso.png"))
    remove_white_bg_floodfill(os.path.join(base_dir, "media__1788960496288.png"), os.path.join(out_dir, "chispero_ngk.png"))
    remove_white_bg_floodfill(os.path.join(base_dir, "media__1788960582180.png"), os.path.join(out_dir, "chispero_champion.png"))
    print("Processed with floodfill!")
