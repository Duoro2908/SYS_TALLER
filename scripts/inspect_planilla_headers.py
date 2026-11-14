with open('templates/admin/planilla.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'<h[1-3][^>]*?style="[^"]*?"[^>]*?>', text)
for m in matches:
    print(m)

