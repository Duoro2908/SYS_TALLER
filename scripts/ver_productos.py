import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT ProductoID, Codigo, Nombre, Stock, PrecioVenta, Costo FROM Productos")
for r in cursor.fetchall():
    print(r)
conn.close()

