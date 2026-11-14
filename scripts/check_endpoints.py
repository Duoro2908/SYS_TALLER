import sys
sys.path.insert(0, '.')
from app import app

with app.test_request_context():
    from flask import url_for
    for endpoint in ['planilla.empleados', 'planilla.index', 'planilla.contratos', 'planilla.registro_mensual']:
        print(endpoint, '->', url_for(endpoint))

