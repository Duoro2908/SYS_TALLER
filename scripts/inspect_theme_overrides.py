with open('static/css/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'data-theme="light"' in line or 'data-theme' in line or 'Recursos' in line or 'Bodega' in line:
        print(f"{i+1}: {line.strip()}")

