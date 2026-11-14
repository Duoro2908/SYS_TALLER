import sys
sys.path.insert(0, '.')
from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['nombre'] = 'Super Administrador'
    sess['username'] = 'admin'

routes_to_test = [
    # Producción (Bodega)
    ('/bodega/compras', 'Compras y Abastecimiento'),
    ('/bodega/inventario', 'Inventario Taller'),
    ('/bodega/historial', 'Historial de Compras'),
    # Recursos Humanos
    ('/admin/rrhh/empleados', 'Administración de Personal'),
    ('/admin/planilla', 'Planilla de Pago'),
    ('/admin/contratos', 'Contratos Laborales'),
    ('/admin/planilla/registro_mensual', 'Registro Mensual'),
]

for url, label in routes_to_test:
    res = client.get(url)
    print(f"Testing [{label}] ({url}) -> Status: {res.status_code}")
    assert res.status_code == 200, f"Failed {url} with status {res.status_code}"

print("\n>>> ALL SUBMODULES IN PRODUCCION (BODEGA) AND RECURSOS HUMANOS RENDER WITH 200 OK! <<<")
