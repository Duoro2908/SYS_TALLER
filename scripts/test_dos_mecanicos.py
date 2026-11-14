import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json
sys.path.insert(0, os.path.abspath('.'))
from database import get_db_connection

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Use a test date in the future (a Wednesday)
test_date = '2026-11-04'
test_time = '10:00'

def cleanup_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CitasWhatsApp WHERE MotoID IN (SELECT MotoID FROM Motocicletas WHERE Placa IN ('M999001', 'M999002', 'M999003')) OR ClienteID IN (SELECT ClienteID FROM Clientes WHERE Telefono IN ('88880001', '88880002', '88880003'))")
        cursor.execute("DELETE FROM Motocicletas WHERE Placa IN ('M999001', 'M999002', 'M999003')")
        cursor.execute("DELETE FROM Clientes WHERE Telefono IN ('88880001', '88880002', '88880003')")
        conn.commit()
        conn.close()

cleanup_db()

def book_cita(name, tel, plate):
    data = urllib.parse.urlencode({
        'nombre': name,
        'telefono': tel,
        'marca': 'Genesis',
        'modelo': 'CR',
        'anio': '2024',
        'placa': plate,
        'cilindraje': '250',
        'tipo_servicio': 'Preventivo',
        'fecha': test_date,
        'hora': test_time
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/agendar_cita', data=data)
    with opener.open(req) as resp:
        return resp.read().decode('utf-8')

print("1. Agendando cita 1 (Mecánico 1)...")
resp1 = book_cita('Mecanico 1 Cliente', '88880001', 'M999001')
import re
flashes = re.findall(r'<div class="flash-msg [^"]*">.*?<span>(.*?)</span>', resp1, re.DOTALL)
print("Flashes 1:", [f.strip() for f in flashes])
assert any('agendada con' in f for f in flashes), f'Cita 1 fallo: {flashes}'
print("-> Cita 1 agendada con éxito!")

print("2. Agendando cita 2 (Mecánico 2, misma hora)...")
resp2 = book_cita('Mecanico 2 Cliente', '88880002', 'M999002')
flashes2 = re.findall(r'<div class="flash-msg [^"]*">.*?<span>(.*?)</span>', resp2, re.DOTALL)
print("Flashes 2:", [f.strip() for f in flashes2])
assert any('agendada con' in f for f in flashes2), f'Cita 2 fallo (debería permitir 2): {flashes2}'
print("-> Cita 2 agendada con éxito a la misma hora!")

print("3. Intentando agendar cita 3 (Misma hora, ambos mecánicos ocupados)...")
resp3 = book_cita('Mecanico 3 Cliente', '88880003', 'M999003')
flashes3 = re.findall(r'<div class="flash-msg [^"]*">.*?<span>(.*?)</span>', resp3, re.DOTALL)
print("Flashes 3:", [f.strip() for f in flashes3])
assert any('Capacidad completa' in f for f in flashes3), f'Cita 3 no fue bloqueada: {flashes3}'
print("-> Cita 3 bloqueada exitosamente con mensaje de 2 mecánicos ocupados!")

print("4. Verificando API de horarios disponibles...")
api_req = urllib.request.Request(f'http://127.0.0.1:5000/api/horarios_disponibles?fecha={test_date}')
with urllib.request.urlopen(api_req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Ocupación detectada por API:", data)
    assert data.get(test_time) == 2, f"Expected 2 citas, got {data.get(test_time)}"
print("\n>>> TEST DE CAPACIDAD DE 2 MECÁNICOS SUPERADO AL 100% <<<")

# Clean up test entries
cleanup_db()
print("Registros de prueba eliminados correctamente.")
