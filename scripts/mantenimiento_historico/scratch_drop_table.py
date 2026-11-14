import pyodbc
from config import Config

def drop_test_table():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS [dbo].[TablaDePrueba_Conexion]")
        conn.commit()
        print("Tabla [dbo].[TablaDePrueba_Conexion] eliminada exitosamente.")
        conn.close()
    except pyodbc.Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    drop_test_table()
