import sys
sys.path.insert(0, '.')
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'RifaPremios'")
for r in cursor.fetchall():
    print(r[0], r[1])
conn.close()

