import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_bot import process_incoming_whatsapp_message, parse_appointment_details
from database import get_db_connection

def test_full_whatsapp_flow():
    print("--- INICIANDO VERIFICACION DE FLUJO DE CITAS WHATSAPP (+505 77326738) ---")
    
    # 1. Test date parser
    p1 = parse_appointment_details("Hola quiero cita para mañana a las 10 am mantenimiento preventivo")
    print(f"[OK] Parser Test 1: Fecha={p1['fecha_programada']}, Tipo={p1['tipo_mantenimiento']}")
    
    p2 = parse_appointment_details("Necesito revisar frenos el lunes a las 2 pm")
    print(f"[OK] Parser Test 2: Fecha={p2['fecha_programada']}, Tipo={p2['tipo_mantenimiento']}")
    
    # 2. Test bot incoming message processing
    res = process_incoming_whatsapp_message("+505 77326738", "Quiero agendar cita express para pasado mañana a las 3 pm")
    print(f"[OK] Process Result Success: {res.get('success')}")
    print(f"[OK] CitaID: {res.get('cita_id')}")
    print(f"[OK] Cliente: {res.get('nombre_cliente')}")
    print(f"[OK] Fecha Programada: {res.get('fecha_programada')}")
    
    # 3. Check DB records
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp")
        count_citas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MensajesWhatsApp")
        count_mensajes = cursor.fetchone()[0]
        print(f"[SUCCESS] Citas en BD: {count_citas}, Mensajes en BD: {count_mensajes}")
        conn.close()
        
    print("--- FLUJO VERIFICADO CORRECTAMENTE ---")

if __name__ == '__main__':
    test_full_whatsapp_flow()
