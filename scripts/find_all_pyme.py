import os
import re

for f in os.listdir('templates/contador'):
    if f.endswith('.html'):
        p = os.path.join('templates/contador', f)
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        m = re.findall(r'.{0,30}pyme.{0,30}', c, re.IGNORECASE)
        if m:
            print(f"=== {f} ===")
            for match in m:
                print("  ", match.strip())

