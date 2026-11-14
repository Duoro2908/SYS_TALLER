import pyodbc
from config import Config

def fix_role_name():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Actualizar Rol 3 a "Mecanico" limpio sin tildes ni caracteres extraños
        cursor.execute("UPDATE Roles SET NombreRol = 'Mecanico' WHERE RolID = 3")
        conn.commit()
        
        print("Nombre del rol actualizado correctamente a 'Mecanico'.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_role_name()
