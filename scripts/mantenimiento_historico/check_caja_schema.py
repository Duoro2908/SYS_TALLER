import pyodbc
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ControlCaja'")
columns = cursor.fetchall()
print("ControlCaja columns:", [c[0] for c in columns])
conn.close()
