import requests

try:
    r = requests.get('http://127.0.0.1:5000/auth/login', timeout=3)
    print("Servidor Flask respondiendo status:", r.status_code)
except Exception as e:
    print("Error conectando a Flask local:", e)
