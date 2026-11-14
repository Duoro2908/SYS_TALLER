import os
import sys

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def inspect():
    conn = get_db_connection()
    if not conn:
        print("Error al conectar a la BD.")
        return
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Total tablas encontradas: {len(tables)}\n")
    
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cursor.fetchone()[0]
            print(f"{t}: {cnt} registros")
        except Exception as e:
            print(f"{t}: Error ({e})")
            
    conn.close()

if __name__ == '__main__':
    inspect()
