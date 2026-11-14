import requests

s = requests.Session()
# Login as admin
r = s.post('http://127.0.0.1:5000/login', data={'username': 'admin', 'password': '123'}, allow_redirects=True)
print("Login status:", r.status_code)

urls = [
    'http://127.0.0.1:5000/',
    'http://127.0.0.1:5000/planilla/',
    'http://127.0.0.1:5000/planilla/contratos',
    'http://127.0.0.1:5000/bodega/inventario',
    'http://127.0.0.1:5000/bodega/compras',
    'http://127.0.0.1:5000/atencion/clientes',
    'http://127.0.0.1:5000/contador/balance',
]

for url in urls:
    res = s.get(url)
    has_toggle = 'id="theme-toggle"' in res.text
    print(f"URL: {url} -> Status: {res.status_code}, ThemeToggle: {has_toggle}")

