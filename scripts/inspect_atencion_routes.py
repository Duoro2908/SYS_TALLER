with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print(f"Total lines in routes/atencion.py: {len(lines)}")
routes = [l for l in lines if l.strip().startswith('@atencion_bp.route')]
for r in routes:
    print("  ", r)
