import pyodbc
from werkzeug.security import generate_password_hash
from database import get_db_connection

def setup_atencion():
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return
    cursor = conn.cursor()

    # Drop CitasWhatsApp table just in case it's not needed (optional, I'll leave it or drop it depending on user intent)
    # The user said "vamos a quitar de caja es citas de whatsapp", so I just remove the UI.
    
    # Create new Role
    cursor.execute("SELECT RolID FROM Roles WHERE NombreRol = 'Atención al Cliente'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller) VALUES ('Atención al Cliente', 0, 0, 0, 0)")
        cursor.execute("SELECT SCOPE_IDENTITY()")
        rol_id = int(cursor.fetchone()[0])
    else:
        rol_id = row[0]

    # Insert user Fanny
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'fanny.atencion'")
    row = cursor.fetchone()
    pwd_hash = generate_password_hash('Fanny2026*')
    if not row:
        cursor.execute("""
            INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo)
            VALUES ('Fanny Marisol Cruz Ruiz', 'fanny.atencion', ?, ?, 1)
        """, (pwd_hash, rol_id))
        print("Usuario Fanny creado.")
    else:
        cursor.execute("UPDATE Usuarios SET PasswordHash = ?, RolID = ?, NombreCompleto = 'Fanny Marisol Cruz Ruiz' WHERE Email = 'fanny.atencion'", (pwd_hash, rol_id))
        print("Usuario Fanny actualizado.")

    # Create AtencionTickets table
    try:
        cursor.execute("""
        CREATE TABLE AtencionTickets (
            TicketID INT IDENTITY(1,1) PRIMARY KEY,
            ClienteNombre VARCHAR(100),
            Telefono VARCHAR(20),
            Asunto VARCHAR(100),
            Mensaje TEXT,
            Estado VARCHAR(20) DEFAULT 'Pendiente',
            FechaCreacion DATETIME DEFAULT GETDATE()
        )
        """)
        print("Tabla AtencionTickets creada.")
    except Exception as e:
        print("Tabla AtencionTickets ya existe o error:", e)

    conn.commit()
    conn.close()
    print("Configuración de BD completada.")

if __name__ == '__main__':
    setup_atencion()
