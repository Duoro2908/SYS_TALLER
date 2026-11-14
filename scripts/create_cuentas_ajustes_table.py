import sys
sys.path.insert(0, '.')
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

sql = """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CuentasContablesAjustes')
BEGIN
    CREATE TABLE CuentasContablesAjustes (
        AjusteID INT IDENTITY(1,1) PRIMARY KEY,
        UsuarioID INT NULL,
        TipoReporte NVARCHAR(50) NOT NULL,
        Mes INT NOT NULL,
        Anio INT NOT NULL,
        Categoria NVARCHAR(100) NOT NULL,
        NombreCuenta NVARCHAR(200) NOT NULL,
        Monto DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
        FechaCreacion DATETIME DEFAULT GETDATE()
    );
    PRINT 'Tabla CuentasContablesAjustes creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La tabla CuentasContablesAjustes ya existe.';
END
"""

cursor.execute(sql)
conn.commit()
conn.close()
print("Ejecución finalizada con éxito.")

