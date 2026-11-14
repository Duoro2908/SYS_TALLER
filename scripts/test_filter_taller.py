import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_bot import process_incoming_whatsapp_message, es_mensaje_de_taller
from database import get_db_connection

def test_workshop_filter():
    print("--- TEST 1: Filtro de Temática de Taller ---")
    m1 = "Hola profesor buenas tardes"
    m2 = "Que onda bro ya hiciste la tarea?"
    m3 = "Quiero una cita de mantenimiento preventivo para mi moto mañana a las 10 am"
    m4 = "Mi moto tiene un ruido en los frenos"
    
    print(f"'{m1}' -> Es taller? {es_mensaje_de_taller(m1)}")
    print(f"'{m2}' -> Es taller? {es_mensaje_de_taller(m2)}")
    print(f"'{m3}' -> Es taller? {es_mensaje_de_taller(m3)}")
    print(f"'{m4}' -> Es taller? {es_mensaje_de_taller(m4)}")
    
    assert es_mensaje_de_taller(m1) is False
    assert es_mensaje_de_taller(m2) is False
    assert es_mensaje_de_taller(m3) is True
    assert es_mensaje_de_taller(m4) is True
    
    print("\n--- TEST 2: Procesar mensaje no relacionado al taller ('no le pone mente') ---")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM MensajesWhatsApp; DELETE FROM CitasWhatsApp;")
    conn.commit()
    
    res_no_taller = process_incoming_whatsapp_message("+505 8899 0011", m1)
    print("Resultado no taller:", res_no_taller)
    assert res_no_taller['es_taller'] is False
    
    cur.execute("SELECT COUNT(*) FROM CitasWhatsApp")
    count_citas = cur.fetchone()[0]
    print("Citas en BD tras mensaje no taller (debe ser 0):", count_citas)
    assert count_citas == 0
    
    print("\n--- TEST 3: Procesar mensaje que SI es de taller (agenda cita al instante) ---")
    from whatsapp_bot import set_bot_status
    set_bot_status(True)
    res_taller = process_incoming_whatsapp_message("+505 8899 0022", m3)
    print("Resultado taller:", res_taller['success'])
    assert res_taller['es_taller'] is True
    assert 'cita_id' in res_taller
    
    cur.execute("SELECT COUNT(*) FROM CitasWhatsApp")
    count_citas_taller = cur.fetchone()[0]
    print("Citas en BD tras mensaje de taller (debe ser 1):", count_citas_taller)
    assert count_citas_taller == 1
    
    # Limpiar nuevamente a 0 para que el usuario empiece limpio
    cur.execute("DELETE FROM MensajesWhatsApp; DELETE FROM CitasWhatsApp;")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM CitasWhatsApp")
    citas_final = cur.fetchone()[0]
    print(f"\n[LIMPIO] Citas finales en BD (debe ser 0): {citas_final}")
    assert citas_final == 0
    conn.close()
    
    print("\n[OK] Todas las pruebas del filtro inteligente de taller pasaron exitosamente!")

if __name__ == '__main__':
    test_workshop_filter()
