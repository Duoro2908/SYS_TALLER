import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

def setup_users():
    conn = get_db_connection()
    if not conn:
        print("ERROR: No DB connection")
        return
        
    cursor = conn.cursor()
    
    # 1. Crear o verificar Rol 'Licenciada en Estadística'
    cursor.execute("SELECT RolID, NombreRol FROM Roles WHERE NombreRol = 'Licenciada en Estadística' OR NombreRol LIKE '%Estad%'")
    rol_est = cursor.fetchone()
    if not rol_est:
        cursor.execute("""
            INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller)
            VALUES ('Licenciada en Estadística', 1, 0, 0, 0)
        """)
        cursor.execute("SELECT SCOPE_IDENTITY()")
        rol_est_id = int(cursor.fetchone()[0])
        print(f"Rol 'Licenciada en Estadística' creado con ID: {rol_est_id}")
    else:
        rol_est_id = rol_est[0]
        print(f"Rol encontrado: {rol_est[1]} con ID: {rol_est_id}")
        
    # Verificar Rol 'Contador'
    cursor.execute("SELECT RolID, NombreRol FROM Roles WHERE NombreRol = 'Contador'")
    rol_cont = cursor.fetchone()
    if not rol_cont:
        cursor.execute("""
            INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller)
            VALUES ('Contador', 1, 0, 0, 0)
        """)
        cursor.execute("SELECT SCOPE_IDENTITY()")
        rol_cont_id = int(cursor.fetchone()[0])
        print(f"Rol 'Contador' creado con ID: {rol_cont_id}")
    else:
        rol_cont_id = rol_cont[0]
        print(f"Rol 'Contador' ID: {rol_cont_id}")
        
    # 2. Registrar o Actualizar Usuario Martha Jovana Lopez Chavarria
    martha_pwd = 'Martha2026*'
    martha_hash = generate_password_hash(martha_pwd, method='scrypt')
    assert check_password_hash(martha_hash, martha_pwd), "Error verificando hash de Martha"
    
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'martha.estadistica'")
    martha_row = cursor.fetchone()
    if martha_row:
        cursor.execute("""
            UPDATE Usuarios
            SET NombreCompleto = 'Martha Jovana Lopez Chavarria',
                PasswordHash = ?,
                RolID = ?,
                Activo = 1
            WHERE UsuarioID = ?
        """, (martha_hash, rol_est_id, martha_row[0]))
        print(f"Usuario Martha actualizado (ID: {martha_row[0]})")
    else:
        cursor.execute("""
            INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
            VALUES ('Martha Jovana Lopez Chavarria', 'martha.estadistica', ?, ?, 1, 18000, 0)
        """, (martha_hash, rol_est_id))
        print("Usuario Martha creado exitosamente.")
        
    # 3. Eliminar usuario Erwind si existe
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'erwind.contabilidad'")
    erwind_row = cursor.fetchone()
    if erwind_row:
        cursor.execute("DELETE FROM ContratosLaborales WHERE UsuarioID = ?", (erwind_row[0],))
        cursor.execute("DELETE FROM Usuarios WHERE UsuarioID = ?", (erwind_row[0],))
        print(f"Usuario Erwind eliminado (ID: {erwind_row[0]})")
        
    # 4. Asegurar Carlos Rene Gavarrete Calero en Finanzas (carlos.finanzas - Carlos2026*)
    carlos_pwd = 'Carlos2026*'
    carlos_hash = generate_password_hash(carlos_pwd, method='scrypt')
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'carlos.finanzas'")
    carlos_row = cursor.fetchone()
    if carlos_row:
        cursor.execute("""
            UPDATE Usuarios
            SET NombreCompleto = 'Carlos Rene Gavarrete Calero',
                PasswordHash = ?,
                RolID = ?,
                Activo = 1,
                SalarioBase = 16500,
                MesesAcumulados = 12
            WHERE UsuarioID = ?
        """, (carlos_hash, rol_cont_id, carlos_row[0]))
        print(f"Usuario carlos.finanzas verificado (ID: {carlos_row[0]})")
    else:
        cursor.execute("""
            INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
            VALUES ('Carlos Rene Gavarrete Calero', 'carlos.finanzas', ?, ?, 1, 16500, 12)
        """, (carlos_hash, rol_cont_id))
        print("Usuario carlos.finanzas creado exitosamente.")

    # 5. Asegurar Carlos Rene Gavarrete Calero en Contabilidad (carlos.contabilidad - Carlos2026**)
    carlos_cont_pwd = 'Carlos2026**'
    carlos_cont_hash = generate_password_hash(carlos_cont_pwd, method='scrypt')
    cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = 'carlos.contabilidad'")
    carlos_cont_row = cursor.fetchone()
    if carlos_cont_row:
        cursor.execute("""
            UPDATE Usuarios
            SET NombreCompleto = 'Carlos Rene Gavarrete Calero',
                PasswordHash = ?,
                RolID = ?,
                Activo = 1,
                SalarioBase = 0,
                MesesAcumulados = 0
            WHERE UsuarioID = ?
        """, (carlos_cont_hash, rol_cont_id, carlos_cont_row[0]))
        print(f"Usuario carlos.contabilidad verificado (ID: {carlos_cont_row[0]})")
    else:
        cursor.execute("""
            INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
            VALUES ('Carlos Rene Gavarrete Calero', 'carlos.contabilidad', ?, ?, 1, 0, 0)
        """, (carlos_cont_hash, rol_cont_id))
        print("Usuario carlos.contabilidad creado exitosamente.")
            
    conn.commit()
    
    # 6. Verificación final de usuarios
    print("--- USUARIOS FINALES VERIFICADOS ---")
    cursor.execute("""
        SELECT u.UsuarioID, u.NombreCompleto, u.Email, r.NombreRol, u.Activo 
        FROM Usuarios u
        JOIN Roles r ON u.RolID = r.RolID
        WHERE u.Email IN ('martha.estadistica', 'carlos.finanzas', 'carlos.contabilidad')
    """)
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Nombre: {row[1]} | Username: {row[2]} | Rol: {row[3]} | Activo: {row[4]}")
        
    conn.close()

if __name__ == '__main__':
    setup_users()
