with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\clientes.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
table_match = re.search(r'<table[\s\S]*?</table>', text)
if table_match:
    print(table_match.group(0)[:2000])
else:
    print("Table not found")
