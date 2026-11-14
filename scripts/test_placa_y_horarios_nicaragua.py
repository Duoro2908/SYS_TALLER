import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json
import re
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath('.'))
from database import get_db_connection

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

NICARAGUA_TZ = timezone(timedelta(hours=-6))
now_nicaragua = datetime.now(NICARAGUA_TZ)
today_nicaragua_str = now_nicaragua.strftime('%Y-%m-%d')
future_date = '2026-11-04' # Wednesday

def cleanup_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM CitasWhatsApp 
            WHERE MotoID IN (SELECT MotoID FROM Motocicletas WHERE Placa IN ('M999001', 'M999002', 'M999003', 'M1043', 'M123456'))
               OR ClienteID IN (SELECT ClienteID FROM Clientes WHERE Telefono IN ('88880001', '88880002', '88880003', '88889999'))
        """)
        cursor.execute("DELETE FROM Motocicletas WHERE Placa IN ('M999001', 'M999002', 'M999003', 'M1043', 'M123456')")
        cursor.execute("DELETE FROM Clientes WHERE Telefono IN ('88880001', '88880002', '88880003', '88889999')")
        conn.commit()
        conn.close()

cleanup_db()

def book_cita(name, tel, plate, fecha, hora):
    data = urllib.parse.urlencode({
        'nombre': name,
        'telefono': tel,
        'marca': 'Genesis',
        'modelo': 'CR',
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

print("=== 1. TEST DE RECHAZO DE SÍMBOLOS EN PLACA ===")
# Probar con símbolos: asterisco (como en la foto M*1043), guion (M-123456), arroba (M@123)
for bad_plate in ['M*1043', 'M-123456', 'M@999', 'M 999']:
    flashes, _ = book_cita('Cliente Simbolo', '88889999', bad_plate, future_date, '10:00')
    print(f"Placa inválida '{bad_plate}' -> Flashes:", flashes)
    assert any('solo puede contener letras y números' in f for f in flashes), f"Fallo al bloquear placa con símbolo '{bad_plate}'"
print("-> Bloqueo de símbolos en placa: OK (100% verificado)")

print("\n=== 2. TEST DE ACEPTACIÓN DE PLACA ALFANUMÉRICA PURA ===")
flashes_ok, _ = book_cita('Cliente Valido', '88880001', 'M1043', future_date, '10:00')
print("Placa alfanumérica 'M1043' -> Flashes:", flashes_ok)
assert any('agendada con éxito' in f for f in flashes_ok), "Fallo al agendar con placa alfanumérica válida"
print("-> Aceptación de placa alfanumérica: OK (100% verificado)")

print("\n=== 3. TEST DE ZONA HORARIA DE MANAGUA (RECHAZO DE HORAS PASADAS DE HOY) ===")
# Si hoy es 27 de octubre y la hora actual en Managua es > 08:00 AM, probar agendar a las 08:00 AM de hoy
current_hour = now_nicaragua.hour
if current_hour >= 9:
    flashes_past, _ = book_cita('Cliente Pasado', '88880002', 'M999002', today_nicaragua_str, '08:00')
    print(f"Intento de agendar hoy a las 08:00 AM (Hora Managua actual: {now_nicaragua.strftime('%H:%M')}) -> Flashes:", flashes_past)
    assert any('respecto a la hora actual de Managua' in f for f in flashes_past), "Fallo al bloquear hora pasada"
    print("-> Bloqueo de horas pasadas para hoy en Managua: OK (100% verificado)")
else:
    print("-> La hora actual de Managua es antes de las 09:00 AM, saltando verificación de 08:00 AM.")

print("\n=== 4. TEST DE CAPACIDAD DE 2 MECÁNICOS A LA MISMA HORA ===")
# Ya agendamos cita 1 en future_date a las 10:00 (M1043)
# Agendamos cita 2 en future_date a las 10:00 (M999002)
flashes_c2, _ = book_cita('Mecanico 2 Cliente', '88880002', 'M999002', future_date, '10:00')
print("Cita 2 a las 10:00 (Mecánico 2) -> Flashes:", flashes_c2)
assert any('agendada con éxito' in f for f in flashes_c2), "Cita 2 debería ser permitida para el segundo mecánico"
print("-> Cita 2 permitida a la misma hora: OK!")

# Intentar cita 3 en future_date a las 10:00 (M999003) -> DEBE BLOQUEARSE
flashes_c3, _ = book_cita('Mecanico 3 Cliente', '88880003', 'M999003', future_date, '10:00')
print("Cita 3 a las 10:00 (Intento de sobrecapacidad) -> Flashes:", flashes_c3)
assert any('Capacidad completa' in f for f in flashes_c3), "Cita 3 no fue bloqueada!"
print("-> Cita 3 bloqueada con aviso de 2 mecánicos ocupados: OK!")

print("\n=== 5. TEST DE API /api/horarios_disponibles CON ZONA HORARIA ===")
api_req = urllib.request.Request(f'http://127.0.0.1:5000/api/horarios_disponibles?fecha={today_nicaragua_str}')
with urllib.request.urlopen(api_req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Respuesta API para hoy:", {k: v for k, v in data.items() if k in ['fecha_hoy', 'hora_actual', 'es_hoy']})
    assert data.get('es_hoy') is True, "API no detectó que la fecha es hoy"
    assert data.get('fecha_hoy') == today_nicaragua_str, "Fecha de hoy incorrecta en API"
    assert 'hora_actual' in data, "hora_actual no presente en API"
    print("-> API con datos de zona horaria de Managua: OK!")

# Cleanup
cleanup_db()
print("\n>>> TODOS LOS TESTS DE PLACA, ZONA HORARIA MANAGUA Y 2 MECÁNICOS PASARON CON 100% DE ÉXITO <<<")
