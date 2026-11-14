import os
import re
import shutil

def migrate():
    base_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR"
    cashier_path = os.path.join(base_dir, 'routes', 'cashier.py')
    atencion_path = os.path.join(base_dir, 'routes', 'atencion.py')
    template_old = os.path.join(base_dir, 'templates', 'caja', 'citas_whatsapp.html')
    template_new = os.path.join(base_dir, 'templates', 'atencion', 'citas_whatsapp.html')
    
    with open(cashier_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extraer las rutas desde @cashier_bp.route('/citas_whatsapp'... hasta el final del archivo
    # Buscamos la línea: @cashier_bp.route('/citas_whatsapp', methods=['GET'])
    idx = content.find("@cashier_bp.route('/citas_whatsapp', methods=['GET'])")
    if idx == -1:
        print("Routes already migrated?")
        return
        
    whatsapp_routes = content[idx:]
    cashier_kept = content[:idx]
    
    with open(cashier_path, 'w', encoding='utf-8') as f:
        f.write(cashier_kept.strip() + '\n')
        
    # Adaptar las rutas para atencion_bp
    whatsapp_routes = whatsapp_routes.replace('@cashier_bp', '@atencion_bp')
    whatsapp_routes = whatsapp_routes.replace("url_for('cashier.citas_whatsapp')", "url_for('atencion.citas_whatsapp')")
    whatsapp_routes = whatsapp_routes.replace("url_for('cashier.index')", "url_for('atencion.index')")
    whatsapp_routes = whatsapp_routes.replace("render_template('caja/citas_whatsapp.html'", "render_template('atencion/citas_whatsapp.html'")
    whatsapp_routes = whatsapp_routes.replace("session.get('rol_id') not in [1, 2, 5]", "session.get('rol_id') not in [1, 5, 8]")
    
    # Needs to import OFFICIAL_PHONE_NUMBER and process_incoming_whatsapp_message if not imported in atencion.py
    imports_to_add = """
import datetime
from flask import jsonify
from bot.whatsapp_bot import process_incoming_whatsapp_message, OFFICIAL_PHONE_NUMBER
"""
    
    with open(atencion_path, 'r', encoding='utf-8') as f:
        atencion_content = f.read()
        
    with open(atencion_path, 'w', encoding='utf-8') as f:
        # Añadir imports al principio
        atencion_content = atencion_content.replace("from database import get_db_connection", "from database import get_db_connection\n" + imports_to_add)
        f.write(atencion_content + '\n' + whatsapp_routes)
        
    # Mover template
    if os.path.exists(template_old):
        shutil.move(template_old, template_new)
        
    # Actualizar base.html
    base_html = os.path.join(base_dir, 'templates', 'base.html')
    with open(base_html, 'r', encoding='utf-8') as f:
        base = f.read()
        
    base = base.replace(
        "<span>Tickets & Soporte</span>",
        "<span>Sugerencias y Quejas</span>\n                    </a>\n                </li>\n                <li>\n                    <a href=\"{{ url_for('atencion.citas_whatsapp') }}\">\n                        <i class=\"fa-brands fa-whatsapp\" style=\"color: #25D366;\"></i>\n                        <span>Citas WhatsApp</span>"
    )
    with open(base_html, 'w', encoding='utf-8') as f:
        f.write(base)
        
    print("Migración completada.")

if __name__ == '__main__':
    migrate()
