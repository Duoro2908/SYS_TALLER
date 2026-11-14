import pyodbc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_db_connection

def alter_citas():
    conn = get_db_connection()
    if not conn:
        print("Error de conexión a la BD.")
        return
        
    cursor = conn.cursor()
    try:
        # Renombrar tabla si es posible, pero es más fácil sólo usar CitasWhatsApp como tabla principal y cambiarle el nombre interno luego si es necesario.
        # Por seguridad y compatibilidad con todo el sistema, añadiremos las columnas Origen y MecanicoAsignadoID
        
        # 1. Add Origen
        try:
            cursor.execute("ALTER TABLE CitasWhatsApp ADD Origen NVARCHAR(50) DEFAULT 'WhatsApp'")
            print("Columna Origen añadida.")
        except pyodbc.Error as e:
            if 'already exists' in str(e) or 'duplicate' in str(e) or 'already has' in str(e) or '42S21' in str(e):
                print("La columna Origen ya existe.")
            else:
                print(f"Error al añadir Origen: {e}")
                
        # 2. Add MecanicoAsignadoID
        try:
            cursor.execute("ALTER TABLE CitasWhatsApp ADD MecanicoAsignadoID INT NULL FOREIGN KEY REFERENCES Usuarios(UsuarioID)")
            print("Columna MecanicoAsignadoID añadida.")
        except pyodbc.Error as e:
            if 'already exists' in str(e) or 'duplicate' in str(e) or 'already has' in str(e) or '42S21' in str(e):
                print("La columna MecanicoAsignadoID ya existe.")
            else:
                print(f"Error al añadir MecanicoAsignadoID: {e}")

        conn.commit()
        print("Migración de CitasWhatsApp completada.")
        
    except Exception as ex:
        print(f"Error general: {ex}")
    finally:
        conn.close()

if __name__ == '__main__':
    alter_citas()
