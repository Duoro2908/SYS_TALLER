with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\citas_whatsapp.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'{% for c in citas %}[\s\S]*?{% endfor %}', text)
if match:
    print(match.group(0)[:1500])
else:
    print("Loop not found")
