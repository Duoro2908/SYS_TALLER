import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def reset_whatsapp_data():
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos.")
        return
        
    cursor = conn.cursor()
    try:
        # Desvincular CitaID de OrdenesTrabajo si existen
        cursor.execute("UPDATE OrdenesTrabajo SET CitaID = NULL WHERE CitaID IS NOT NULL")
        
        # Eliminar mensajes
        cursor.execute("DELETE FROM MensajesWhatsApp")
        
        # Eliminar citas
        cursor.execute("DELETE FROM CitasWhatsApp")
        
        # Reiniciar IDENTITIES
        try:
            cursor.execute("DBCC CHECKIDENT ('MensajesWhatsApp', RESEED, 0)")
        except Exception:
            pass
            
        try:
            cursor.execute("DBCC CHECKIDENT ('CitasWhatsApp', RESEED, 0)")
        except Exception:
            pass
            
        conn.commit()
        
        # Verificar conteos
        cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp")
        citas_cnt = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MensajesWhatsApp")
        msgs_cnt = cursor.fetchone()[0]
        
        print(f"[EXITO] Tablas de WhatsApp reiniciadas a 0. Citas: {citas_cnt}, Mensajes: {msgs_cnt}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al reiniciar tablas: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    reset_whatsapp_data()
