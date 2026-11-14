import os, re

for folder in ['templates', 'routes']:
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(('.html', '.py')):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    c = fl.read()
                matches = list(re.finditer(r'\bexpress\b', c, re.IGNORECASE))
                if matches:
                    print(f"File {p}: {len(matches)} matches")
                    for m in matches:
                        s = max(0, m.start() - 40)
                        e = min(len(c), m.end() + 40)
                        print(f"  L{c[:m.start()].count(chr(10))+1}: {c[s:e].replace(chr(10), ' ')}")

