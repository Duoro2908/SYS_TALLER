with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('/citas_whatsapp/estado/')
print(text[idx-50:idx+600])
