import pyodbc
from config import Config

def fix_and_run_db_updates():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()

        print("Fijando marcas de motocicletas a 'Genesis'...")
        cursor.execute("UPDATE Motocicletas SET Marca = 'Genesis'")

        print("Modificando restricciones de Motocicletas...")
        cursor.execute("""
            IF EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CHK_Moto_Cilindraje')
            BEGIN
                ALTER TABLE Motocicletas DROP CONSTRAINT CHK_Moto_Cilindraje;
            END
        """)
        cursor.execute("ALTER TABLE Motocicletas ADD CONSTRAINT CHK_Moto_Cilindraje CHECK (Cilindraje <= 250)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CHK_Moto_Marca')
            BEGIN
                ALTER TABLE Motocicletas ADD CONSTRAINT CHK_Moto_Marca CHECK (Marca = 'Genesis');
            END
        """)

        print("Insertando proveedor Imgesa...")
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM Proveedores WHERE NombreEmpresa = 'Imgesa')
            BEGIN
                INSERT INTO Proveedores (RUC, NombreEmpresa, Telefono, DiasCredito)
                VALUES ('J0310000000000', 'Imgesa', '2222-2222', 30);
            END
        """)

        print("Agregando ProveedorID a Productos...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Productos') AND name = 'ProveedorID')
            BEGIN
                ALTER TABLE Productos ADD ProveedorID INT NULL FOREIGN KEY REFERENCES Proveedores(ProveedorID);
            END
        """)

        print("Creando tabla PedidosInventario...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PedidosInventario]') AND type in (N'U'))
            BEGIN
                CREATE TABLE PedidosInventario (
                    PedidoID INT IDENTITY(1,1) PRIMARY KEY,
                    ProveedorID INT FOREIGN KEY REFERENCES Proveedores(ProveedorID),
                    UsuarioSolicitaID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
                    FechaSolicitud DATETIME DEFAULT GETDATE(),
                    Estado NVARCHAR(30) DEFAULT 'Pendiente' CHECK (Estado IN ('Pendiente', 'Aprobado', 'Rechazado')),
                    TotalEstimado DECIMAL(10,2) DEFAULT 0
                );
            END
        """)

        print("Creando tabla DetallePedidosInventario...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DetallePedidosInventario]') AND type in (N'U'))
            BEGIN
                CREATE TABLE DetallePedidosInventario (
                    DetalleID INT IDENTITY(1,1) PRIMARY KEY,
                    PedidoID INT FOREIGN KEY REFERENCES PedidosInventario(PedidoID),
                    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
                    Cantidad INT NOT NULL CHECK (Cantidad > 0),
                    CostoUnitarioEstimado DECIMAL(10,2) NOT NULL
                );
            END
        """)

        conn.commit()
        print("¡Actualizaciones completadas exitosamente!")
        conn.close()
    except pyodbc.Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_and_run_db_updates()
