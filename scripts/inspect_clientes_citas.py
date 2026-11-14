import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cur = conn.cursor()

print("--- 1. Clientes Table Schema ---")
cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Clientes'")
print(cur.fetchall())

print("\n--- 2. Motocicletas Table Schema ---")
cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Motocicletas'")
print(cur.fetchall())

print("\n--- 3. Clientes Actuales ---")
cur.execute("SELECT TOP 10 * FROM Clientes")
for r in cur.fetchall():
    print(r)

print("\n--- 4. CitasWhatsApp Table Schema ---")
cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CitasWhatsApp'")
print(cur.fetchall())

print("\n--- 5. CitasWhatsApp Actuales ---")
cur.execute("SELECT TOP 10 * FROM CitasWhatsApp")
for r in cur.fetchall():
    print(r)

conn.close()
