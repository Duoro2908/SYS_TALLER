import sys
sys.path.insert(0, '.')
from app import app

def run_tests():
    print("Iniciando pruebas de integración...")
    client = app.test_client()

    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['username'] = 'admin'
        sess['rol_id'] = 1  # Superadmin
        sess['rol_nombre'] = 'Super Administrador'
        sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'

    rutas_a_probar = [
        ('/', "Dashboard Superadmin Principal"),
        ('/contador/balance', "Balance General (MiPyME)"),
        ('/contador/estado_resultados', "Estado de Resultados (MiPyME)"),
        ('/contador/historial_finanzas', "Historial de Finanzas (12 Meses y Razones)"),
        ('/contador/historial_finanzas?mes=11&anio=2026', "Historial Noviembre 2026"),
        ('/contador/historial_finanzas?mes=11&anio=2026&ver_vivo=1', "Historial Noviembre 2026 (En Vivo)"),
        ('/contador/razones', "Razones Financieras"),
        ('/admin/rrhh/empleados', "RRHH Empleados"),
        ('/bodega/inventario', "Bodega Inventario")
    ]

    errores = 0
    for ruta, nombre in rutas_a_probar:
        try:
            resp = client.get(ruta, follow_redirects=True)
            if resp.status_code == 200:
                print(f"[OK 200] {nombre} ({ruta})")
            else:
                print(f"[FAIL {resp.status_code}] {nombre} ({ruta})")
                errores += 1
        except Exception as e:
            print(f"[ERROR] {nombre} ({ruta}): {e}")
            errores += 1

    if errores == 0:
        print("\n>>> TODAS LAS PRUEBAS PASARON EXITOSAMENTE (0 ERRORES) <<<")
    else:
        print(f"\n>>> SE ENCONTRARON {errores} ERRORES <<<")

if __name__ == '__main__':
    run_tests()
