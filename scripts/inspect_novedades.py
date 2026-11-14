import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='NovedadesNomina'")
cols = cursor.fetchall()
print("Columns in NovedadesNomina:", cols)
conn.close()
