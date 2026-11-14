with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("def cambiar_estado_cita")
print(text[idx:idx+800])
