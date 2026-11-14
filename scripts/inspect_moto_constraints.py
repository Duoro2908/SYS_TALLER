import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT name, definition FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('Motocicletas')")
for r in cursor.fetchall():
    print(r)

conn.close()
