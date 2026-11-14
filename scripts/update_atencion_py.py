import os

path = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\atencion.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update citas_whatsapp() to pass clientes_dropdown
old_render = """    wa_config = get_whatsapp_config()
    
    return render_template('atencion/citas_whatsapp.html', 
                           citas=citas, 
                           stats=stats, 
                           mensajes=mensajes, 
                           total_mensajes=total_mensajes_count,
                           conversaciones=conversaciones,
                           numero_oficial=wa_config.get('telefono_numero', OFFICIAL_PHONE_NUMBER),
                           wa_config=wa_config,
                           public_webhook_url=get_public_webhook_url())"""

new_render = """    wa_config = get_whatsapp_config()
    
    # Lista de clientes y motos para selector modal
    cursor.execute(\"\"\"
        SELECT c.ClienteID, c.NombreCompleto, c.Telefono, m.MotoID, m.Marca, m.Modelo, m.Placa
        FROM Clientes c
        LEFT JOIN Motocicletas m ON c.ClienteID = m.ClienteID
        ORDER BY c.NombreCompleto ASC
    \"\"\")
    clientes_dropdown = cursor.fetchall()
    
    return render_template('atencion/citas_whatsapp.html', 
                           citas=citas, 
                           stats=stats, 
                           mensajes=mensajes, 
                           total_mensajes=total_mensajes_count,
                           conversaciones=conversaciones,
                           clientes_dropdown=clientes_dropdown,
                           numero_oficial=wa_config.get('telefono_numero', OFFICIAL_PHONE_NUMBER),
                           wa_config=wa_config,
                           public_webhook_url=get_public_webhook_url())"""

if old_render in content:
    content = content.replace(old_render, new_render, 1)
    print("Replaced render in citas_whatsapp()")
else:
    print("Warning: old_render not found directly, checking normalized...")
    # Normalize CRLF
    content = content.replace(old_render.replace("\n", "\r\n"), new_render.replace("\n", "\r\n"))
    print("Done normalized replacement")

# 2. Add endpoints: crear, editar, eliminar
new_endpoints = """
@atencion_bp.route('/citas_whatsapp/crear', methods=['POST'])
def citas_whatsapp_crear():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    cliente_id = request.form.get('cliente_id')
    moto_id = request.form.get('moto_id')
    fecha_prog = request.form.get('fecha_programada')
    tipo = request.form.get('tipo_mantenimiento', 'Preventivo')
    estado = request.form.get('estado', 'Pendiente')
    notas = request.form.get('notas', '')
    
    nombre_nuevo = request.form.get('nombre_nuevo', '').strip()
    telefono_nuevo = request.form.get('telefono_nuevo', '').strip()
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if not cliente_id and nombre_nuevo:
                cursor.execute("INSERT INTO Clientes (NombreCompleto, Telefono, CitasNoAsistidas) VALUES (?, ?, 0)", (nombre_nuevo, telefono_nuevo))
                cursor.execute("SELECT @@IDENTITY")
                cliente_id = int(cursor.fetchone()[0])
                
                modelo_nuevo = request.form.get('moto_nueva', '').strip()
                if modelo_nuevo:
                    cursor.execute("INSERT INTO Motocicletas (ClienteID, Marca, Modelo, Cilindraje) VALUES (?, 'Genesis', ?, 150)", (cliente_id, modelo_nuevo))
                    cursor.execute("SELECT @@IDENTITY")
                    moto_id = int(cursor.fetchone()[0])

            # Asegurar tipo de mantenimiento y estado permitidos
            tipos_validos = ['Preventivo', 'General', 'Correctivo', 'Express']
            estados_validos = ['Pendiente', 'Confirmada', 'Cancelada', 'No Asistio']
            
            tipo_final = tipo if tipo in tipos_validos else 'Preventivo'
            estado_final = estado if estado in estados_validos else 'Pendiente'

            cursor.execute(\"\"\"
                INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Notas, Origen, FechaCreacion)
                VALUES (?, ?, ?, ?, ?, ?, 'WhatsApp', GETDATE())
            \"\"\", (int(cliente_id) if cliente_id else None, int(moto_id) if moto_id else None, fecha_prog, tipo_final, estado_final, notas))
            conn.commit()
            flash("Cita registrada y agendada exitosamente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al registrar la cita: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.citas_whatsapp'))

@atencion_bp.route('/citas_whatsapp/editar/<int:cita_id>', methods=['POST'])
def citas_whatsapp_editar(cita_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    fecha_prog = request.form.get('fecha_programada')
    tipo = request.form.get('tipo_mantenimiento')
    estado = request.form.get('estado')
    notas = request.form.get('notas', '')
    
    tipos_validos = ['Preventivo', 'General', 'Correctivo', 'Express']
    estados_validos = ['Pendiente', 'Confirmada', 'Cancelada', 'No Asistio']
    
    tipo_final = tipo if tipo in tipos_validos else 'Preventivo'
    estado_final = estado if estado in estados_validos else 'Pendiente'

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(\"\"\"
                UPDATE CitasWhatsApp 
                SET FechaProgramada = ?, TipoMantenimiento = ?, Estado = ?, Notas = ?
                WHERE CitaID = ?
            \"\"\", (fecha_prog, tipo_final, estado_final, notas, cita_id))
            conn.commit()
            flash("Cita actualizada exitosamente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al actualizar la cita: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.citas_whatsapp'))

@atencion_bp.route('/citas_whatsapp/eliminar/<int:cita_id>', methods=['POST'])
def citas_whatsapp_eliminar(cita_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
            conn.commit()
            flash("Cita eliminada correctamente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al eliminar la cita: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.citas_whatsapp'))
"""

if "@atencion_bp.route('/citas_whatsapp/crear'" not in content:
    idx_target = content.find("@atencion_bp.route('/citas_whatsapp/estado/<int:cita_id>'")
    if idx_target != -1:
        content = content[:idx_target] + new_endpoints + "\n" + content[idx_target:]
        print("Inserted new endpoints before cambiar_estado_cita!")
    else:
        content += "\n" + new_endpoints
        print("Appended new endpoints at the end!")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved routes/atencion.py successfully.")
