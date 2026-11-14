import sys
sys.path.append('.')
from database import get_db_connection

conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT Email, RolID FROM Usuarios")
    for row in cursor.fetchall():
        print(row)
    conn.close()
