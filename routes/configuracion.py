from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database import get_db_connection
from werkzeug.security import generate_password_hash

settings_bp = Blueprint('settings', __name__)
configuracion_bp = settings_bp

@settings_bp.route('/admin/settings', methods=['GET', 'POST'])
def index():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5]:
        flash("Acceso denegado. Solo administradores pueden acceder a esta sección.", "error")
        return redirect(url_for('index'))
        
    rol_id = session.get('rol_id')
    usuarios = []
    
    if rol_id in [1, 5]:
        # Ambos pueden ver la lista, excepto al Super Administrador (Rol 1)
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UsuarioID, NombreCompleto, Email, SalarioBase, RolID, MesesAcumulados FROM Usuarios WHERE Activo = 1 AND RolID != 1")
            usuarios = cursor.fetchall()
            conn.close()

    if request.method == 'POST':
        action = request.form.get('action')
        
        # Cambio de contraseña
        if action == 'change_password':
            target_usuario_id = request.form.get('usuario_id')
            nueva_password = request.form.get('nueva_password')
            confirmar_password = request.form.get('confirmar_password')
            
            # Validar permisos
            if rol_id != 1 and str(target_usuario_id) != str(session.get('usuario_id')):
                flash("No tienes permisos para cambiar la contraseña de otro usuario.", "error")
                return redirect(url_for('settings.index'))
                
            if nueva_password and nueva_password == confirmar_password:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        hashed = generate_password_hash(nueva_password, method='scrypt')
                        cursor.execute("UPDATE Usuarios SET PasswordHash = ? WHERE UsuarioID = ?", (hashed, target_usuario_id))
                        conn.commit()
                        # flash("Contraseña actualizada exitosamente.", "success")
                    except Exception as e:
                        flash("Error al actualizar la contraseña.", "error")
                    finally:
                        conn.close()
            else:
                flash("Las contraseñas no coinciden o están vacías.", "error")
                
        # Añadir nuevo empleado
        elif action == 'add_user' and rol_id in [1, 5]:
            nombre = request.form.get('new_nombre')
            email = request.form.get('new_email')
            password = request.form.get('new_password')
            rol = request.form.get('new_rol')
            salario = request.form.get('new_salario', 0)
            meses = request.form.get('new_meses', 0)
            
            if nombre and email and password and rol:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        # Check if email exists
                        cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Email = ?", (email,))
                        if cursor.fetchone():
                            flash("El nombre de usuario (Email) ya existe. Intenta con otro.", "error")
                        else:
                            hashed = generate_password_hash(password, method='scrypt')
                            cursor.execute("""
                                INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
                                VALUES (?, ?, ?, ?, 1, ?, ?)
                            """, (nombre, email, hashed, rol, salario, meses))
                            conn.commit()
                            # flash("Empleado registrado exitosamente.", "success")
                    except Exception as e:
                        flash(f"Error al registrar empleado: {e}", "error")
                    finally:
                        conn.close()
            else:
                flash("Faltan datos para registrar al empleado.", "error")
                
        # Eliminar (desactivar) empleado
        elif action == 'delete_user' and rol_id in [1, 5]:
            target_id = request.form.get('delete_usuario_id')
            if str(target_id) == str(session.get('usuario_id')):
                flash("No puedes eliminarte a ti mismo.", "error")
            elif target_id:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE Usuarios SET Activo = 0 WHERE UsuarioID = ?", (target_id,))
                        conn.commit()
                        # flash("Empleado eliminado exitosamente.", "success")
                    except Exception as e:
                        flash(f"Error al eliminar empleado: {e}", "error")
                    finally:
                        conn.close()
                        
        # Actualizar Salario y Meses
        elif action == 'update_salary' and rol_id in [1, 5]:
            target_id = request.form.get('usuario_id')
            nuevo_salario = request.form.get('salario')
            nuevos_meses = request.form.get('meses', 0)
            
            if target_id and nuevo_salario is not None:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE Usuarios SET SalarioBase = ?, MesesAcumulados = ? WHERE UsuarioID = ?", (nuevo_salario, nuevos_meses, target_id))
                        conn.commit()
                        # flash("Datos de pago actualizados exitosamente.", "success")
                    except Exception as e:
                        flash(f"Error al actualizar datos de pago: {e}", "error")
                    finally:
                        conn.close()
                        
        return redirect(url_for('settings.index'))
        
    return render_template('settings/index.html', usuarios=usuarios)
