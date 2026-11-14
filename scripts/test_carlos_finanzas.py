import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_carlos_finanzas_y_contabilidad():
    client = app.test_client()

    print("=== TEST 1: LOGIN CARLOS.FINANZAS (MODO FINANZAS) ===")
    resp = client.post('/login', data={'email': 'carlos.finanzas', 'password': 'Carlos2026*'}, follow_redirects=False)
    print("Status:", resp.status_code, "Redirect to:", resp.headers.get('Location'))
    assert resp.status_code == 302, "Error al iniciar sesión con carlos.finanzas"

    with client.session_transaction() as sess:
        assert sess.get('username') == 'carlos.finanzas'
        assert sess.get('nombre_completo') == 'Carlos Rene Gavarrete Calero'

    # Verificar redirección de '/' -> '/contador/resumen_finanzas'
    resp_idx = client.get('/', follow_redirects=False)
    assert resp_idx.headers.get('Location') == '/contador/resumen_finanzas'

    # Verificar contenido de la página y separación de menú lateral
    resp_page = client.get('/contador/resumen_finanzas')
    assert resp_page.status_code == 200
    html_fin = resp_page.get_data(as_text=True)
    assert '<span>Finanzas</span>' in html_fin
    assert 'Razones Financieras' in html_fin
    assert 'Contador - Finanzas' in html_fin
    # Recursos Humanos NO debe aparecer en el menú lateral ni tener acceso
    assert '<span>Contabilidad</span>' not in html_fin
    assert '<span>Recursos Humanos</span>' not in html_fin
    resp_rrhh_blocked = client.get('/admin/planilla', follow_redirects=False)
    assert resp_rrhh_blocked.status_code == 302, "carlos.finanzas no debe tener acceso a /admin/planilla"
    print("[OK] carlos.finanzas ve ÚNICAMENTE Finanzas y tiene Recursos Humanos 100% bloqueado y oculto!")

    # Logout
    client.get('/logout')

    print("\n=== TEST 2: LOGIN CARLOS.CONTABILIDAD (MODO CONTABILIDAD) ===")
    resp2 = client.post('/login', data={'email': 'carlos.contabilidad', 'password': 'Carlos2026**'}, follow_redirects=False)
    print("Status:", resp2.status_code, "Redirect to:", resp2.headers.get('Location'))
    assert resp2.status_code == 302, "Error al iniciar sesión con carlos.contabilidad"

    with client.session_transaction() as sess:
        assert sess.get('username') == 'carlos.contabilidad'
        assert sess.get('nombre_completo') == 'Carlos Rene Gavarrete Calero'

    # Verificar redirección de '/' -> '/contador/resumen_contable'
    resp2_idx = client.get('/', follow_redirects=False)
    assert resp2_idx.headers.get('Location') == '/contador/resumen_contable'

    # Verificar contenido de la página y separación de menú lateral
    resp_cont_page = client.get('/contador/balance')
    assert resp_cont_page.status_code == 200
    html_cont = resp_cont_page.get_data(as_text=True)
    assert '<span>Contabilidad</span>' in html_cont
    assert 'Balance General' in html_cont
    assert 'Estado de Resultados' in html_cont
    assert 'Contador - Contabilidad' in html_cont
    # Finanzas y Recursos Humanos NO deben aparecer en el menú lateral de carlos.contabilidad
    assert '<span>Finanzas</span>' not in html_cont
    assert '<span>Recursos Humanos</span>' not in html_cont
    resp_rrhh_blocked2 = client.get('/admin/planilla', follow_redirects=False)
    assert resp_rrhh_blocked2.status_code == 302, "carlos.contabilidad no debe tener acceso a /admin/planilla"
    print("[OK] carlos.contabilidad ve ÚNICAMENTE Contabilidad y tiene Recursos Humanos 100% bloqueado y oculto!")

    # Logout
    client.get('/logout')

    # Verificar Planilla
    print("\n=== TEST 3: VERIFICAR PLANILLA (CARLOS INCLUIDO EXACTAMENTE UNA VEZ) ===")
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['rol_id'] = 1
        sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'
        sess['username'] = 'elvin.admin'

    resp_plan = client.get('/admin/planilla')
    assert resp_plan.status_code == 200
    html_plan = resp_plan.get_data(as_text=True)
    assert 'Carlos Rene Gavarrete Calero' in html_plan, "Carlos debe figurar en la planilla"
    assert html_plan.count('Carlos Rene Gavarrete Calero') == html_plan.count('Martha Jovana Lopez Chavarria'), "Carlos debe figurar como un único empleado en la planilla"
    assert 'carlos.finanzas' in html_plan
    assert 'carlos.contabilidad' not in html_plan, "carlos.contabilidad no debe duplicar la fila de Carlos"
    assert 'Erwind Bismark Cruz Ruiz' not in html_plan, "Erwind no debe figurar en planilla"
    assert 'Martha Jovana Lopez Chavarria' in html_plan
    assert 'C$ 16,500.00' in html_plan or '16,500' in html_plan, "Salario de Carlos debe ser C$ 16,500.00"
    assert 'C$ 180,000.00' in html_plan or '180,000' in html_plan, "Total bruto de planilla debe ser C$ 180,000.00"
    print("PLANILLA OK: Carlos incluido exactamente 1 vez (C$ 16,500.00), planilla total C$ 180,000.00!")

    print("\n>>> TODOS LOS TESTS DE SEPARACIÓN Y CUADRE PASARON CON ÉXITO <<<")

if __name__ == '__main__':
    test_carlos_finanzas_y_contabilidad()
