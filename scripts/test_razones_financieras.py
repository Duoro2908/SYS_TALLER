import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from routes.contador import calcular_motor_razones_financieras, safe_div

def test_safe_div():
    print("=== TEST 1: SAFE DIVISION ===")
    assert safe_div(10, 0) == 0.0
    assert safe_div(10, None) == 0.0
    assert safe_div(None, 10) == 0.0
    assert safe_div(10, 2) == 5.0
    assert safe_div(10, 3) == 3.33
    print("safe_div: OK")

def test_motor_razones_financieras_with_zeros():
    print("\n=== TEST 2: MOTOR CON DATOS VACÍOS / CEROS ===")
    datos_vacios = {}
    razones, resumen = calcular_motor_razones_financieras(datos_vacios)
    assert 'liquidez' in razones
    assert 'actividad' in razones
    assert 'endeudamiento' in razones
    assert 'rentabilidad' in razones
    assert 'cobertura' in razones
    assert resumen['total'] == 20
    assert isinstance(resumen['score'], float)
    print(f"Motor con ceros ejecutado exitosamente. Total ratios: {resumen['total']}, Score: {resumen['score']}")

def test_endpoints():
    print("\n=== TEST 3: ENDPOINTS FLASK /contador/razones Y /contador/resumen_finanzas ===")
    client = app.test_client()

    with client.session_transaction() as sess:
        sess['usuario_id'] = 6
        sess['rol_id'] = 6
        sess['username'] = 'carlos.finanzas'
        sess['nombre_completo'] = 'Carlos Rene Gavarrete Calero'

    # Test GET /contador/razones
    resp = client.get('/contador/razones?mes=10&anio=2026')
    assert resp.status_code == 200, f"Error en /contador/razones: {resp.status_code}"
    html = resp.get_data(as_text=True)

    # Verificar 5 Categorías
    assert "1. Razones de Liquidez" in html
    assert "2. Razones de Actividad o Rotación" in html
    assert "3. Razones de Endeudamiento" in html
    assert "4. Razones de Rentabilidad" in html
    assert "5. Razones de Cobertura" in html

    # Verificar Ratios clave
    assert "Razón Corriente (Liquidez General)" in html
    assert "Prueba Ácida (Liquidez Inmediata)" in html
    assert "Capital de Trabajo Neto (CTN)" in html
    assert "Rotación de Inventarios" in html
    assert "Días de Inventario (Permanencia)" in html
    assert "Rotación de Cartera" in html
    assert "Periodo Promedio de Cobro" in html
    assert "Rotación de Cuentas por Pagar" in html
    assert "Rotación de Activos Fijos" in html
    assert "Rotación de Activos Totales" in html
    assert "Nivel de Endeudamiento Total" in html
    assert "Endeudamiento a Corto Plazo" in html
    assert "Apalancamiento Financiero" in html
    assert "Margen Bruto de Utilidad" in html
    assert "Margen Operacional - EBIT" in html
    assert "Margen Neto de Utilidad" in html
    assert "ROA - Rendimiento sobre el Activo" in html
    assert "ROE - Rendimiento sobre el Patrimonio" in html
    assert "Cobertura de Intereses" in html
    assert "Cobertura Total del Servicio de la Deuda" in html

    # Verificar presencia de Semáforos
    assert "Saludable" in html or "Precaución" in html or "Crítico" in html
    assert "Meta ideal" in html or "Meta:" in html
    assert "score-dial" in html

    print("GET /contador/razones?mes=10&anio=2026: OK (Todas las 5 categorías y 20 razones renderizadas)")

    # Test GET /contador/resumen_finanzas
    resp2 = client.get('/contador/resumen_finanzas?mes=10&anio=2026')
    assert resp2.status_code == 200, f"Error en /contador/resumen_finanzas: {resp2.status_code}"
    print("GET /contador/resumen_finanzas?mes=10&anio=2026: OK")

if __name__ == '__main__':
    test_safe_div()
    test_motor_razones_financieras_with_zeros()
    test_endpoints()
    print("\n>>> TODOS LOS TESTS DE RAZONES FINANCIERAS PASARON EXITOSAMENTE <<<")
