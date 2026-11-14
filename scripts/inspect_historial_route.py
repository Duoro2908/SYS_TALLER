with open('routes/contador.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
idx = text.find("def historial_finanzas")
print(text[idx:idx+1200])

