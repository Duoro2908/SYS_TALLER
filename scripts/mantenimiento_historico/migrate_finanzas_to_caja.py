import os
import shutil
import re

base_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR"
contador_path = os.path.join(base_dir, 'routes', 'contador.py')
cashier_path = os.path.join(base_dir, 'routes', 'cashier.py')

with open(contador_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract facturas
facturas_start = content.find("@contador_bp.route('/facturas')")
facturas_end = content.find("@contador_bp.route('/cierres')")
facturas_route = content[facturas_start:facturas_end]

# Extract cierres
cierres_start = facturas_end
cierres_end = content.find("@contador_bp.route('/balance', methods=['GET', 'POST'])")
cierres_route = content[cierres_start:cierres_end]

if facturas_start != -1 and cierres_start != -1:
    # Remove from contador
    contador_kept = content[:facturas_start] + content[cierres_end:]
    with open(contador_path, 'w', encoding='utf-8') as f:
        f.write(contador_kept)
        
    def transform_route(route):
        route = route.replace('@contador_bp', '@cashier_bp')
        route = route.replace('@contador_required\n', '')
        # add auth check
        auth_check = "    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5]:\n        return redirect(url_for('auth.login'))\n"
        route = re.sub(r'(def \w+\(\):\n)', r'\1' + auth_check, route)
        route = route.replace("render_template('contador/facturas.html'", "render_template('caja/facturas.html'")
        route = route.replace("render_template('contador/cierres.html'", "render_template('caja/cierres.html'")
        return route
        
    facturas_route = transform_route(facturas_route)
    cierres_route = transform_route(cierres_route)
    
    with open(cashier_path, 'a', encoding='utf-8') as f:
        f.write('\n' + facturas_route + cierres_route)
        
    print("Routes moved to cashier.py")
    
    # Move templates
    try:
        shutil.move(os.path.join(base_dir, 'templates', 'contador', 'facturas.html'), os.path.join(base_dir, 'templates', 'caja', 'facturas.html'))
    except Exception as e:
        print(e)
    try:
        shutil.move(os.path.join(base_dir, 'templates', 'contador', 'cierres.html'), os.path.join(base_dir, 'templates', 'caja', 'cierres.html'))
    except Exception as e:
        print(e)
    print("Templates moved")
else:
    print("Routes not found")
