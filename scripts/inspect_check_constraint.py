import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT definition FROM sys.check_constraints WHERE name = 'CHK_Moto_Marca'")
row = cursor.fetchone()
if row:
    print("CHK_Moto_Marca definition:", row[0])
else:
    print("Constraint not found")

conn.close()
