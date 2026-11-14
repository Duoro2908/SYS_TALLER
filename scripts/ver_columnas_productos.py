import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Productos'")
for r in cursor.fetchall():
    print(r)
cursor.execute("SELECT TOP 5 * FROM Productos")
for r in cursor.fetchall():
    print(r)
conn.close()

