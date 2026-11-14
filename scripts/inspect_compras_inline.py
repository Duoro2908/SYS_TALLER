with open('templates/bodega/compras.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'style="[^"]*?(?:color|background)[^"]*?"', text)
for m in matches:
    print(m)

