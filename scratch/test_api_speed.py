import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = app.test_client()

# Simulate a logged in user with session
with client.session_transaction() as sess:
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'
    sess['username'] = 'admin'

tipos = ['caja', 'cobrar', 'inventario', 'credito_iva', 'compras', 'debito_iva', 'retenciones_dgi', 'obligaciones_laborales', 'facturas']

for t in tipos:
    t0 = time.time()
    resp = client.get(f'/contador/api/detalle_transacciones?tipo={t}&mes=11&anio=2026')
    elapsed = time.time() - t0
    data = resp.get_json() if resp.status_code == 200 else resp.data.decode('utf-8')
    item_count = len(data.get('items', [])) if isinstance(data, dict) else 'error'
    print(f"Tipo: {t:22} | Status: {resp.status_code} | Time: {elapsed:.3f}s | Items: {item_count}")

