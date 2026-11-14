with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\citas_whatsapp.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of citas_whatsapp.html:", len(text))
lines = text.splitlines()
print("\nFirst 40 lines:")
print("\n".join(lines[:40]))
