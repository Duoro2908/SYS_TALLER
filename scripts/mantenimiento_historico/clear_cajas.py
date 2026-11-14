import pyodbc
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

try:
    cursor.execute("UPDATE Facturas SET CajaID = NULL")
    cursor.execute("DELETE FROM ControlCaja")
    conn.commit()
    print("ControlCaja limpiado con éxito.")
except Exception as e:
    conn.rollback()
    print("Error:", e)
finally:
    conn.close()
