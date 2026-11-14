import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app import app

client = app.test_client()

urls = [
    ('/', 'Dashboard Principal'),
    ('/admin/planilla', 'Recursos Humanos - Planilla'),
    ('/admin/contratos', 'Recursos Humanos - Contratos'),
    ('/admin/rrhh/registro_mensual', 'Recursos Humanos - Registro Mensual'),
    ('/admin/rrhh/empleados', 'Recursos Humanos - Personal'),
    ('/bodega/inventario', 'Bodega - Inventario'),
    ('/bodega/compras', 'Bodega - Compras'),
    ('/bodega/historial', 'Bodega - Historial'),
    ('/atencion/clientes', 'Atención - Directorio Clientes'),
    ('/atencion/citas_whatsapp', 'Atención - Citas WhatsApp'),
    ('/atencion/gestion_citas', 'Atención - Gestión de Citas'),
    ('/mecanico/ordenes', 'Taller - Órdenes de Trabajo'),
    ('/mecanico/citas_programadas', 'Taller - Citas Programadas'),
    ('/caja/', 'Caja - Panel'),
    ('/caja/facturas', 'Caja - Facturas'),
    ('/contador/balance', 'Contabilidad - Balance General'),
    ('/contador/estado_resultados', 'Contabilidad - Estado de Resultados'),
    ('/contador/historial', 'Contabilidad - Historial Mensual'),
    ('/mercadotecnia/resumen', 'Mercadotecnia - Dinámicas'),
    ('/integrantes', 'Integrantes del Proyecto'),
]

all_ok = True
for url, name in urls:
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['user_id'] = 1
        sess['rol_id'] = 1
        sess['username'] = 'elvin.admin'
        sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'
        sess['rol_nombre'] = 'Super Administrador'
        
    res = client.get(url, follow_redirects=True)
    has_toggle = 'id="theme-toggle"' in res.text
    has_anti_flicker = 'Anti-flicker theme loader' in res.text
    status = res.status_code
    print(f"[{status}] {name} ({url}) -> ThemeToggle: {has_toggle}, AntiFlicker: {has_anti_flicker}")
    if status != 200 or not has_toggle or not has_anti_flicker:
        all_ok = False

print("\n=== RESULTADO GENERAL ===")
if all_ok:
    print("¡EXITO TOTAL! Todos los módulos cargaron 100% OK con botón de cambio de tema y anti-flicker.")
else:
    print("Se detectaron fallos en algunos módulos.")
