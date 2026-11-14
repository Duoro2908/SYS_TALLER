import pyodbc
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT RolID FROM Usuarios WHERE Email='fanny.atencion'")
row = cursor.fetchone()
print(f"Rol de Fanny es: {row[0] if row else 'No encontrada'}")
conn.close()
