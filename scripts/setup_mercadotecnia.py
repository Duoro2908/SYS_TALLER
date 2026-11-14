import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from database import get_db_connection

def setup_merca():
    conn = get_db_connection()
    if not conn:
        print("Error de conexión a la base de datos")
        return
        
    cursor = conn.cursor()

    # 1. Crear o verificar Rol Mercadotecnia
    cursor.execute("SELECT RolID, NombreRol FROM Roles WHERE NombreRol = 'Mercadotecnia'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("""
            INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller)
            VALUES ('Mercadotecnia', 0, 0, 0, 0)
        """)
        cursor.execute("SELECT SCOPE_IDENTITY()")
        rol_merca_id = int(cursor.fetchone()[0])
        print(f"Rol 'Mercadotecnia' creado con ID: {rol_merca_id}")
    else:
        rol_merca_id = row[0]
        print(f"Rol 'Mercadotecnia' ya existe con ID: {rol_merca_id}")

    # 2. Registrar o Actualizar Usuario Carlos Manuel Huete Huete (carlos.merca)
    pwd_hash = generate_password_hash('Manuel2026*', method='scrypt')
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'carlos.merca'")
    user_row = cursor.fetchone()
    if user_row:
        cursor.execute("""
            UPDATE Usuarios
            SET NombreCompleto = 'Carlos Manuel Huete Huete',
                PasswordHash = ?,
                RolID = ?,
                Activo = 1
            WHERE UsuarioID = ?
        """, (pwd_hash, rol_merca_id, user_row[0]))
        user_id = user_row[0]
        print(f"Usuario carlos.merca actualizado (ID: {user_id})")
    else:
        cursor.execute("""
            INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
            VALUES ('Carlos Manuel Huete Huete', 'carlos.merca', ?, ?, 1, 0, 0)
        """, (pwd_hash, rol_merca_id))
        cursor.execute("SELECT SCOPE_IDENTITY()")
        user_id = int(cursor.fetchone()[0])
        print(f"Usuario carlos.merca creado exitosamente (ID: {user_id})")

    # 3. Crear Tabla RifaPremios si no existe
    try:
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='RifaPremios' and xtype='U')
        BEGIN
            CREATE TABLE RifaPremios (
                RifaID INT IDENTITY(1,1) PRIMARY KEY,
                ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
                MesPeriodo NVARCHAR(50) NOT NULL,
                Cantidad INT DEFAULT 1,
                FechaAsignacion DATETIME DEFAULT GETDATE(),
                Estado NVARCHAR(50) DEFAULT 'Activa',
                GanadorClienteID INT NULL,
                GanadorNombre NVARCHAR(150) NULL,
                GanadorTelefono NVARCHAR(50) NULL,
                FechaSorteo DATETIME NULL,
                Observaciones NVARCHAR(255) NULL,
                UsuarioID INT NULL
            );
            PRINT 'Tabla RifaPremios creada exitosamente';
        END
        ELSE
        BEGIN
            PRINT 'Tabla RifaPremios ya existía';
        END
        """)
        print("Verificación de tabla RifaPremios completada.")
    except Exception as e:
        print(f"Error con tabla RifaPremios: {e}")

    conn.commit()

    # 4. Verificar datos finales
    cursor.execute("""
        SELECT u.UsuarioID, u.NombreCompleto, u.Email, r.NombreRol, u.Activo 
        FROM Usuarios u
        JOIN Roles r ON u.RolID = r.RolID
        WHERE u.Email = 'carlos.merca'
    """)
    u = cursor.fetchone()
    print("Usuario final:", u)

    conn.close()

if __name__ == '__main__':
    setup_merca()
