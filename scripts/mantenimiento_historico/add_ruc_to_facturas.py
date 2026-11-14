import sys
sys.path.append(r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR")
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

try:
    cursor.execute("""
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Facturas' AND COLUMN_NAME = 'RUC_Emisor'
    )
    BEGIN
        ALTER TABLE Facturas ADD RUC_Emisor NVARCHAR(50) DEFAULT 'J0310000123456' WITH VALUES;
    END
    """)
    conn.commit()
    print("Column RUC_Emisor checked/added.")

    cursor.execute("""
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Facturas' AND COLUMN_NAME = 'RUCCliente'
    )
    BEGIN
        ALTER TABLE Facturas ADD RUCCliente NVARCHAR(50) NULL;
    END
    """)
    conn.commit()
    print("Column RUCCliente checked/added.")

    cursor.execute("UPDATE Facturas SET RUC_Emisor = 'J0310000123456' WHERE RUC_Emisor IS NULL OR RUC_Emisor = ''")
    conn.commit()
    print(f"Updated existing invoices with default RUC. Rows affected: {cursor.rowcount}")

    cursor.execute("SELECT FacturaID, NumeroFactura, RUC_Emisor, RUCCliente FROM Facturas")
    rows = cursor.fetchall()
    print(f"Total Facturas: {len(rows)}")
    for r in rows[:3]:
        print("Sample:", r)

except Exception as e:
    conn.rollback()
    print("Error:", e)
finally:
    conn.close()
