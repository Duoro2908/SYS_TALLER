import re
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database import get_db_connection

import datetime
from flask import jsonify
from whatsapp_bot import (
    process_incoming_whatsapp_message, OFFICIAL_PHONE_NUMBER, 
    send_whatsapp_message, send_whatsapp_message_detailed, get_whatsapp_config, set_bot_status, save_whatsapp_config,
    safe_print
)

import os

def get_public_webhook_url():
    """
    Detecta automáticamente o recupera la URL pública del Webhook de WhatsApp:
    1. Si está definida la variable de entorno PUBLIC_WEBHOOK_URL, la usa.
    2. Si se guardó una URL de túnel/dominio en ConfiguracionWhatsApp, la usa.
    3. Si se accede desde un dominio público en la web (con HTTPS), genera f"{scheme}://{host}/atencion/whatsapp/webhook".
    4. Fallback por defecto.
    """
    env_url = os.environ.get('PUBLIC_WEBHOOK_URL')
    if env_url:
        return env_url
    try:
        cfg = get_whatsapp_config()
        saved = cfg.get('webhook_url', '')
        if saved and saved.strip():
            url = saved.strip()
            if not url.endswith('/atencion/whatsapp/webhook'):
                if url.endswith('/'):
                    url = url[:-1]
                if not url.endswith('/whatsapp/webhook'):
                    url = f"{url}/atencion/whatsapp/webhook"
            return url
    except Exception:
        pass
    try:
        if request:
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            if 'localhost' not in host and '127.0.0.1' not in host:
                return f"{scheme}://{host}/atencion/whatsapp/webhook"
    except Exception:
        pass
    return "https://tudominio-o-tunel.trycloudflare.com/atencion/whatsapp/webhook"

atencion_bp = Blueprint('atencion', __name__, url_prefix='/atencion')

@atencion_bp.before_request
def check_role():
    # El Webhook oficial de WhatsApp es público para recibir llamadas de la API de Meta
    if request.path.endswith('/whatsapp/webhook'):
        return None
        
    if 'usuario_id' not in session:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Tu sesión ha expirado. Por favor recarga la página e inicia sesión nuevamente.'}), 401
        return redirect(url_for('auth.login'))
    
    rol = session.get('rol_id')
    # Permitir al rol Atención al Cliente (1008), Gerente (5) o Administrador (1)
    if rol not in (1, 5, 1008):
        if request.is_json:
            return jsonify({'success': False, 'error': 'No tienes permiso para realizar esta acción.'}), 403
        flash("No tienes permiso para acceder a este módulo", "error")
        return redirect(url_for('index'))

@atencion_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rol = session.get('rol_id')
    try:
        rol_num = int(rol)
    except (TypeError, ValueError):
        rol_num = 0
        
    vista = request.args.get('view')
        
    if rol_num == 5 or vista == 'gerencia':
        # El gerente o quien acceda desde el menú de gerencia solo ve los casos escalados a gerencia
        cursor.execute("SELECT * FROM AtencionTickets WHERE Estado = 'Escalado a Gerencia' ORDER BY FechaCreacion DESC")
    else:
        # Atención al cliente y Administradores ven todo
        cursor.execute("SELECT * FROM AtencionTickets ORDER BY FechaCreacion DESC")
        
    tickets = cursor.fetchall()
    conn.close()
    return render_template('atencion/index.html', tickets=tickets)

@atencion_bp.route('/escalar/<int:id>', methods=['POST'])
def escalar_ticket(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE AtencionTickets SET Estado = 'Escalado a Gerencia' WHERE TicketID = ?", (id,))
            conn.commit()
            flash("El caso ha sido escalado exitosamente a la Gerencia.", "success")
        except Exception as e:
            flash(f"Error al escalar el caso: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.index'))

@atencion_bp.route('/eliminar_ticket/<int:id>', methods=['POST'])
def eliminar_ticket(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM AtencionTickets WHERE TicketID = ?", (id,))
            conn.commit()
            flash("La queja o sugerencia ha sido eliminada del buzón.", "success")
        except Exception as e:
            flash(f"Error al eliminar el ticket: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.index'))

def _safe_atencion_redirect(default_endpoint):
    next_url = (request.form.get('next_url') or '').strip()
    if next_url.startswith('/atencion/'):
        return redirect(next_url)
    return redirect(url_for(default_endpoint))


@atencion_bp.route('/citas_taller')
def citas_taller():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 8, 1008]:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('atencion.index'))

    from routes.mecanico import obtener_datos_citas_programadas
    citas, mantenimientos, productos = obtener_datos_citas_programadas(
        conn, session.get('rol_id'), session.get('usuario_id')
    )
    conn.close()

    return render_template(
        'mecanico/citas_programadas.html',
        citas=citas,
        mantenimientos=mantenimientos,
        productos=productos,
        next_endpoint='atencion.citas_taller',
    )


@atencion_bp.route('/citas_whatsapp', methods=['GET'])
def citas_whatsapp():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('atencion.index'))
        
    cursor = conn.cursor()
    
    # 1. Obtener únicamente Citas pendientes por agendar originadas vía WhatsApp
    cursor.execute("""
        SELECT cw.CitaID, cw.ClienteID, c.NombreCompleto, c.Telefono, 
               m.Marca, m.Modelo, cw.FechaProgramada, cw.TipoMantenimiento, 
               cw.Estado, cw.Notas, cw.FechaCreacion, cw.MotoID, cw.MecanicoAsignadoID
        FROM CitasWhatsApp cw
        LEFT JOIN Clientes c ON cw.ClienteID = c.ClienteID
        LEFT JOIN Motocicletas m ON cw.MotoID = m.MotoID
        WHERE ISNULL(cw.Origen, 'WhatsApp') = 'WhatsApp'
          AND (cw.Estado = 'Pendiente' OR cw.Estado IS NULL)
          AND cw.MecanicoAsignadoID IS NULL
        ORDER BY cw.FechaProgramada ASC
    """)
    citas_rows = cursor.fetchall()
    
    citas = []
    hoy_str = datetime.datetime.now().strftime('%Y-%m-%d')
    for r in citas_rows:
        fecha_prog_dt = r[6]
        fecha_prog_str = fecha_prog_dt.strftime('%Y-%m-%d %H:%M') if fecha_prog_dt else ''
        fecha_prog_iso = fecha_prog_dt.strftime('%Y-%m-%dT%H:%M') if fecha_prog_dt else ''
        tel_raw = r[3] or ''
        tel_clean = re.sub(r'\D', '', tel_raw)
        if len(tel_clean) == 8:
            tel_clean = '505' + tel_clean
        citas.append({
            'cita_id': r[0],
            'cliente_id': r[1],
            'cliente_nombre': r[2] or 'Cliente Desconocido',
            'telefono': tel_raw or 'Sin Teléfono',
            'telefono_clean': tel_clean,
            'moto_info': f"{r[4]} {r[5]}" if r[4] else "Sin Moto Registrada",
            'fecha_programada': fecha_prog_str,
            'fecha_prog_iso': fecha_prog_iso,
            'fecha_formateada': fecha_prog_dt.strftime('%d/%m/%Y %I:%M %p') if fecha_prog_dt else 'N/A',
            'tipo': r[7] or 'Preventivo',
            'estado': r[8] or 'Pendiente',
            'notas': r[9] or '',
            'fecha_creacion': r[10].strftime('%d/%m/%Y %H:%M') if r[10] else '',
            'moto_id': r[11],
            'mecanico_asignado_id': r[12] if len(r) > 12 else None
        })
        
    # 2. Métricas KPI (Total pendientes en WhatsApp y confirmadas transferidas a Taller)
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM CitasWhatsApp WHERE ISNULL(Origen, 'WhatsApp') = 'WhatsApp' AND (Estado = 'Pendiente' OR Estado IS NULL) AND MecanicoAsignadoID IS NULL),
            (SELECT COUNT(*) FROM CitasWhatsApp WHERE Estado = 'Confirmada' AND MecanicoAsignadoID IS NOT NULL)
    """)
    counts = cursor.fetchone()
    count_pend = counts[0] if counts else 0
    count_conf = counts[1] if counts else 0
    
    stats = {
        'total': count_pend,
        'pendientes': count_pend,
        'confirmadas': count_conf,
        'hoy': sum(1 for c in citas if c['fecha_programada'].startswith(hoy_str))
    }
    
    # 3. Obtener Historial de Mensajes Recientes
    cursor.execute("""
        SELECT TOP 50 mw.MensajeID, mw.TelefonoCliente, mw.ClienteID, c.NombreCompleto, 
                      mw.Direccion, mw.Contenido, mw.EsAutoRespuesta, mw.FechaHora, mw.CitaID
        FROM MensajesWhatsApp mw
        LEFT JOIN Clientes c ON mw.ClienteID = c.ClienteID
        ORDER BY mw.MensajeID DESC
    """)
    mensajes_rows = cursor.fetchall()
    
    mensajes = []
    for m in mensajes_rows:
        mensajes.append({
            'mensaje_id': m[0],
            'telefono': m[1],
            'cliente_id': m[2],
            'cliente_nombre': m[3] or m[1],
            'direccion': m[4],
            'contenido': m[5],
            'es_bot': bool(m[6]),
            'fecha': m[7].strftime('%d/%m %H:%M') if m[7] else '',
            'cita_id': m[8]
        })
        
    # 4. Obtener Lista de Conversaciones Activas
    cursor.execute("""
        SELECT mw.TelefonoCliente, 
               COALESCE(c.NombreCompleto, mw.TelefonoCliente) as Nombre,
               MAX(mw.FechaHora) as UltimoMensajeFecha,
               (SELECT TOP 1 Contenido FROM MensajesWhatsApp WHERE TelefonoCliente = mw.TelefonoCliente ORDER BY FechaHora DESC) as UltimoContenido,
               (SELECT TOP 1 Direccion FROM MensajesWhatsApp WHERE TelefonoCliente = mw.TelefonoCliente ORDER BY FechaHora DESC) as UltimaDireccion,
               COUNT(*) as TotalMensajes
        FROM MensajesWhatsApp mw
        LEFT JOIN Clientes c ON mw.ClienteID = c.ClienteID
        GROUP BY mw.TelefonoCliente, c.NombreCompleto
        ORDER BY MAX(mw.FechaHora) DESC
    """)
    conversaciones_rows = cursor.fetchall()
    conversaciones = []
    for row in conversaciones_rows:
        dt = row[2]
        conversaciones.append({
            'telefono': row[0],
            'nombre': row[1] or row[0],
            'fecha': dt.strftime('%I:%M %p') if dt else '',
            'ultimo_mensaje': row[3] or '',
            'ultima_direccion': row[4] or '',
            'total_mensajes': row[5]
        })

    # Lista de clientes y motos para selector modal
    cursor.execute("""
        SELECT c.ClienteID, c.NombreCompleto, c.Telefono, m.MotoID, m.Marca, m.Modelo, m.Placa
        FROM Clientes c
        LEFT JOIN Motocicletas m ON c.ClienteID = m.ClienteID
        ORDER BY c.NombreCompleto ASC
    """)
    clientes_dropdown = cursor.fetchall()

    cursor.execute("""
        SELECT UsuarioID, NombreCompleto 
        FROM Usuarios 
        WHERE RolID = 3 AND Activo = 1 
        ORDER BY NombreCompleto ASC
    """)
    mecanicos = cursor.fetchall()

    conn.close()
    
    # 5. Total real de mensajes registrados para sincronización precisa
    total_mensajes_count = len(mensajes)
    conn_count = get_db_connection()
    if conn_count:
        try:
            c_cur = conn_count.cursor()
            c_cur.execute("SELECT COUNT(*) FROM MensajesWhatsApp")
            total_mensajes_count = c_cur.fetchone()[0]
        except Exception:
            pass
        finally:
            conn_count.close()

    wa_config = get_whatsapp_config()
    
    return render_template('atencion/citas_whatsapp.html', 
                           citas=citas, 
                           stats=stats, 
                           mensajes=mensajes, 
                           total_mensajes=total_mensajes_count,
                           conversaciones=conversaciones,
                           clientes_dropdown=clientes_dropdown,
                           mecanicos=mecanicos,
                           numero_oficial=wa_config.get('telefono_numero', OFFICIAL_PHONE_NUMBER),
                           wa_config=wa_config,
                           public_webhook_url=get_public_webhook_url())


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
                # Validar que el nombre no contenga números y solo letras/espacios
                if any(char.isdigit() for char in nombre_nuevo) or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\.-]{3,80}$", nombre_nuevo):
                    flash('El nombre del cliente solo debe contener letras y espacios (sin números).', 'error')
                    return redirect(url_for('atencion.citas_whatsapp'))
                if telefono_nuevo and (not telefono_nuevo.isdigit() or len(telefono_nuevo) < 8 or len(telefono_nuevo) > 15):
                    flash('El teléfono del cliente debe contener entre 8 y 15 dígitos numéricos.', 'error')
                    return redirect(url_for('atencion.citas_whatsapp'))

                cursor.execute("INSERT INTO Clientes (NombreCompleto, Telefono, CitasNoAsistidas) VALUES (?, ?, 0)", (nombre_nuevo, telefono_nuevo))
                cursor.execute("SELECT @@IDENTITY")
                cliente_id = int(cursor.fetchone()[0])
                
                modelo_nuevo = request.form.get('moto_nueva', '').strip()
                if modelo_nuevo:
                    cursor.execute("INSERT INTO Motocicletas (ClienteID, Marca, Modelo, Cilindraje) VALUES (?, 'Genesis', ?, 150)", (cliente_id, modelo_nuevo))
                    cursor.execute("SELECT @@IDENTITY")
                    moto_id = int(cursor.fetchone()[0])
            elif cliente_id and not moto_id:
                cursor.execute("SELECT TOP 1 MotoID FROM Motocicletas WHERE ClienteID = ?", (int(cliente_id),))
                m_row = cursor.fetchone()
                if m_row:
                    moto_id = m_row[0]

            # Asegurar tipo de mantenimiento y estado permitidos
            tipos_validos = ['Preventivo', 'General', 'Correctivo']
            estados_validos = ['Pendiente', 'Confirmada', 'Cancelada', 'No Asistio']
            
            tipo_final = tipo if tipo in tipos_validos else 'Preventivo'
            estado_final = estado if estado in estados_validos else 'Pendiente'

            cursor.execute("""
                INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Notas, Origen, FechaCreacion)
                VALUES (?, ?, ?, ?, ?, ?, 'WhatsApp', GETDATE())
            """, (int(cliente_id) if cliente_id else None, int(moto_id) if moto_id else None, fecha_prog, tipo_final, estado_final, notas))
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
    
    tipos_validos = ['Preventivo', 'General', 'Correctivo']
    estados_validos = ['Pendiente', 'Confirmada', 'Cancelada', 'No Asistio']
    
    tipo_final = tipo if tipo in tipos_validos else 'Preventivo'
    estado_final = estado if estado in estados_validos else 'Pendiente'

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE CitasWhatsApp 
                SET FechaProgramada = ?, TipoMantenimiento = ?, Estado = ?, Notas = ?
                WHERE CitaID = ?
            """, (fecha_prog, tipo_final, estado_final, notas, cita_id))
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
            # Desvincular referencias para evitar conflicto con llaves foráneas
            cursor.execute("UPDATE OrdenesTrabajo SET CitaID = NULL WHERE CitaID = ?", (cita_id,))
            cursor.execute("UPDATE MensajesWhatsApp SET CitaID = NULL WHERE CitaID = ?", (cita_id,))
            cursor.execute("DELETE FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
            conn.commit()
            flash("Cita eliminada correctamente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al eliminar la cita: {e}", "error")
        finally:
            conn.close()
    return _safe_atencion_redirect('atencion.citas_whatsapp')

@atencion_bp.route('/citas_whatsapp/estado/<int:cita_id>', methods=['POST'])
def cambiar_estado_cita(cita_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    nuevo_estado = request.form.get('nuevo_estado', 'Pendiente')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE CitasWhatsApp SET Estado = ? WHERE CitaID = ?", (nuevo_estado, cita_id))
            
            # Registrar notificación saliente
            cursor.execute("SELECT c.Telefono, cw.ClienteID FROM CitasWhatsApp cw JOIN Clientes c ON cw.ClienteID = c.ClienteID WHERE cw.CitaID = ?", (cita_id,))
            row = cursor.fetchone()
            if row:
                telefono, cliente_id = row[0], row[1]
                msg_text = f"📢 Su cita #{cita_id} en Taller CR ha cambiado a estado: *{nuevo_estado}*."
                cursor.execute("""
                    INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID)
                    VALUES (?, ?, 'Saliente', ?, 0, ?)
                """, (telefono, cliente_id, msg_text, cita_id))
                
            conn.commit()
            flash(f'Estado de la cita #{cita_id} actualizado a "{nuevo_estado}".', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al actualizar cita: {e}', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('atencion.citas_whatsapp'))

@atencion_bp.route('/citas_whatsapp/agendar_en_taller', methods=['POST'])
def agendar_en_taller():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3, 5, 8, 1008]:
        return redirect(url_for('auth.login'))
        
    cita_id = request.form.get('cita_id')
    mecanico_id = request.form.get('mecanico_id')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    tipo_mantenimiento = request.form.get('tipo_mantenimiento', 'Preventivo')
    
    if not cita_id or not mecanico_id or not fecha or not hora:
        flash('⚠️ Por favor complete todos los campos para agendar la cita en el taller.', 'warning')
        return redirect(url_for('atencion.citas_whatsapp'))
        
    try:
        if 'AM' in hora.upper() or 'PM' in hora.upper():
            dt_prog = datetime.datetime.strptime(f"{fecha} {hora.strip()}", "%Y-%m-%d %I:%M %p")
        else:
            dt_prog = datetime.datetime.strptime(f"{fecha} {hora.strip()}", "%Y-%m-%d %H:%M")
    except Exception:
        flash('⚠️ Formato de fecha u hora no válido.', 'error')
        return redirect(url_for('atencion.citas_whatsapp'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('atencion.citas_whatsapp'))
        
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NombreCompleto FROM Usuarios WHERE UsuarioID = ?", (mecanico_id,))
        mec_row = cursor.fetchone()
        mec_nombre = mec_row[0] if mec_row else 'Mecánico'
        
        # Validar disponibilidad del mecánico
        cursor.execute("""
            SELECT COUNT(*) 
            FROM CitasWhatsApp 
            WHERE MecanicoAsignadoID = ? 
              AND CAST(FechaProgramada AS DATE) = CAST(? AS DATE)
              AND DATEPART(HOUR, FechaProgramada) = ?
              AND Estado = 'Confirmada'
              AND CitaID != ?
        """, (mecanico_id, dt_prog.strftime('%Y-%m-%d'), dt_prog.hour, cita_id))
        
        citas_ocupadas = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM OrdenesTrabajo 
            WHERE MecanicoID = ? 
              AND Estado = 'En Proceso'
              AND CAST(FechaIngreso AS DATE) = CAST(? AS DATE)
              AND DATEPART(HOUR, FechaIngreso) = ?
        """, (mecanico_id, dt_prog.strftime('%Y-%m-%d'), dt_prog.hour))
        
        ordenes_ocupadas = cursor.fetchone()[0]
        
        if citas_ocupadas > 0 or ordenes_ocupadas > 0:
            flash(
                f"⚠️ Conflicto de horario: El mecánico {mec_nombre} ya tiene asignada una cita o trabajo para el {dt_prog.strftime('%d/%m/%Y')} a las {hora}. "
                f"Por favor selecciona otro horario o asigna a otro mecánico disponible.",
                "warning"
            )
            return redirect(url_for('atencion.citas_whatsapp'))
            
        # Asegurar que la cita tenga MotoID
        cursor.execute("SELECT ClienteID, MotoID FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
        c_info = cursor.fetchone()
        if c_info:
            cliente_id, moto_id = c_info[0], c_info[1]
            if not moto_id:
                cursor.execute("SELECT TOP 1 MotoID FROM Motocicletas WHERE ClienteID = ?", (cliente_id,))
                m_row = cursor.fetchone()
                if m_row:
                    moto_id = m_row[0]
                else:
                    import random
                    placa_gen = f"M-{random.randint(10000, 99999)}"
                    cursor.execute("""
                        INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje)
                        OUTPUT INSERTED.MotoID
                        VALUES (?, ?, 'Genesis', 'Standard', 2022, 125)
                    """, (cliente_id, placa_gen))
                    moto_id = cursor.fetchone()[0]
                cursor.execute("UPDATE CitasWhatsApp SET MotoID = ? WHERE CitaID = ?", (moto_id, cita_id))
                
        cursor.execute("""
            UPDATE CitasWhatsApp 
            SET MecanicoAsignadoID = ?,
                FechaProgramada = ?,
                TipoMantenimiento = ?,
                Estado = 'Confirmada'
            WHERE CitaID = ?
        """, (mecanico_id, dt_prog, tipo_mantenimiento, cita_id))
        
        conn.commit()
        flash(
            f"✅ Cita #{cita_id} agendada exitosamente en el Taller con {mec_nombre} para el {dt_prog.strftime('%d/%m/%Y a las %I:%M %p')}. "
            f"El mantenimiento ya está listo en 'Citas Programadas'.",
            "success"
        )
    except Exception as e:
        conn.rollback()
        flash(f"Error al agendar la cita en el taller: {str(e)}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('mechanic.citas_programadas'))


@atencion_bp.route('/citas_whatsapp/crear_orden/<int:cita_id>', methods=['POST'])
def crear_orden_desde_cita(cita_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 8, 1008]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('atencion.citas_whatsapp'))
        
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ClienteID, MotoID, TipoMantenimiento, Notas FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
        cita = cursor.fetchone()
        if not cita:
            flash('Cita no encontrada.', 'error')
            conn.close()
            return redirect(url_for('atencion.citas_whatsapp'))
            
        cliente_id, moto_id, tipo_servicio, notas = cita[0], cita[1], cita[2], cita[3]
        
        if not moto_id:
            cursor.execute("SELECT TOP 1 MotoID FROM Motocicletas WHERE ClienteID = ?", (cliente_id,))
            m_row = cursor.fetchone()
            if m_row:
                moto_id = m_row[0]
            else:
                import random
                placa_gen = f"M-{random.randint(10000, 99999)}"
                cursor.execute("""
                    INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje)
                    OUTPUT INSERTED.MotoID
                    VALUES (?, ?, 'Genesis', 'Motoneta / Standard', 2022, 125)
                """, (cliente_id, placa_gen))
                moto_id = cursor.fetchone()[0]
                
        # Obtener mecánico activo para asignación de la orden en Taller
        mecanico_id = session.get('usuario_id') if session.get('rol_id') in [1, 3] else None
        if not mecanico_id:
            cursor.execute("SELECT TOP 1 UsuarioID FROM Usuarios WHERE RolID = 3 AND Activo = 1")
            mec_row = cursor.fetchone()
            mecanico_id = mec_row[0] if mec_row else 1

        tipo_srv = tipo_servicio or 'Preventivo'
        cursor.execute("SELECT TOP 1 PrecioBase, DescripcionDetallada FROM CatalogoMantenimientos WHERE Tipo = ?", (tipo_srv,))
        cat_row = cursor.fetchone()
        costo_mano_obra = float(cat_row[0]) if cat_row and cat_row[0] else 350.0
        desc_detallada = cat_row[1] if cat_row and cat_row[1] else f"Mantenimiento {tipo_srv}"

        # 1. Crear Orden de Trabajo en estado 'En Proceso' (inicia formalmente el mantenimiento en Taller)
        cursor.execute("""
            INSERT INTO OrdenesTrabajo (MotoID, MecanicoID, TipoServicio, Estado, FechaIngreso, KilometrajeIngreso, ProblemaReportado, CitaID)
            OUTPUT INSERTED.OrdenID
            VALUES (?, ?, ?, 'En Proceso', GETDATE(), 0, ?, ?)
        """, (moto_id, mecanico_id, tipo_srv, f"Mantenimiento iniciado desde Cita WhatsApp #{cita_id}. {notas or ''}", cita_id))
        
        orden_id = cursor.fetchone()[0]
        
        # 2. Registrar Mano de Obra inicial
        cursor.execute("""
            INSERT INTO OrdenManoObra (OrdenID, DescripcionServicio, CostoSugerido)
            VALUES (?, ?, ?)
        """, (orden_id, f"Mantenimiento {tipo_srv} - {desc_detallada}", costo_mano_obra))

        # 3. Marcar cita WhatsApp como Confirmada
        cursor.execute("UPDATE CitasWhatsApp SET Estado = 'Confirmada' WHERE CitaID = ?", (cita_id,))
        
        conn.commit()
        flash(f'¡Éxito! Orden de Trabajo #{orden_id} generada y enviada al Taller. El mantenimiento ha iniciado en estado "En Proceso".', 'success')
        conn.close()

        if session.get('rol_id') in [1, 3]:
            return redirect(url_for('mechanic.ordenes_list'))
        return redirect(url_for('atencion.citas_whatsapp'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Error al generar Orden de Trabajo para el Taller: {e}', 'error')
        return _safe_atencion_redirect('atencion.citas_whatsapp')


@atencion_bp.route('/whatsapp/responder_manual', methods=['POST'])
def whatsapp_responder_manual():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 8, 1008]:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
    data = request.get_json() or {}
    telefono = data.get('telefono')
    mensaje = data.get('mensaje')
    
    if not telefono or not mensaje:
        return jsonify({'success': False, 'error': 'Teléfono y mensaje obligatorios'}), 400
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ClienteID FROM Clientes WHERE Telefono LIKE ? OR Telefono = ?", (f"%{telefono[-8:]}", telefono))
            cli = cursor.fetchone()
            cliente_id = cli[0] if cli else None
            
            cursor.execute("""
                INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta)
                VALUES (?, ?, 'Saliente', ?, 0)
            """, (telefono, cliente_id, mensaje))
            
            # Enviar por API de Meta
            enviado = send_whatsapp_message(telefono, mensaje)
            if not enviado:
                print("Advertencia: No se pudo enviar el mensaje por Meta API (probablemente faltan tokens).")
                
            conn.commit()
            return jsonify({'success': True, 'mensaje': 'Mensaje manual registrado y enviado con éxito.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Error de base de datos'}), 500

@atencion_bp.route('/whatsapp/chat_history/<telefono>', methods=['GET'])
def whatsapp_chat_history(telefono):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 8, 1008]:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Direccion, Contenido, FechaHora, EsAutoRespuesta
                FROM MensajesWhatsApp
                WHERE TelefonoCliente = ? OR TelefonoCliente LIKE ?
                ORDER BY FechaHora ASC
            """, (telefono, f"%{telefono[-8:]}"))
            
            mensajes = []
            for row in cursor.fetchall():
                mensajes.append({
                    'direccion': row[0],
                    'contenido': row[1],
                    'fecha': row[2].strftime('%d/%m %H:%M') if row[2] else '',
                    'es_bot': bool(row[3])
                })
                
            return jsonify({'success': True, 'mensajes': mensajes})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Error de base de datos'}), 500

@atencion_bp.route('/whatsapp/toggle_bot', methods=['POST'])
def whatsapp_toggle_bot():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
    data = request.get_json(force=True, silent=True) or {}
    estado_solicitado = data.get('estado')
    
    cfg = get_whatsapp_config()
    if estado_solicitado is None:
        nuevo_estado = not cfg.get('bot_activo', True)
    else:
        nuevo_estado = bool(estado_solicitado)
        
    ok = set_bot_status(nuevo_estado)
    if ok:
        estado_txt = "ENCENDIDO" if nuevo_estado else "APAGADO"
        return jsonify({
            'success': True,
            'bot_activo': nuevo_estado,
            'mensaje': f"Bot de WhatsApp {estado_txt} correctamente."
        })
    return jsonify({'success': False, 'error': 'Error al actualizar estado del bot en la base de datos'}), 500

@atencion_bp.route('/whatsapp/guardar_config', methods=['POST'])
def whatsapp_guardar_config():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado. Tu sesión ha expirado.'}), 401
        
    data = request.get_json(force=True, silent=True) or {}
    telefono = data.get('telefono', '').strip()
    token = data.get('meta_access_token', '').strip()
    phone_id = data.get('meta_phone_number_id', '').strip()
    bienvenida = data.get('mensaje_bienvenida', '').strip()
    webhook_url = data.get('webhook_url', '').strip()
    
    if not telefono:
        return jsonify({'success': False, 'error': 'El número de teléfono es obligatorio.'}), 400
        
    ok = save_whatsapp_config(telefono, token, phone_id, bienvenida, webhook_url)
    if ok:
        return jsonify({
            'success': True, 
            'mensaje': '¡Configuración de WhatsApp guardada exitosamente!',
            'webhook_url': get_public_webhook_url()
        })
    return jsonify({'success': False, 'error': 'Error al guardar configuración en la base de datos.'}), 500

@atencion_bp.route('/whatsapp/probar_conexion', methods=['POST'])
def whatsapp_probar_conexion():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
    data = request.get_json(force=True, silent=True) or {}
    cfg = get_whatsapp_config()
    telefono = data.get('telefono') or cfg.get('telefono_numero', OFFICIAL_PHONE_NUMBER)
    
    mensaje_test = (
        "🔔 *Prueba de Conexión - Taller y Lubricantes CR*\n\n"
        "¡Excelente! Tu WhatsApp está conectado y listo para recibir y agendar citas de clientes.\n\n"
        "🏍️ *Sistema de Citas Inteligente Activo.*"
    )
    
    enviado, err_detalle = send_whatsapp_message_detailed(telefono, mensaje_test)
    if enviado:
        return jsonify({'success': True, 'enviado': True, 'mensaje': f'¡Mensaje real de prueba enviado exitosamente a {telefono}!'})
    else:
        return jsonify({
            'success': False, 
            'enviado': False, 
            'error': err_detalle or 'No se pudo enviar el mensaje a través de Meta API.'
        })

@atencion_bp.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    cfg = get_whatsapp_config()
    verify_token = cfg.get('verify_token', 'taller_cr_whatsapp_token_2026')
    
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        safe_print(f"[WEBHOOK GET RECIBIDO] mode={mode}, token={token}")
        if mode == 'subscribe' and token == verify_token:
            safe_print(f"[WEBHOOK VERIFICADO] Meta conectó exitosamente el webhook con challenge: {challenge}")
            return challenge, 200
        safe_print(f"[WEBHOOK ERROR] Verificación fallida. Token recibido: {token}")
        return jsonify({'status': 'Verification token mismatch'}), 403
        
    elif request.method == 'POST':
        try:
            data = request.get_json(force=True, silent=True) or {}
            safe_print(f"[WEBHOOK POST RECIBIDO]: {data}")
            
            # Registrar en archivo webhook_incoming.log para auditoría
            try:
                with open('webhook_incoming.log', 'a', encoding='utf-8') as lf:
                    lf.write(f"{datetime.datetime.now().isoformat()} - {data}\n")
            except Exception:
                pass
            
            if 'entry' in data:
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        val = change.get('value', {})
                        for msg in val.get('messages', []):
                            from_phone = msg.get('from')
                            text_body = ''
                            if msg.get('type') == 'text':
                                text_body = msg.get('text', {}).get('body', '')
                            elif msg.get('type') == 'interactive':
                                inter = msg.get('interactive', {})
                                if 'button_reply' in inter:
                                    text_body = inter['button_reply'].get('title', '')
                                elif 'list_reply' in inter:
                                    text_body = inter['list_reply'].get('title', '')
                            else:
                                text_body = msg.get('text', {}).get('body', '')
                                
                            if from_phone and text_body:
                                safe_print(f"[MENSAJE RECIBIDO DE {from_phone}]: {text_body}")
                                process_incoming_whatsapp_message(from_phone, text_body)
                                
            elif 'phone' in data and 'message' in data:
                process_incoming_whatsapp_message(data['phone'], data['message'])
                
            elif 'From' in request.form and 'Body' in request.form:
                from_phone = request.form.get('From', '').replace('whatsapp:', '')
                text_body = request.form.get('Body', '')
                process_incoming_whatsapp_message(from_phone, text_body)
                
            return jsonify({'status': 'success', 'message': 'Processed successfully'}), 200
        except Exception as e:
            safe_print(f"[ERROR WEBHOOK POST]: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@atencion_bp.route('/whatsapp/live_feed', methods=['GET'])
def whatsapp_live_feed():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de BD'}), 500
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cw.CitaID, cw.ClienteID, c.NombreCompleto, c.Telefono, 
               m.Marca, m.Modelo, cw.FechaProgramada, cw.TipoMantenimiento, 
               cw.Estado, cw.Notas, cw.FechaCreacion, cw.MotoID
        FROM CitasWhatsApp cw
        LEFT JOIN Clientes c ON cw.ClienteID = c.ClienteID
        LEFT JOIN Motocicletas m ON cw.MotoID = m.MotoID
        WHERE ISNULL(cw.Origen, 'WhatsApp') = 'WhatsApp'
        ORDER BY cw.FechaProgramada ASC
    """)
    citas_rows = cursor.fetchall()
    
    hoy_str = datetime.datetime.now().strftime('%Y-%m-%d')
    citas = []
    for r in citas_rows:
        fecha_prog_dt = r[6]
        fecha_prog_str = fecha_prog_dt.strftime('%Y-%m-%d %H:%M') if fecha_prog_dt else ''
        fecha_prog_iso = fecha_prog_dt.strftime('%Y-%m-%dT%H:%M') if fecha_prog_dt else ''
        tel_raw = r[3] or ''
        tel_clean = re.sub(r'\D', '', tel_raw)
        if len(tel_clean) == 8:
            tel_clean = '505' + tel_clean
        citas.append({
            'cita_id': r[0],
            'cliente_id': r[1],
            'cliente_nombre': r[2] or 'Cliente Desconocido',
            'telefono': tel_raw or 'Sin Teléfono',
            'telefono_clean': tel_clean,
            'moto_info': f"{r[4]} {r[5]}" if r[4] else "Sin Moto Registrada",
            'fecha_programada': fecha_prog_str,
            'fecha_prog_iso': fecha_prog_iso,
            'fecha_formateada': fecha_prog_dt.strftime('%d/%m/%Y %I:%M %p') if fecha_prog_dt else 'N/A',
            'tipo': r[7] or 'Preventivo',
            'estado': r[8] or 'Pendiente',
            'notas': r[9] or '',
            'fecha_creacion': r[10].strftime('%d/%m/%Y %H:%M') if r[10] else '',
            'moto_id': r[11]
        })
        
    stats = {
        'total': len(citas),
        'pendientes': sum(1 for c in citas if c['estado'] == 'Pendiente'),
        'confirmadas': sum(1 for c in citas if c['estado'] == 'Confirmada'),
        'hoy': sum(1 for c in citas if c['fecha_programada'].startswith(hoy_str))
    }
    
    cursor.execute("""
        SELECT TOP 30 MensajeID, TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, FechaHora, CitaID
        FROM MensajesWhatsApp
        ORDER BY MensajeID DESC
    """)
    msgs = []
    for m in cursor.fetchall():
        msgs.append({
            'mensaje_id': m[0],
            'telefono': m[1],
            'cliente_id': m[2],
            'direccion': m[3],
            'contenido': m[4],
            'es_bot': bool(m[5]),
            'fecha': m[6].strftime('%d/%m %H:%M') if m[6] else '',
            'cita_id': m[7]
        })

    cursor.execute("SELECT COUNT(*) FROM MensajesWhatsApp")
    total_mensajes_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT mw.TelefonoCliente, 
               COALESCE(c.NombreCompleto, mw.TelefonoCliente) as Nombre,
               MAX(mw.FechaHora) as UltimoMensajeFecha,
               (SELECT TOP 1 Contenido FROM MensajesWhatsApp WHERE TelefonoCliente = mw.TelefonoCliente ORDER BY FechaHora DESC) as UltimoContenido,
               (SELECT TOP 1 Direccion FROM MensajesWhatsApp WHERE TelefonoCliente = mw.TelefonoCliente ORDER BY FechaHora DESC) as UltimaDireccion,
               COUNT(*) as TotalMensajes
        FROM MensajesWhatsApp mw
        LEFT JOIN Clientes c ON mw.ClienteID = c.ClienteID
        GROUP BY mw.TelefonoCliente, c.NombreCompleto
        ORDER BY MAX(mw.FechaHora) DESC
    """)
    conversaciones_rows = cursor.fetchall()
    conversaciones = []
    for row in conversaciones_rows:
        dt = row[2]
        conversaciones.append({
            'telefono': row[0],
            'nombre': row[1] or row[0],
            'fecha': dt.strftime('%I:%M %p') if dt else '',
            'ultimo_mensaje': row[3] or '',
            'ultima_direccion': row[4] or '',
            'total_mensajes': row[5]
        })

    conn.close()
    
    cfg = get_whatsapp_config()
    
    return jsonify({
        'success': True,
        'stats': stats,
        'citas': citas,
        'mensajes': msgs,
        'total_mensajes': total_mensajes_count,
        'conversaciones': conversaciones,
        'bot_activo': cfg.get('bot_activo', True)
    })

@atencion_bp.route('/citas_whatsapp/escalar_ticket/<int:cita_id>', methods=['POST'])
def citas_whatsapp_escalar_ticket(cita_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cw.ClienteID, c.NombreCompleto, c.Telefono, cw.TipoMantenimiento, cw.FechaProgramada, cw.Notas
                FROM CitasWhatsApp cw
                LEFT JOIN Clientes c ON cw.ClienteID = c.ClienteID
                WHERE cw.CitaID = ?
            """, (cita_id,))
            cita = cursor.fetchone()
            if cita:
                nombre = cita[1] or 'Cliente WhatsApp'
                telefono = cita[2] or ''
                asunto = f"Cita WhatsApp #{cita_id} ({cita[3]})"
                fecha_str = cita[4].strftime('%d/%m/%Y %H:%M') if cita[4] else 'Por definir'
                mensaje = f"Cita de {cita[3]} programada para {fecha_str}. Solicitud: \"{cita[5] or ''}\". Derivada desde WhatsApp a Atención al Cliente para seguimiento."
                
                cursor.execute("""
                    INSERT INTO AtencionTickets (ClienteNombre, Telefono, Asunto, Mensaje, Estado, FechaCreacion)
                    VALUES (?, ?, ?, ?, 'Pendiente', GETDATE())
                """, (nombre, telefono, asunto, mensaje))
                conn.commit()
                flash(f"¡Éxito! Cita #{cita_id} derivada como Ticket a Atención al Cliente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al derivar caso: {e}", "error")
        finally:
            conn.close()
            
    return redirect(url_for('atencion.citas_whatsapp'))


@atencion_bp.route('/clientes', methods=['GET'])
def clientes_list():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.ClienteID, C.NombreCompleto, C.Telefono,
               (SELECT COUNT(F.FacturaID) 
                FROM Facturas F 
                WHERE F.ClienteID = C.ClienteID OR 
                      F.OrdenID IN (SELECT OrdenID FROM OrdenesTrabajo O JOIN Motocicletas M ON O.MotoID = M.MotoID WHERE M.ClienteID = C.ClienteID)
               ) AS Visitas,
               C.Identificacion
        FROM Clientes C 
        ORDER BY Visitas DESC, C.ClienteID DESC
    """)
    clientes = cursor.fetchall()
    
    # Mark top 5
    top_5_ids = [c[0] for c in clientes[:5]] if clientes else []
    
    conn.close()
    
    return render_template('atencion/clientes.html', clientes=clientes, top_5_ids=top_5_ids)

@atencion_bp.route('/clientes/add', methods=['POST'])
def clientes_add():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return redirect(url_for('auth.login'))
        
    identificacion = request.form.get('identificacion', '').strip().upper()
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    
    if not identificacion or not nombre or not telefono:
        flash('Todos los campos (Identificación, Nombre y Teléfono) son obligatorios.', 'error')
        return redirect(url_for('atencion.clientes_list'))
        
    if not telefono.isdigit():
        flash('El teléfono debe contener únicamente números.', 'error')
        return redirect(url_for('atencion.clientes_list'))
        
    if len(telefono) < 8 or len(telefono) > 15:
        flash('El número de teléfono debe tener entre 8 y 15 dígitos.', 'error')
        return redirect(url_for('atencion.clientes_list'))

    # Validación estricta de Nombre: no permitir números, solo letras y espacios
    if any(char.isdigit() for char in nombre):
        flash('El nombre completo no puede contener números. Ingrese un nombre válido.', 'error')
        return redirect(url_for('atencion.clientes_list'))

    if len(nombre) < 3 or len(nombre) > 80:
        flash('El nombre completo debe tener entre 3 y 80 caracteres.', 'error')
        return redirect(url_for('atencion.clientes_list'))

    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\.-]+$", nombre):
        flash('El nombre solo debe contener letras del alfabeto y espacios.', 'error')
        return redirect(url_for('atencion.clientes_list'))

    # Validación estricta de Identificación (Cédula de Nicaragua o DNI/Pasaporte)
    if identificacion.startswith('TEL-') or identificacion.startswith('TEMP-'):
        flash('Identificación inválida. Ingrese una Cédula válida (ej. 001-120590-0012A) o documento oficial.', 'error')
        return redirect(url_for('atencion.clientes_list'))

    clean_id = re.sub(r'[\s-]', '', identificacion)
    is_cedula_ni = bool(re.match(r'^\d{3}-?\d{6}-?\d{4}[A-Z]$', identificacion))
    is_doc_valido = bool(re.match(r'^[A-Z0-9-]{6,20}$', identificacion)) and len(clean_id) >= 6

    if not is_cedula_ni and not is_doc_valido:
        flash('Formato de identificación inválido. Ingrese una Cédula (001-120590-0012A) o documento oficial de 6 a 20 caracteres.', 'error')
        return redirect(url_for('atencion.clientes_list'))
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Validar si ya existe la identificación
            cursor.execute("SELECT COUNT(*) FROM Clientes WHERE UPPER(Identificacion) = ?", (identificacion,))
            if cursor.fetchone()[0] > 0:
                flash(f'La identificación "{identificacion}" ya se encuentra registrada para otro cliente.', 'error')
                return redirect(url_for('atencion.clientes_list'))
                
            # Validar si ya existe el teléfono
            cursor.execute("SELECT COUNT(*) FROM Clientes WHERE Telefono = ?", (telefono,))
            if cursor.fetchone()[0] > 0:
                flash(f'El número de teléfono "{telefono}" ya se encuentra registrado para otro cliente.', 'error')
                return redirect(url_for('atencion.clientes_list'))

            cursor.execute("INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email) VALUES (?, ?, ?, '')", (identificacion, nombre, telefono))
            conn.commit()
            flash('Cliente agregado exitosamente.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar cliente: {e}', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('atencion.clientes_list'))

@atencion_bp.route('/clientes/delete/<int:cliente_id>', methods=['POST'])
def clientes_delete(cliente_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # 1. Validar si tiene órdenes de trabajo activas o archivadas vinculadas a sus motocicletas o citas
            cursor.execute('''
                SELECT COUNT(*) 
                FROM OrdenesTrabajo ot 
                WHERE ot.MotoID IN (SELECT MotoID FROM Motocicletas WHERE ClienteID = ?)
                   OR ot.CitaID IN (SELECT CitaID FROM CitasWhatsApp WHERE ClienteID = ?)
            ''', (cliente_id, cliente_id))
            ordenes_count = cursor.fetchone()[0]
            if ordenes_count > 0:
                flash('No se puede eliminar el cliente porque tiene órdenes de trabajo activas o archivadas en el taller.', 'error')
                return redirect(url_for('atencion.clientes_list'))

            # 2. Validar si tiene facturas fiscales registradas en el sistema contable
            cursor.execute("SELECT COUNT(*) FROM Facturas WHERE ClienteID = ?", (cliente_id,))
            facturas_count = cursor.fetchone()[0]
            if facturas_count > 0:
                flash('No se puede eliminar el cliente porque tiene facturas fiscales registradas en el sistema contable.', 'error')
                return redirect(url_for('atencion.clientes_list'))

            # 3. Limpiar mensajes de WhatsApp
            cursor.execute('''
                DELETE FROM MensajesWhatsApp 
                WHERE ClienteID = ? 
                   OR CitaID IN (SELECT CitaID FROM CitasWhatsApp WHERE ClienteID = ?)
            ''', (cliente_id, cliente_id))

            # 4. Limpiar citas
            cursor.execute("DELETE FROM CitasWhatsApp WHERE ClienteID = ?", (cliente_id,))

            # 5. Limpiar ventas recibidas y rifas
            cursor.execute("DELETE FROM VentasRecibidas WHERE ClienteID = ?", (cliente_id,))
            cursor.execute("UPDATE RifaPremios SET GanadorClienteID = NULL WHERE GanadorClienteID = ?", (cliente_id,))

            # 6. Eliminar motocicletas del cliente (seguro porque se comprobó que no tienen órdenes de trabajo)
            cursor.execute("DELETE FROM Motocicletas WHERE ClienteID = ?", (cliente_id,))

            # 7. Eliminar el registro del cliente
            cursor.execute("DELETE FROM Clientes WHERE ClienteID = ?", (cliente_id,))
            conn.commit()
            flash('Cliente eliminado exitosamente.', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error al eliminar cliente: {e}', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('atencion.clientes_list'))

@atencion_bp.route('/gestion_citas', methods=['GET'])
def gestion_citas():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('atencion.index'))
        
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cw.CitaID, cw.ClienteID, c.NombreCompleto, c.Telefono, 
               m.Marca, m.Modelo, cw.FechaProgramada, cw.TipoMantenimiento, 
               cw.Estado, cw.MecanicoAsignadoID, cw.Origen, u.NombreCompleto as MecanicoNombre
        FROM CitasWhatsApp cw
        LEFT JOIN Clientes c ON cw.ClienteID = c.ClienteID
        LEFT JOIN Motocicletas m ON cw.MotoID = m.MotoID
        LEFT JOIN Usuarios u ON cw.MecanicoAsignadoID = u.UsuarioID
        WHERE cw.Estado = 'Pendiente' AND cw.MecanicoAsignadoID IS NULL
          AND NOT EXISTS (SELECT 1 FROM OrdenesTrabajo ot WHERE ot.CitaID = cw.CitaID)
        ORDER BY cw.FechaProgramada ASC
    """)
    citas = cursor.fetchall()
    
    cursor.execute("SELECT UsuarioID, NombreCompleto FROM Usuarios WHERE RolID = 3 AND Activo = 1")
    mecanicos = cursor.fetchall()

    # Mecánicos ya asignados en citas confirmadas/activas agrupados por horario
    cursor.execute("""
        SELECT CONVERT(VARCHAR(16), FechaProgramada, 120) as FechaHora, MecanicoAsignadoID
        FROM CitasWhatsApp
        WHERE MecanicoAsignadoID IS NOT NULL
          AND Estado NOT IN ('Cancelada', 'No Asistio')
    """)
    asignaciones = cursor.fetchall()
    mecanicos_ocupados = {}
    for row in asignaciones:
        fecha_str = row[0]
        mec_id = row[1]
        if fecha_str and mec_id:
            if fecha_str not in mecanicos_ocupados:
                mecanicos_ocupados[fecha_str] = []
            if mec_id not in mecanicos_ocupados[fecha_str]:
                mecanicos_ocupados[fecha_str].append(mec_id)
    
    # 3. Telemetría y estadísticas operativas del taller
    cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp WHERE CAST(FechaProgramada AS DATE) = CAST(GETDATE() AS DATE)")
    citas_hoy = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp WHERE Estado = 'Confirmada'")
    citas_confirmadas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE Estado IN ('Pendiente', 'En Proceso')")
    ordenes_activas = cursor.fetchone()[0]

    mecanicos_stats = {}
    for mec in mecanicos:
        mec_id = mec[0]
        cursor.execute("""
            SELECT COUNT(*) FROM CitasWhatsApp 
            WHERE MecanicoAsignadoID = ? AND Estado = 'Confirmada'
        """, (mec_id,))
        count_citas_mec = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM OrdenesTrabajo 
            WHERE MecanicoID = ? AND Estado IN ('Pendiente', 'En Proceso')
        """, (mec_id,))
        count_ot_mec = cursor.fetchone()[0]
        
        mecanicos_stats[mec_id] = {
            'citas_programadas': count_citas_mec,
            'ordenes_activas': count_ot_mec
        }

    telemetria = {
        'total_pendientes': len(citas),
        'total_mecanicos': len(mecanicos),
        'citas_hoy': citas_hoy,
        'citas_confirmadas': citas_confirmadas,
        'ordenes_activas': ordenes_activas
    }

    conn.close()
    
    return render_template('atencion/gestion_citas.html', 
                           citas=citas, 
                           mecanicos=mecanicos, 
                           mecanicos_ocupados=mecanicos_ocupados,
                           telemetria=telemetria,
                           mecanicos_stats=mecanicos_stats)

@atencion_bp.route('/asignar_cita', methods=['POST'])
def asignar_cita():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
    data = request.json or {}
    cita_id = data.get('cita_id')
    mecanico_id = data.get('mecanico_id')
    
    if not cita_id:
        return jsonify({'success': False, 'message': 'ID de cita requerido.'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if mecanico_id:
                # 1. Obtener la fecha y hora de la cita actual
                cursor.execute("""
                    SELECT FechaProgramada 
                    FROM CitasWhatsApp 
                    WHERE CitaID = ?
                """, (cita_id,))
                cita_info = cursor.fetchone()
                if not cita_info:
                    return jsonify({'success': False, 'message': 'La cita especificada no existe.'}), 404
                
                fecha_prog = cita_info[0]
                
                # 2. Verificar si este mecánico ya tiene asignada otra cita en la misma fecha y hora
                cursor.execute("""
                    SELECT cw.CitaID, u.NombreCompleto 
                    FROM CitasWhatsApp cw
                    JOIN Usuarios u ON u.UsuarioID = ?
                    WHERE cw.MecanicoAsignadoID = ?
                      AND CONVERT(VARCHAR(16), cw.FechaProgramada, 120) = CONVERT(VARCHAR(16), ?, 120)
                      AND cw.CitaID != ?
                      AND cw.Estado NOT IN ('Cancelada', 'No Asistio')
                """, (mecanico_id, mecanico_id, fecha_prog, cita_id))
                conflicto = cursor.fetchone()
                
                if conflicto:
                    nombre_mec = conflicto[1]
                    hora_txt = fecha_prog.strftime('%I:%M %p')
                    return jsonify({
                        'success': False,
                        'message': f'El mecánico {nombre_mec} ya tiene una cita asignada en este mismo horario ({hora_txt}). Por favor, selecciona al otro mecánico disponible.'
                    }), 400
                
                # 3. Asignar mecánico y confirmar
                cursor.execute("UPDATE CitasWhatsApp SET MecanicoAsignadoID = ?, Estado = 'Confirmada' WHERE CitaID = ?", (mecanico_id, cita_id))
            else:
                cursor.execute("UPDATE CitasWhatsApp SET MecanicoAsignadoID = NULL, Estado = 'Pendiente' WHERE CitaID = ?", (cita_id,))
                
            conn.commit()
            return jsonify({'success': True, 'message': 'Mecánico asignado y cita confirmada exitosamente.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500
        finally:
            conn.close()
            
    return jsonify({'success': False, 'message': 'Error de conexión con la base de datos.'}), 500

@atencion_bp.route('/eliminar_cita', methods=['POST'])
def eliminar_cita():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 5, 1008]:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
    data = request.json or {}
    cita_id = data.get('cita_id')
    
    if not cita_id:
        return jsonify({'success': False, 'message': 'ID de cita requerido.'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT CitaID, FechaProgramada FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
            cita = cursor.fetchone()
            if not cita:
                return jsonify({'success': False, 'message': 'La cita no existe o ya fue descartada.'}), 404
                
            # Verificar si ya tiene Orden de Trabajo
            cursor.execute("SELECT 1 FROM OrdenesTrabajo WHERE CitaID = ?", (cita_id,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'No se puede eliminar una cita que ya tiene una orden de trabajo iniciada.'}), 400
            
            # Intentar eliminación física o marcar como Cancelada
            try:
                cursor.execute("DELETE FROM CitasWhatsApp WHERE CitaID = ?", (cita_id,))
            except Exception:
                cursor.execute("UPDATE CitasWhatsApp SET Estado = 'Cancelada', MecanicoAsignadoID = NULL WHERE CitaID = ?", (cita_id,))
                
            conn.commit()
            return jsonify({'success': True, 'message': 'La cita ha sido descartada exitosamente.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500
        finally:
            conn.close()
            
    return jsonify({'success': False, 'message': 'Error de conexión con la base de datos.'}), 500

