import sys
sys.path.insert(0, '.')
from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['nombre'] = 'Super Administrador'
    sess['username'] = 'admin'

routes_all = [
    # Dashboard / Gerencia
    ('/', 'Home / Redir'),
    ('/dashboard', 'Dashboard'),
    ('/gerencia/estadisticas', 'Estadísticas Gerencia'),
    # Atencion al cliente
    ('/atencion/', 'Atención Sugerencias'),
    ('/atencion/clientes', 'Clientes'),
    ('/atencion/gestion_citas', 'Gestión Citas'),
    ('/atencion/citas_whatsapp', 'Citas WhatsApp'),
    # Taller
    ('/mecanico/citas_programadas', 'Taller Citas'),
    ('/mecanico/ordenes', 'Órdenes de Trabajo'),
    # Caja
    ('/caja/ventas_recibidas', 'Ventas Recibidas'),
    ('/caja/ordenes_taller', 'Órdenes Taller Caja'),
    ('/caja/facturas', 'Facturas Emitidas'),
    ('/caja/cierres', 'Control de Cajas'),
    # Finanzas
    ('/contador/razones', 'Razones Financieras'),
    ('/contador/historial_finanzas', 'Historial Finanzas'),
    # Contabilidad
    ('/contador/balance', 'Balance General'),
    ('/contador/estado_resultados', 'Estado de Resultados'),
    ('/contador/historial', 'Historial Contabilidad'),
    # Mercadotecnia
    ('/mercadotecnia/participantes', 'Mkt Participantes'),
    ('/mercadotecnia/premios', 'Mkt Premios'),
    ('/mercadotecnia/resumen', 'Mkt Resumen'),
]

errors = []
for url, label in routes_all:
    try:
        res = client.get(url, follow_redirects=True)
        print(f"[{label}] ({url}) -> Status: {res.status_code}")
        if res.status_code != 200:
            errors.append((label, url, res.status_code))
    except Exception as e:
        print(f"EXCEPTION in [{label}] ({url}): {e}")
        errors.append((label, url, str(e)))

if not errors:
    print("\n>>> ALL SYSTEM MODULES TESTED AND RETURNED 200 OK! <<<")
else:
    print(f"\nErrors found: {errors}")

