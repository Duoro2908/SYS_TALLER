with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\citas_whatsapp.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Check where the end of the body or end of file is
print("File length:", len(text))
idx_actions = text.find('<div class="cita-actions">')
print("Found cita-actions at:", idx_actions)
if idx_actions != -1:
    print(text[idx_actions:idx_actions+1200].encode('ascii', errors='replace').decode('ascii'))
