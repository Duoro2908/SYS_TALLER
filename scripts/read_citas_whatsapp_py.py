with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("def citas_whatsapp():")
print(text[idx:idx+2000])
