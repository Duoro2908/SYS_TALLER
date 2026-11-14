import pyodbc
from database import get_db_connection

def update_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE ControlCaja ADD MontoFinal DECIMAL(10,2) NULL")
        print("Añadido MontoFinal")
    except Exception as e:
        print("MontoFinal ya existe o error:", e)
        
    try:
        cursor.execute("ALTER TABLE ControlCaja ADD Diferencia DECIMAL(10,2) NULL")
        print("Añadido Diferencia")
    except Exception as e:
        print("Diferencia ya existe o error:", e)
        
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    update_schema()
