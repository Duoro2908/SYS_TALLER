with open('templates/contador/balance.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length of balance.html:", len(text))
matches = re.findall(r'pyme', text, re.IGNORECASE)
print("Occurrences of pyme in balance.html:", len(matches))

with open('templates/contador/estado_resultados.html', 'r', encoding='utf-8') as f:
    text_er = f.read()
matches_er = re.findall(r'pyme', text_er, re.IGNORECASE)
print("Occurrences of pyme in estado_resultados.html:", len(matches_er))

