import pyodbc
from werkzeug.security import generate_password_hash
from database import get_db_connection

def update_db():
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    # 1. Update Roles
    cursor.execute("UPDATE Roles SET NombreRol = 'Super Administrador' WHERE RolID = 1")
    cursor.execute("UPDATE Roles SET PuedeVerFinanzas = 1 WHERE RolID = 2") # Cajera now sees finanzas
    
    # Check if Role 4 exists
    cursor.execute("SELECT RolID FROM Roles WHERE NombreRol = 'Gerente General'")
    role4 = cursor.fetchone()
    if not role4:
        cursor.execute("INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller) VALUES ('Gerente General', 1, 1, 1, 1)")
        cursor.execute("SELECT SCOPE_IDENTITY()")
        role4_id = int(cursor.fetchone()[0])
    else:
        role4_id = role4.RolID

    # 2. Update Users
    users_data = [
        # (ID, NombreCompleto, Email, Password, RolID)
        (1, 'Elvin Alexander Mendez Cruz', 'elvin.admin', 'Elvin2026*', 1),
        (2, 'Jhosep David Cooper Sandino', 'jhosep.gerente', 'Jhosep2026*', role4_id),
        (3, 'Roxana Camila Cooper Sandino', 'roxana.caja', 'Roxana2026*', 2),
        (4, 'Jose Francisco Cooper Mendez', 'jose.mecanico', 'Jose2026*', 3),
        (5, 'Elmerson Daniel Cruz Ruiz', 'elmerson.mecanico', 'Elmerson2026*', 3)
    ]

    for uid, nombre, email, pwd, rol in users_data:
        pwd_hash = generate_password_hash(pwd)
        cursor.execute("""
            UPDATE Usuarios 
            SET NombreCompleto = ?, Email = ?, PasswordHash = ?, RolID = ?
            WHERE UsuarioID = ?
        """, (nombre, email, pwd_hash, rol, uid))

    conn.commit()
    conn.close()
    print("Usuarios actualizados correctamente en la base de datos.")

if __name__ == '__main__':
    update_db()
