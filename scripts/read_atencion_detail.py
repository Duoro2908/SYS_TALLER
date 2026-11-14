with open(r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py', 'r', encoding='utf-8') as f:
    text = f.read()

def show_block(header, max_chars=1500):
    idx = text.find(header)
    if idx != -1:
        print(f"=== {header} ===")
        print(text[idx:idx+max_chars])
    else:
        print(f"Header not found: {header}")

show_block("@atencion_bp.route('/citas_whatsapp',")
show_block("@atencion_bp.route('/clientes',")
