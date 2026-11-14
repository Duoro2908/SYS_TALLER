import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = app.test_client()
with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['username'] = 'elvin.admin'

resp = client.get('/admin/contratos')
html = resp.data.decode('utf-8')
for line in html.splitlines():
    if 'abrirModalEditarContrato' in line:
        print("LINE:", line[:150])
        break
