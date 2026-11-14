import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from routes.contador import calcular_motor_razones_financieras, verificar_cierre_estados

def test_verificar_cierre_estados():
    print("=== TEST 1: VERIFICAR CIERRE DE ESTADOS ===")
    # Mes 10 de 2026 actualmente no tiene cierre contable sellado
    info = verificar_cierre_estados(10, 2026)
    assert isinstance(info, dict)
    assert 'ambos_cerrados' in info
    assert 'balance_cerrado' in info
    assert 'estado_cerrado' in info
    print(f"Estado de cierre mes 10/2026: Ambos cerrados={info['ambos_cerrados']}, Balance={info['balance_cerrado']}, Estado={info['estado_cerrado']}")
    print("verificar_cierre_estados: OK")

def test_motor_razones_unclosed():
    print("\n=== TEST 2: MOTOR CON PERÍODO NO CERRADO (DEBE APARECER EN 0) ===")
    datos = {
        'ventas_netas': 120000.0,
        'costo_ventas': 45000.0,
        'utilidad_bruta': 75000.0,
        'gastos_operativos': 35000.0,
        'utilidad_operativa': 40000.0,
        'utilidad_neta': 36000.0,
        'activo_circulante': 80000.0,
        'pasivo_circulante': 40000.0,
        'activo_total': 250000.0,
        'pasivo_total': 60000.0,
        'patrimonio': 190000.0
    }
    
    # Período cerrado = False (comportamiento estricto MiPyME)
    razones, resumen = calcular_motor_razones_financieras(datos, periodo_cerrado=False)
    assert resumen['score'] == 0.0
    assert resumen['saludable'] == 0
    assert resumen['precaucion'] == 0
    assert resumen['critico'] == 0
    assert resumen['pendientes'] == 20
    assert 'en Cero' in resumen['diagnostico']

    for cat in razones.values():
        for r in cat:
            assert r['valor_raw'] == 0.0
            assert r['estado'] == 'Pendiente'
            assert r['badge_class'] == 'pending'
            assert '0' in r['valor']

    print(f"Razones en cero verificadas: 20 razones en 0.00, score: {resumen['score']}%, diagnóstico: '{resumen['diagnostico']}'")
    print("test_motor_razones_unclosed: OK")

def test_motor_razones_closed():
    print("\n=== TEST 3: MOTOR CON PERÍODO CERRADO (CÁLCULO OFICIAL) ===")
    datos = {
        'ventas_netas': 120000.0,
        'costo_ventas': 45000.0,
        'utilidad_bruta': 75000.0,
        'gastos_operativos': 35000.0,
        'utilidad_operativa': 40000.0,
        'utilidad_neta': 36000.0,
        'activo_circulante': 80000.0,
        'pasivo_circulante': 40000.0,
        'activo_total': 250000.0,
        'pasivo_total': 60000.0,
        'patrimonio': 190000.0
    }
    razones, resumen = calcular_motor_razones_financieras(datos, periodo_cerrado=True)
    assert resumen['score'] > 0
    rc = next(r for r in razones['liquidez'] if r['id'] == 'razon_corriente')
    assert rc['valor_raw'] == 2.0
    assert rc['valor'] == '2.00x'
    assert rc['estado'] == 'Saludable'
    print(f"Cálculo cerrado verificado: Razón corriente = {rc['valor']}, score = {resumen['score']}%")
    print("test_motor_razones_closed: OK")

def test_endpoints_unclosed_vs_simulacion():
    print("\n=== TEST 4: ENDPOINTS /contador/razones Y /contador/resumen_finanzas ===")
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1010
        sess['rol_id'] = 6
        sess['username'] = 'carlos.finanzas'
        sess['nombre_completo'] = 'Carlos Rene Gavarrete Calero'

    # 1. Razones oficiales (mes no cerrado -> valores en 0)
    resp = client.get('/contador/razones?mes=10&anio=2026')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'Razones Financieras en Cero (0.00)' in html
    assert 'Período Pendiente de Cierre Contable Oficial' in html
    assert '0%' in html
    assert 'En Cero (Pendientes)' in html
    assert 'Activar Modo Simulación' in html or 'Simulación Preliminar' in html

    # 2. Razones con modo simulación preliminar
    resp_sim = client.get('/contador/razones?mes=10&anio=2026&ver_simulacion=1')
    assert resp_sim.status_code == 200
    html_sim = resp_sim.get_data(as_text=True)
    assert 'Modo Simulación Preliminar' in html_sim
    assert 'Volver a Modo Oficial (En 0)' in html_sim or 'Ver Cifras Oficiales (En 0)' in html_sim

    # 3. Resumen de finanzas automatizado
    resp_res = client.get('/contador/resumen_finanzas?mes=10&anio=2026')
    assert resp_res.status_code == 200
    html_res = resp_res.get_data(as_text=True)
    assert 'Resumen Financiero Automatizado' in html_res
    assert 'Facturación Neta Total' in html_res
    assert 'Punto de Equilibrio' in html_res
    assert 'Margen Bruto' in html_res
    assert 'Mano de Obra' in html_res or 'M. Obra' in html_res
    print("test_endpoints_unclosed_vs_simulacion: OK")

if __name__ == '__main__':
    test_verificar_cierre_estados()
    test_motor_razones_unclosed()
    test_motor_razones_closed()
    test_endpoints_unclosed_vs_simulacion()
    print("\n>>> TODOS LOS TESTS DE AUTOMATIZACIÓN Y CIERRE CONTABLE PASARON EXITOSAMENTE <<<")
