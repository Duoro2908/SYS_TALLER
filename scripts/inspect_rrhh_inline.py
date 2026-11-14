with open('templates/admin/empleados_rrhh.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'style="[^"]*?(?:color|background)[^"]*?"', text)
for m in matches[:25]:
    print(m)

