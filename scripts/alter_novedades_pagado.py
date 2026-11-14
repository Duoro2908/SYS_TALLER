import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cursor = conn.cursor()
try:
    cursor.execute("""
        IF NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'NovedadesNomina' AND COLUMN_NAME = 'Pagado'
        )
        BEGIN
            ALTER TABLE NovedadesNomina ADD Pagado BIT DEFAULT 0;
            PRINT 'Columna Pagado anadida a NovedadesNomina';
        END
        ELSE
        BEGIN
            PRINT 'Columna Pagado ya existe';
        END
    """)
    conn.commit()
    print("Migracion NovedadesNomina exitosa!")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
