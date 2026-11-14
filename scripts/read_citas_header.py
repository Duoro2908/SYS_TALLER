with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\atencion\citas_whatsapp.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('<div class="wa-header">')
print(text[idx1:idx1+1800].encode('ascii', errors='replace').decode('ascii'))
