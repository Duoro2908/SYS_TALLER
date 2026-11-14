import sys
sys.path.insert(0, '.')
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
for row in cursor.fetchall():
    print(row[0])
conn.close()

