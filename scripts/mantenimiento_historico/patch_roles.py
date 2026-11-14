import os
import re

routes_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes"

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Rule 1: Replace != 2 with not in [1, 2, 5] (Since usually 5 is gerente and 1 is admin)
    # Actually, let's just make it not in [1, 2] if it was strictly != 2.
    content = re.sub(r"session\.get\('rol_id'\)\s*!=\s*2", "session.get('rol_id') not in [1, 2]", content)

    # Rule 2: Replace not in (4, 6) with not in (1, 4, 6)
    content = re.sub(r"session\.get\('rol_id'\)\s*not in\s*\(\s*4\s*,\s*6\s*\)", "session.get('rol_id') not in (1, 4, 6)", content)

    # Rule 3: Replace not in [3, 5] with not in [1, 3, 5]
    content = re.sub(r"session\.get\('rol_id'\)\s*not in\s*\[\s*3\s*,\s*5\s*\]", "session.get('rol_id') not in [1, 3, 5]", content)
    
    # Rule 4: Replace not in [1, 3] with not in [1, 3, 5] just in case we need consistency, but 1 is already there.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched {filepath}")

for filename in os.listdir(routes_dir):
    if filename.endswith(".py"):
        patch_file(os.path.join(routes_dir, filename))

print("Patching complete.")
