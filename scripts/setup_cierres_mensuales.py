import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_db_connection

def setup_cierres_mensuales():
    conn = get_db_connection()
    if not conn:
        print("Error al conectar a la BD.")
        return False
    
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CierresMensualesNomina')
        BEGIN
            CREATE TABLE CierresMensualesNomina (
                CierreID INT IDENTITY(1,1) PRIMARY KEY,
                Mes INT NOT NULL,
                Anio INT NOT NULL,
                PeriodoTexto VARCHAR(60) NOT NULL,
                FechaCierre DATETIME DEFAULT GETDATE(),
                UsuarioCierreID INT NULL,
                UsuarioCierreNombre VARCHAR(150) NULL,
                TotalColaboradores INT DEFAULT 10,
                TotalPagados INT DEFAULT 0,
                TotalPendientes INT DEFAULT 0,
                MasaSalarialBruta DECIMAL(18,2) DEFAULT 0.00,
                TotalInssLaboral DECIMAL(18,2) DEFAULT 0.00,
                TotalBaseImponibleIr DECIMAL(18,2) DEFAULT 0.00,
                TotalIrDgi DECIMAL(18,2) DEFAULT 0.00,
                TotalSalarioNeto DECIMAL(18,2) DEFAULT 0.00,
                TotalInssPatronal DECIMAL(18,2) DEFAULT 0.00,
                TotalInatec DECIMAL(18,2) DEFAULT 0.00,
                TotalCargasPatronales DECIMAL(18,2) DEFAULT 0.00,
                TotalProvisionesAcumuladas DECIMAL(18,2) DEFAULT 0.00,
                CostoTotalEmpleador DECIMAL(18,2) DEFAULT 0.00,
                Estado VARCHAR(30) DEFAULT 'CERRADO',
                Observaciones NVARCHAR(MAX) NULL,
                DetalleSnapshotJson NVARCHAR(MAX) NULL,
                CONSTRAINT UQ_Cierre_Mes_Anio UNIQUE (Mes, Anio)
            );
            PRINT 'Tabla CierresMensualesNomina creada exitosamente.';
        END
        ELSE
        BEGIN
            PRINT 'Tabla CierresMensualesNomina ya existe.';
        END
    """)
    conn.commit()
    conn.close()
    print("Setup de tabla CierresMensualesNomina finalizado.")
    return True

if __name__ == '__main__':
    setup_cierres_mensuales()
