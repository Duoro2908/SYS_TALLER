import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json
import re

sys.path.insert(0, os.path.abspath('.'))
from database import get_db_connection

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

future_date = '2026-11-04'

def cleanup_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM CitasWhatsApp 
            WHERE MotoID IN (SELECT MotoID FROM Motocicletas WHERE Placa IN ('M777001', 'M777002'))
               OR ClienteID IN (SELECT ClienteID FROM Clientes WHERE Telefono IN ('87770001', '87770002'))
        """)
        cursor.execute("DELETE FROM Motocicletas WHERE Placa IN ('M777001', 'M777002')")
        cursor.execute("DELETE FROM Clientes WHERE Telefono IN ('87770001', '87770002')")
        conn.commit()
        conn.close()

cleanup_db()

def book_cita(name, tel, marca, modelo, plate, fecha, hora):
    data = urllib.parse.urlencode({
        'nombre': name,
        'telefono': tel,
        'marca': marca,
        'modelo': modelo,
        'anio': '2024',
        'placa': plate,
        'cilindraje': '250',
        'tipo_servicio': 'Preventivo',
        'fecha': fecha,
        'hora': hora
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/agendar_cita', data=data)
    with opener.open(req) as resp:
        html = resp.read().decode('utf-8')
        flashes = re.findall(r'<div class="flash-msg [^"]*">.*?<span>(.*?)</span>', html, re.DOTALL)
        return [f.strip() for f in flashes], html

print("=== 1. VERIFICAR QUE NO EXISTAN 'CLIENTE WA' EN /api/search_client ===")
api_req = urllib.request.Request('http://127.0.0.1:5000/api/search_client')
with urllib.request.urlopen(api_req) as resp:
    clients = json.loads(resp.read().decode('utf-8'))
    print(f"Total clientes retornados por el directorio: {len(clients)}")
    wa_clients = [c for c in clients if 'cliente wa' in c['nombre'].lower()]
    print(f"Clientes WA encontrados: {len(wa_clients)}")
    assert len(wa_clients) == 0, f"Error: Aún se encontraron clientes WA: {wa_clients}"
print("-> Directorio libre de 'Cliente WA': OK (100% verificado)")

print("\n=== 2. VERIFICAR QUE SE RECHACEN OTRAS MARCAS (Yamaha, Honda, etc.) ===")
for bad_brand in ['Yamaha', 'Honda', 'Bajaj', 'Suzuki']:
    flashes, _ = book_cita('Cliente Marca Falsa', '87770001', bad_brand, 'CR4V 250', 'M777001', future_date, '10:00')
    print(f"Intento con marca '{bad_brand}' -> Flashes:", flashes)
    assert any('exclusiva en motocicletas de la marca Genesis' in f for f in flashes), f"Fallo al bloquear marca '{bad_brand}'"
print("-> Bloqueo estricto de otras marcas: OK (100% verificado)")

print("\n=== 3. VERIFICAR QUE SE RECHACEN MODELOS DE OTRAS MARCAS (FZ, Pulsar, etc.) ===")
for bad_model in ['FZ 2.0', 'Pulsar NS 200', 'Boxer 150', 'YBR 125']:
    flashes, _ = book_cita('Cliente Modelo Falso', '87770001', 'Genesis', bad_model, 'M777001', future_date, '10:00')
    print(f"Intento con modelo no Genesis '{bad_model}' -> Flashes:", flashes)
    assert any('Solo se permiten modelos Genesis' in f for f in flashes), f"Fallo al bloquear modelo '{bad_model}'"
print("-> Bloqueo estricto de modelos de otras marcas: OK (100% verificado)")

print("\n=== 4. VERIFICAR AGENDAMIENTO EXITOSO CON MARCA GENESIS Y MODELO GENESIS ===")
flashes_ok, _ = book_cita('Carlos Rodriguez', '87770001', 'Genesis', 'CR4V 250', 'M777001', future_date, '10:00')
print("Cita con Genesis CR4V 250 -> Flashes:", flashes_ok)
assert any('agendada con éxito' in f for f in flashes_ok), "Fallo al agendar cita con Genesis legítima"
print("-> Agendamiento Genesis oficial: OK (100% verificado)")

print("\n=== 5. VERIFICAR QUE NO HAYA PLACEHOLDERS 'Ej.' EN LA PÁGINA ===")
with urllib.request.urlopen('http://127.0.0.1:5000/agendar_cita') as resp:
    page_html = resp.read().decode('utf-8')
    assert 'Ej.' not in page_html, "Error: Todavía existe algún placeholder con 'Ej.' en la página"
    print("-> Eliminación de 'Ej.' y placeholders vacíos: OK (100% verificado)")

cleanup_db()
print("\n>>> TODOS LOS TESTS DE GENESIS EXCLUSIVO Y LIMPIEZA DE CLIENTES WA PASARON AL 100% <<<")
