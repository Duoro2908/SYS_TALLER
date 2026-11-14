import pyodbc
from database import get_db_connection

def update_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE ControlCaja ADD EfectivoFisico DECIMAL(10,2) NULL")
        print("Añadido EfectivoFisico")
    except Exception as e:
        print("EfectivoFisico ya existe o error:", e)
        
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    update_schema()
