import re

with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\auth\login.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find card-right content
match = re.search(r'<div class="card-right">([\s\S]*?)</div>\s*<!--\s*Fin', text) or re.search(r'<div class="card-right">([\s\S]*?)</div>\s*</div>\s*<!--', text)
if match:
    print(match.group(0)[:2000])
else:
    # Print the last 150 lines
    lines = text.splitlines()
    print('\n'.join(lines[-150:]))

