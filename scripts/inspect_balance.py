path = r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\contador\estado_resultados.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in estado_resultados.html: {len(lines)}")
for i, line in enumerate(lines):
    if '{% block' in line or '{% endblock' in line:
        print(f"Line {i+1}: {line.strip()}")
