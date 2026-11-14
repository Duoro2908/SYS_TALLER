from database import get_db_connection

def test_add_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Check if table exists to avoid errors on rerun
        cursor.execute("SELECT count(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TablaDePrueba_Conexion'")
        exists = cursor.fetchone()[0]
        
        if exists == 0:
            cursor.execute("CREATE TABLE TablaDePrueba_Conexion (ID int IDENTITY(1,1) PRIMARY KEY, Mensaje VARCHAR(100))")
            conn.commit()
            print("¡Tabla creada con éxito!")
        else:
            print("La tabla ya existía.")
            
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        print("Tablas encontradas en la BD:")
        for t in tables:
            print(f"- {t[0]}")
        conn.close()
    else:
        print("Error de conexión a la base de datos.")

if __name__ == '__main__':
    test_add_table()
