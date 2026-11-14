import sys
sys.path.insert(0, '.')
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
for tbl in ['GastosOperativos', 'ReportesContables']:
    print(f"--- {tbl} ---")
    cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{tbl}'")
    for r in cursor.fetchall():
        print(f"  {r[0]}: {r[1]} ({r[2]})")
conn.close()

