import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

def test_endpoints():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['rol_id'] = 1
        sess['usuario_nombre'] = 'Elvin Alexander Mendez Cruz'
        sess['rol_nombre'] = 'Super Administrador'
        
    routes_to_test = [
        ('/atencion/', 'Buzon de Atencion y Quejas'),
        ('/atencion/citas_whatsapp', 'Gestion de Citas WhatsApp'),
        ('/admin/contratos', 'Submodulo de Contratos Laborales'),
        ('/admin/planilla', 'Planilla de Pago y Nomina'),
        ('/admin/rrhh/registro_mensual', 'Registro Mensual y Cierres de Nomina'),
        ('/contador/razones', 'Razones Financieras'),
        ('/contador/historial_finanzas', 'Historial Financiero'),
        ('/contador/balance', 'Balance General MiPyME'),
        ('/contador/estado_resultados', 'Estado de Resultados MiPyME')
    ]
    
    print("Iniciando pruebas de carga de rutas...")
    all_ok = True
    for route, name in routes_to_test:
        try:
            res = client.get(route)
            status = res.status_code
            print(f"[{'PASS' if status == 200 else 'FAIL'}] {name} ({route}) -> HTTP {status}")
            if status != 200:
                all_ok = False
        except Exception as e:
            print(f"[ERROR] {name} ({route}) -> Excepción: {e}")
            all_ok = False
            
    if all_ok:
        print("\nTodas las rutas verificadas exitosamente con HTTP 200 OK.")
    else:
        print("\nSe encontraron fallas en algunas rutas.")

if __name__ == '__main__':
    test_endpoints()
