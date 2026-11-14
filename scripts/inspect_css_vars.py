with open('static/css/styles.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
root_match = re.search(r':root.*?\n\}', text, re.DOTALL)
if root_match:
    print(root_match.group(0))

dark_match = re.search(r'\[data-theme="dark"\].*?\n\}', text, re.DOTALL)
if dark_match:
    print('--- DARK ---')
    print(dark_match.group(0))

