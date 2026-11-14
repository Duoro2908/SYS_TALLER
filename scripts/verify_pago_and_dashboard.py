import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['rol'] = 1
    sess['username'] = 'elvin.admin'
    sess['nombre_usuario'] = 'elvin.admin'

print("==================================================================")
print("1. VERIFICACIÓN DEL DASHBOARD - 10 USUARIOS/COLABORADORES")
print("==================================================================")
resp = client.get('/api/dashboard/stats')
assert resp.status_code == 200
data = json.loads(resp.data.decode('utf-8'))
print(f"Stats en vivo: usuarios = {data.get('usuarios')}, productos = {data.get('productos')}, ordenes = {data.get('ordenes')}")
assert data.get('usuarios') == 10, f"Error: Se esperaban 10 usuarios, se obtuvo {data.get('usuarios')}"
print("[PASS] Dashboard muestra exactamente 10 colaboradores activos en el taller.")

resp_root = client.get('/')
assert resp_root.status_code == 200
html_root = resp_root.data.decode('utf-8')
assert '10 Colaboradores Activos en Nómina' in html_root or 'id="statUsuarios">10' in html_root
print("[PASS] Vista HTML del Dashboard renderiza 10 usuarios en el KPI card.")

print("\n==================================================================")
print("2. VERIFICACIÓN DE COLILLA EN ESTADO NO PAGADO (TODO EN C$ 0.00)")
print("==================================================================")
# Asegurar que el empleado 2 esté en estado no pagado
client.post('/admin/planilla/toggle_pago', 
            data=json.dumps({'usuario_id': 2, 'pagado': False}),
            content_type='application/json')

resp_col_unpaid = client.get('/admin/planilla/colilla/2')
assert resp_col_unpaid.status_code == 200
html_col_unpaid = resp_col_unpaid.data.decode('utf-8')
assert 'PAGO PENDIENTE DE AUTORIZACIÓN (C$ 0.00)' in html_col_unpaid
assert 'Salario Neto Líquido a Pagar' in html_col_unpaid
assert 'C$ 0.00' in html_col_unpaid
assert 'Autorizar y Pagar Ahora' in html_col_unpaid
print("[PASS] Colilla de empleado sin pagar muestra montos en C$ 0.00 y banner de pendiente.")

print("\n==================================================================")
print("3. VERIFICACIÓN DE PAGO Y CÁLCULO PRECISO EN COLILLA")
print("==================================================================")
resp_toggle = client.post('/admin/planilla/toggle_pago', 
                          data=json.dumps({'usuario_id': 2, 'pagado': True}),
                          content_type='application/json')
assert resp_toggle.status_code == 200
toggle_res = json.loads(resp_toggle.data.decode('utf-8'))
emp2 = toggle_res.get('empleado', {})
print(f"Empleado 2 pagado: Bruto = C$ {emp2.get('salario_bruto')}, INSS = C$ {emp2.get('inss_laboral')}, IR = C$ {emp2.get('ir')}, Neto = C$ {emp2.get('salario_neto')}")
assert emp2.get('salario_neto') > 0

resp_col_paid = client.get('/admin/planilla/colilla/2')
assert resp_col_paid.status_code == 200
html_col_paid = resp_col_paid.data.decode('utf-8')
assert 'DESEMBOLSO AUTORIZADO Y PAGADO' in html_col_paid
assert 'Revertir a No Pagado' in html_col_paid
assert f"C$ {emp2.get('salario_neto'):,.2f}" in html_col_paid
print(f"[PASS] Colilla pagada calculó y renderizó salario neto: C$ {emp2.get('salario_neto'):,.2f}")

# Revertir para mantener estado limpio
client.post('/admin/planilla/toggle_pago', 
            data=json.dumps({'usuario_id': 2, 'pagado': False}),
            content_type='application/json')

print("\n==================================================================")
print("4. VERIFICACIÓN DEL SUBMÓDULO REGISTRO MENSUAL Y CIERRE MANUAL")
print("==================================================================")
resp_reg = client.get('/admin/rrhh/registro_mensual?mes=10&anio=2026')
assert resp_reg.status_code == 200
html_reg = resp_reg.data.decode('utf-8')
assert 'Registro Mensual y Cierre de Nómina' in html_reg
assert 'Realizar Cierre de Mes (Manual)' in html_reg
print("[PASS] Submódulo Registro Mensual cargó exitosamente.")

# Ejecutar cierre manual del mes
resp_cierre = client.post('/admin/rrhh/ejecutar_cierre', data={
    'mes': 10,
    'anio': 2026,
    'observaciones': 'Cierre manual ejecutado por auditoría de prueba'
})
assert resp_cierre.status_code == 200
cierre_json = json.loads(resp_cierre.data.decode('utf-8'))
assert cierre_json.get('success') is True
print(f"[PASS] Cierre manual ejecutado: {cierre_json.get('message')}")

# Verificar que ahora el mes está marcado como cerrado en la vista
resp_reg_closed = client.get('/admin/rrhh/registro_mensual?mes=10&anio=2026')
assert resp_reg_closed.status_code == 200
html_reg_closed = resp_reg_closed.data.decode('utf-8')
assert 'Cierre Mensual Registrado (Cerrado)' in html_reg_closed
assert 'Imprimir Acta Oficial de Cierre' in html_reg_closed

# Obtener ID del cierre creado
from database import get_db_connection
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT CierreID FROM CierresMensualesNomina WHERE Mes = 10 AND Anio = 2026")
cierre_id = cur.fetchone()[0]
conn.close()

# Verificar Acta Oficial
resp_acta = client.get(f'/admin/rrhh/acta_cierre/{cierre_id}')
assert resp_acta.status_code == 200
html_acta = resp_acta.data.decode('utf-8')
assert 'ACTA OFICIAL DE CIERRE MENSUAL DE NÓMINA' in html_acta
print(f"[PASS] Acta Oficial de Cierre #{cierre_id} generada y renderizada con éxito.")

# Reabrir el cierre
resp_reabrir = client.post(f'/admin/rrhh/reabrir_cierre/{cierre_id}')
assert resp_reabrir.status_code == 200
reabrir_json = json.loads(resp_reabrir.data.decode('utf-8'))
assert reabrir_json.get('success') is True
print("[PASS] Período reabierto correctamente.")

print("\n==================================================================")
print("¡TODAS LAS PRUEBAS DE CALIDAD MUNDIAL PASARON AL 100%!")
print("==================================================================")
