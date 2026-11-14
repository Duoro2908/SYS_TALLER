import shutil
import os

base_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\1a095a4f-1b5f-4151-8f57-b384a3bf6d33"
out_dir = r"C:\Users\Alexander\OneDrive\Music\Documents\Taller CR\static\img"

# Simply copy the original images, preserving their original white backgrounds
shutil.copy(os.path.join(base_dir, "media__1788959765864.png"), os.path.join(out_dir, "chispero_denso.png"))
shutil.copy(os.path.join(base_dir, "media__1788960496288.png"), os.path.join(out_dir, "chispero_ngk.png"))
shutil.copy(os.path.join(base_dir, "media__1788960582180.png"), os.path.join(out_dir, "chispero_champion.png"))

print("Original high-quality images restored.")
