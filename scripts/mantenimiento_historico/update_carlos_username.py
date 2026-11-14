import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def run():
    conn = get_db_connection()
    if not conn:
        print("Error de conexión")
        return
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Usuarios 
        SET Email = 'carlos.finanzas' 
        WHERE Email = 'carlos.contador' OR NombreCompleto LIKE 'Carlos Rene Gavarrete%'
    """)
    conn.commit()
    print("Filas actualizadas:", cursor.rowcount)
    
    cursor.execute("SELECT UsuarioID, NombreCompleto, Email, RolID, Activo FROM Usuarios WHERE Email = 'carlos.finanzas'")
    user = cursor.fetchone()
    print("Usuario verificado:", user)
    conn.close()

if __name__ == '__main__':
    run()
