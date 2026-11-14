with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "return render_template('atencion/citas_whatsapp.html'" in l:
        print("".join(lines[i-15:i+10]))
        break
