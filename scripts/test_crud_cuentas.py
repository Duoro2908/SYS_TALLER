import sys
sys.path.insert(0, '.')
from app import app
from routes.contador import obtener_datos_financieros_taller
import database

def test_crud():
    print("Probando CRUD de cuentas contables...")
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['username'] = 'admin'
        sess['rol_id'] = 1
        sess['rol_nombre'] = 'Super Administrador'

    # 1. Agregar Cuenta al Balance
    res = client.post('/contador/agregar_cuenta', data={
        'tipo_reporte': 'Balance',
        'mes': 11,
        'anio': 2026,
        'categoria': 'Activo Corriente',
        'nombre_cuenta': 'Inversiones Temporales Bancarias',
        'monto': '15000.00'
    }, follow_redirects=True)
    assert res.status_code == 200, f"Error al agregar cuenta: {res.status_code}"
    print("[OK] Cuenta agregada al Balance General")

    # 2. Verificar datos financieros calculados y cuadre
    datos = obtener_datos_financieros_taller(mes=11, anio=2026)
    print(f"Total Activos: C$ {datos['activo_total']:,.2f}")
    print(f"Total Pasivos + Patrimonio: C$ {datos['pasivo_mas_patrimonio']:,.2f}")
    print(f"Diferencia de Cuadre: C$ {datos['diferencia_cuadre']:,.2f} (Cuadra: {datos['cuadra']})")
    assert datos['cuadra'], "¡El balance no cuadra después del ajuste!"

    # 3. Consultar ID en BD y Eliminar
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT AjusteID FROM CuentasContablesAjustes WHERE NombreCuenta = 'Inversiones Temporales Bancarias'")
    row = cur.fetchone()
    assert row is not None, "No se encontró el registro en CuentasContablesAjustes"
    ajuste_id = row[0]
    conn.close()

    res_del = client.post(f'/contador/eliminar_cuenta/{ajuste_id}', data={
        'tipo_reporte': 'Balance',
        'mes': 11,
        'anio': 2026
    }, follow_redirects=True)
    assert res_del.status_code == 200, f"Error al eliminar cuenta: {res_del.status_code}"
    print("[OK] Cuenta eliminada correctamente y balance verificado")
    print("\n>>> PRUEBA CRUD CUENTAS CONTABLES EXITOSA <<<")

if __name__ == '__main__':
    test_crud()

