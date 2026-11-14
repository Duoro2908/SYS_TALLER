with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\citas_whatsapp.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("--- Search buttons in citas_whatsapp.html ---")
matches = re.findall(r'<button[\s\S]*?</button>', text)
for m in matches[:10]:
    first_line = m.splitlines()[0]
    print(" ", first_line[:100])

print("\n--- Search modals in citas_whatsapp.html ---")
modals = re.findall(r'id=\"[^\"]*modal[^\"]*\"', text, re.IGNORECASE)
print(modals)
