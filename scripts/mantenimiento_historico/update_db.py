import shutil
import os
from database import get_db_connection

def update_db():
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return
        
    try:
        cursor = conn.cursor()
        
        # Corregir nombres
        cursor.execute("UPDATE Usuarios SET NombreCompleto = 'Elvin Mendez' WHERE Email = 'gerente'")
        cursor.execute("UPDATE Usuarios SET NombreCompleto = 'Cley Mendez' WHERE Email = 'mecanico'")
        
        # Actualizar ImagenUrl basado en el Nombre o Categoria
        # Llantas
        cursor.execute("UPDATE Productos SET ImagenUrl = 'llanta.png' WHERE Nombre LIKE '%Llanta%'")
        # Motor
        cursor.execute("UPDATE Productos SET ImagenUrl = 'motor.png' WHERE Categoria = 'Motor'")
        # Frenos
        cursor.execute("UPDATE Productos SET ImagenUrl = 'frenos.png' WHERE Categoria = 'Frenos'")
        # Electrico
        cursor.execute("UPDATE Productos SET ImagenUrl = 'electrico.png' WHERE Categoria = 'Sistema Eléctrico'")
        
        conn.commit()
        print("Base de datos actualizada correctamente.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_db()
