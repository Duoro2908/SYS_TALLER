with open('routes/contador.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Total lines:", len(text.splitlines()))

# Find where finanzas routes are
idx_hf = text.find("def historial_finanzas")
print("historial_finanzas starts around character:", idx_hf)
idx_end_hf = text.find("def ", idx_hf + 20)
print(text[idx_hf:idx_end_hf])

