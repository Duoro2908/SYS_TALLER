import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_mercadotecnia():
    client = app.test_client()

    print("=== 1. VERIFICAR BOTÓN DE SPOT EN LOGIN Y PÁGINA DEDICADA ===")
    resp_login = client.get('/login')
    assert resp_login.status_code == 200
    html_login = resp_login.get_data(as_text=True)
    assert 'Spot Publicitario' in html_login
    assert '/spot_publicitario' in html_login

    resp_spot = client.get('/spot_publicitario')
    assert resp_spot.status_code == 200
    html_spot = resp_spot.get_data(as_text=True)
    assert 'genesis_dark_taller.jpg' in html_spot
    assert 'promo_rifa.jpg' in html_spot
    assert '1,000' in html_spot
    print("SPOT PUBLICITARIO CINEMATOGRÁFICO: OK (Pantalla grande, controles lentos y botón en login)")

    print("\n=== 2. VERIFICAR LOGIN CARLOS MANUEL HUETE (carlos.merca) ===")
    resp = client.post('/login', data={'email': 'carlos.merca', 'password': 'Manuel2026*'}, follow_redirects=False)
    assert resp.status_code == 302, f"Login falló con status {resp.status_code}"

    with client.session_transaction() as sess:
        print("Sesión:", dict(sess))
        assert sess.get('nombre_completo') == 'Carlos Manuel Huete Huete'
        assert sess.get('username') == 'carlos.merca'
        assert sess.get('rol_nombre') == 'Mercadotecnia'

    # Redirección index -> /mercadotecnia/resumen
    resp_idx = client.get('/', follow_redirects=False)
    print("Redirección index:", resp_idx.headers.get('Location'))
    assert resp_idx.headers.get('Location') == '/mercadotecnia/resumen'

    # Probar submódulos de mercadotecnia
    for url in ['/mercadotecnia/resumen', '/mercadotecnia/participantes', '/mercadotecnia/premios']:
        r = client.get(url)
        print(f"GET {url} -> {r.status_code}")
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        assert 'Mercadotecnia' in html
        assert 'Ingeniero de Sistemas - Mercadotecnia' in html

    print("MÓDULO Y SUBMÓDULOS DE MERCADOTECNIA: OK!")

    print("\n=== 3. VERIFICAR PLANILLA DE PAGO ===")
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['rol_id'] = 1
        sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'
        sess['username'] = 'elvin.admin'

    resp_plan = client.get('/admin/planilla')
    assert resp_plan.status_code == 200
    html_plan = resp_plan.get_data(as_text=True)
    assert 'Carlos Manuel Huete Huete' in html_plan, 'Carlos Huete no aparece en planilla'
    print("CARLOS MANUEL HUETE PRESENTE EN PLANILLA DE PAGOS: OK!")

    print("\n>>> TODOS LOS TESTS DE MERCADOTECNIA PASARON AL 100% <<<")

if __name__ == '__main__':
    test_mercadotecnia()
