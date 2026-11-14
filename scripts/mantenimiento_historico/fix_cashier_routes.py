import os

base_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR"
atencion_path = os.path.join(base_dir, 'routes', 'atencion.py')
cashier_path = os.path.join(base_dir, 'routes', 'cashier.py')

with open(atencion_path, 'r', encoding='utf-8') as f:
    atencion_content = f.read()

# Find where ventas_recibidas starts
idx = atencion_content.find("@atencion_bp.route('/ventas_recibidas')")

if idx != -1:
    ventas_routes = atencion_content[idx:]
    atencion_kept = atencion_content[:idx]
    
    # Save atencion.py
    with open(atencion_path, 'w', encoding='utf-8') as f:
        f.write(atencion_kept.strip() + '\n')
        
    # Fix the routes
    ventas_routes = ventas_routes.replace('@atencion_bp', '@cashier_bp')
    # url_for might have been wrongly changed?
    # the migrate script did:
    # whatsapp_routes = whatsapp_routes.replace("url_for('cashier.index')", "url_for('atencion.index')")
    # let's just make sure it uses 'cashier.index'
    ventas_routes = ventas_routes.replace("url_for('atencion.index')", "url_for('cashier.index')")
    
    with open(cashier_path, 'a', encoding='utf-8') as f:
        f.write('\n' + ventas_routes + '\n')
        
    print("Routes moved back to cashier.py successfully.")
else:
    print("Not found.")
