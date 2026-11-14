with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\clientes.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of clientes.html:", len(text))
print("First 800 chars:")
print(text[:800])
