import os
import shutil

base_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR"
cashier_path = os.path.join(base_dir, 'routes', 'cashier.py')
atencion_path = os.path.join(base_dir, 'routes', 'atencion.py')
clientes_template_old = os.path.join(base_dir, 'templates', 'caja', 'clientes.html')
clientes_template_new = os.path.join(base_dir, 'templates', 'atencion', 'clientes.html')

with open(cashier_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("@cashier_bp.route('/clientes', methods=['GET'])")
end_idx = content.find("@cashier_bp.route('/emision_factura', methods=['GET', 'POST'])")

if start_idx != -1 and end_idx != -1:
    clientes_routes = content[start_idx:end_idx]
    
    # Remove from cashier
    cashier_kept = content[:start_idx] + content[end_idx:]
    with open(cashier_path, 'w', encoding='utf-8') as f:
        f.write(cashier_kept)
        
    # Process for atencion
    clientes_routes = clientes_routes.replace('@cashier_bp', '@atencion_bp')
    clientes_routes = clientes_routes.replace("url_for('cashier.clientes_list')", "url_for('atencion.clientes_list')")
    clientes_routes = clientes_routes.replace("render_template('caja/clientes.html'", "render_template('atencion/clientes.html'")
    clientes_routes = clientes_routes.replace("session.get('rol_id') not in [1, 2, 5]", "session.get('rol_id') not in [1, 5, 1008]")
    
    # Append to atencion
    with open(atencion_path, 'a', encoding='utf-8') as f:
        f.write('\n' + clientes_routes)
        
    print("Routes moved to atencion.py")
    
    # Move template
    if os.path.exists(clientes_template_old):
        shutil.move(clientes_template_old, clientes_template_new)
        print("Template moved to atencion folder")
else:
    print("Routes not found")
