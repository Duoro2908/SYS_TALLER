from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from database import get_db_connection
from datetime import datetime, timezone, timedelta, time
import re

NICARAGUA_TZ = timezone(timedelta(hours=-6))

auth_bp = Blueprint('auth', __name__)
autenticacion_bp = auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash("Error de conexión a la base de datos.", "error")
            return render_template('auth/login.html')
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.UsuarioID, u.NombreCompleto, u.PasswordHash, u.RolID, u.Activo, r.NombreRol 
            FROM Usuarios u
            LEFT JOIN Roles r ON u.RolID = r.RolID
            WHERE u.Email = ?
        """, (email,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            if not usuario.Activo:
                flash("Este usuario está desactivado.", "error")
            elif check_password_hash(usuario.PasswordHash, password):
                session['usuario_id'] = usuario.UsuarioID
                session['nombre_completo'] = usuario.NombreCompleto
                session['rol_id'] = usuario.RolID
                session['rol_nombre'] = usuario.NombreRol
                session['username'] = email
                return redirect(url_for('index'))
            else:
                flash("Contraseña incorrecta.", "error")
        else:
            flash('Contraseña incorrecta', 'error')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

TIPOS_SERVICIO_VALIDOS = ('Preventivo', 'General', 'Correctivo')
HORARIOS_TALLER_VALIDOS = (
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
    '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
)


def _render_agendar_cita_form(form_data=None):
    """Renderiza el formulario público de citas preservando los datos ingresados."""
    conn = get_db_connection()
    mantenimientos = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Tipo, DescripcionDetallada, PrecioBase FROM CatalogoMantenimientos WHERE PrecioBase > 0 ORDER BY PrecioBase ASC")
            mantenimientos = cursor.fetchall()
        finally:
            conn.close()
    now_nicaragua = datetime.now(NICARAGUA_TZ)
    return render_template(
        'auth/agendar_cita.html',
        mantenimientos=mantenimientos,
        server_today=now_nicaragua.strftime('%Y-%m-%d'),
        server_hour=now_nicaragua.strftime('%H:%M'),
        form_data=form_data or {}
    )


def _validar_datos_cita(form_data):
    """Valida estrictamente todos los campos del agendamiento de citas; retorna mensaje o None."""
    nombre = form_data['nombre']
    telefono = form_data['telefono']
    marca = form_data['marca']
    modelo = form_data['modelo']
    anio = form_data['anio']
    placa = form_data['placa']
    cilindraje = form_data['cilindraje']
    tipo_servicio = form_data['tipo_servicio']
    fecha = form_data['fecha']
    hora = form_data['hora']

    # 1. Nombre completo: solo letras/espacios, sin dígitos, nombre y apellido (>= 2 letras c/u)
    if not nombre:
        return "Por favor, ingresa tu nombre completo (nombre y apellido)."
    if any(ch.isdigit() for ch in nombre):
        return "En el nombre completo no se permiten números, únicamente letras y espacios."
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]{4,100}$", nombre):
        return "El nombre completo contiene caracteres no válidos. Usa únicamente letras y espacios."
    palabras_nombre = [p for p in nombre.split() if len(p) >= 2]
    if len(palabras_nombre) < 2:
        return "Ingresa tu nombre completo incluyendo nombre y apellido (mínimo 2 letras por palabra)."
    if len(set(nombre.replace(' ', '').lower())) < 3:
        return "Por favor, ingresa un nombre real y válido."

    # 2. Teléfono: solo dígitos (con + opcional al inicio), sin letras ni patrones falsos
    if not telefono:
        return "Por favor, ingresa tu número de teléfono de WhatsApp."
    if any(ch.isalpha() for ch in telefono):
        return "En el número de teléfono no se permiten letras, únicamente dígitos numéricos."
    clean_tel = re.sub(r'[\s\-]', '', telefono).lstrip('+')
    if not clean_tel.isdigit():
        return "El teléfono solo puede contener dígitos numéricos (ej. 88888888 o +50588888888)."
    if len(clean_tel) == 8:
        if clean_tel[0] not in ('2', '5', '7', '8'):
            return "El teléfono nacional de 8 dígitos debe iniciar con 2, 5, 7 u 8."
    elif not (10 <= len(clean_tel) <= 15):
        return "El teléfono debe tener 8 dígitos locales o entre 10 y 15 dígitos con código internacional."
    local_digits = clean_tel[-8:]
    if len(set(local_digits)) == 1 or local_digits in ('12345678', '87654321', '01234567'):
        return "El número de teléfono ingresado no parece válido. Verifica tu número real de contacto."

    # 3. Marca y Modelo
    if not marca or len(marca) < 2 or len(marca) > 50:
        return "Ingresa o selecciona una marca de motocicleta válida (mínimo 2 caracteres)."
    if marca.isdigit() or not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', marca):
        return "La marca de la motocicleta debe incluir letras válidas (ej. Genesis, Yamaha, Honda)."
    if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-&/]+$', marca):
        return "La marca contiene símbolos no permitidos."

    if not modelo or len(modelo) < 2 or len(modelo) > 50:
        return "Ingresa o selecciona el modelo de tu motocicleta (mínimo 2 caracteres)."
    if not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', modelo) or not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\./]+$', modelo):
        return "El modelo de la motocicleta contiene símbolos inválidos."

    # 4. Año numérico (4 dígitos reales)
    max_anio = datetime.now(NICARAGUA_TZ).year + 1
    if not anio or not anio.isdigit() or len(anio) != 4 or not (1980 <= int(anio) <= max_anio):
        return f"Ingresa un año numérico válido de 4 dígitos entre 1980 y {max_anio} (ej. 2023)."

    # 5. Placa Nicaragua: alfanumérica estricta (4 a 12 caracteres, combinando letras y números)
    if not placa:
        return "Por favor, ingresa el número de placa de tu motocicleta."
    if not re.match(r'^[A-Z0-9]{4,12}$', placa):
        return "La placa solo permite entre 4 y 12 letras y números (sin espacios, guiones ni símbolos; ej. M123456)."
    if not (re.search(r'[A-Z]', placa) and re.search(r'[0-9]', placa)):
        return "La placa debe combinar letras y números reales (ej. M123456 o MY45820)."

    # 6. Cilindraje obligatorio entre 49 cc y máximo 400 cc
    if not cilindraje or not cilindraje.isdigit():
        return "El cilindraje (CC) es obligatorio y debe contener solo números (ej. 150, 200, 250)."
    cil_int = int(cilindraje)
    if not (49 <= cil_int <= 400):
        return "El cilindraje permitido es entre 49 cc y máximo 400 cc."

    # 7. Paquete de mantenimiento válido
    if tipo_servicio not in TIPOS_SERVICIO_VALIDOS:
        return "Debes seleccionar un paquete de mantenimiento válido (Preventivo, General o Correctivo)."

    # 8. Fecha estrictamente a partir del día siguiente (Nicaragua UTC-6) y no domingo
    now_nicaragua = datetime.now(NICARAGUA_TZ)
    today_nicaragua = now_nicaragua.date()
    max_fecha = today_nicaragua + timedelta(days=90)

    if not fecha:
        return "Por favor, selecciona la fecha para tu cita a partir de mañana."
    try:
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return "El formato de la fecha seleccionada no es válido."

    if fecha_dt < today_nicaragua:
        return "No se pueden agendar citas en fechas pasadas. Selecciona una fecha a partir de mañana."
    if fecha_dt == today_nicaragua:
        hoy_fmt = today_nicaragua.strftime('%d/%m/%Y')
        return f"No se pueden agendar citas para hoy ({hoy_fmt}). Las citas deben programarse a partir del día siguiente."
    if fecha_dt.weekday() == 6:
        return "El taller permanece cerrado los domingos. Por favor, selecciona un día de lunes a sábado a partir de mañana."
    if fecha_dt > max_fecha:
        return "Solo puedes agendar citas con un máximo de 90 días de anticipación."

    # 9. Hora válida dentro del horario del taller
    if not hora or hora not in HORARIOS_TALLER_VALIDOS:
        return "Selecciona una hora de ingreso válida dentro del horario de atención (08:00 AM a 05:00 PM)."

    return None


@auth_bp.route('/agendar_cita', methods=['GET', 'POST'])
def agendar_cita():
    from database import ensure_schema_migrations
    ensure_schema_migrations()

    if request.method == 'POST':
        form_data = {
            'nombre': re.sub(r'\s+', ' ', (request.form.get('nombre') or '').strip()),
            'telefono': (request.form.get('telefono') or '').strip(),
            'marca': re.sub(r'\s+', ' ', (request.form.get('marca') or '').strip()),
            'modelo': re.sub(r'\s+', ' ', (request.form.get('modelo') or '').strip()),
            'anio': (request.form.get('anio') or '').strip(),
            'placa': (request.form.get('placa') or '').strip().upper(),
            'cilindraje': (request.form.get('cilindraje') or '').strip(),
            'tipo_servicio': (request.form.get('tipo_servicio') or '').strip(),
            'fecha': (request.form.get('fecha') or '').strip(),
            'hora': (request.form.get('hora') or '').strip()
        }

        err_msg = _validar_datos_cita(form_data)
        if err_msg:
            flash(err_msg, "error")
            return _render_agendar_cita_form(form_data)

        nombre = form_data['nombre']
        tel_compact = re.sub(r'[\s\-]', '', form_data['telefono'])
        telefono_local = tel_compact.lstrip('+')
        if len(telefono_local) == 11 and telefono_local.startswith('505'):
            telefono_local = telefono_local[3:]
        telefono_guardar = telefono_local
        marca = form_data['marca']
        modelo = form_data['modelo']
        anio = int(form_data['anio'])
        placa = form_data['placa']
        cilindraje = int(form_data['cilindraje'])
        tipo_servicio = form_data['tipo_servicio']
        fecha = form_data['fecha']
        hora = form_data['hora']

        conn = get_db_connection()
        if not conn:
            flash("Error de conexión con la base de datos del taller. Intenta nuevamente en unos segundos.", "error")
            return _render_agendar_cita_form(form_data)

        cursor = conn.cursor()

        try:
            # 1. Máximo 20 citas diarias
            cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp WHERE CAST(FechaProgramada AS DATE) = ? AND Estado != 'Cancelada'", (fecha,))
            total_citas = cursor.fetchone()[0]
            if total_citas >= 20:
                flash("Lo sentimos, ya no hay cupos disponibles para este día (límite de 20 citas alcanzado). Selecciona otro día.", "error")
                return _render_agendar_cita_form(form_data)

            # 2. Buscar o crear cliente comparando dígitos finales de teléfono
            tel_8 = telefono_local[-8:]
            cursor.execute("""
                SELECT ClienteID, NombreCompleto
                FROM Clientes
                WHERE Telefono = ?
                   OR RIGHT(REPLACE(REPLACE(REPLACE(Telefono, ' ', ''), '-', ''), '+', ''), 8) = ?
            """, (form_data['telefono'], tel_8))
            cliente = cursor.fetchone()
            if cliente:
                cliente_id = cliente[0]
                nombre_db = (cliente[1] or '').strip()
                if nombre_db and nombre.lower() not in nombre_db.lower() and nombre_db.lower() not in nombre.lower():
                    flash("El teléfono ingresado ya está registrado a nombre de otro cliente. Verifica el número o usa el directorio de arriba.", "error")
                    return _render_agendar_cita_form(form_data)
            else:
                identificacion = f"TEL-{telefono_guardar}"
                cursor.execute(
                    "INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono) OUTPUT INSERTED.ClienteID VALUES (?, ?, ?)",
                    (identificacion, nombre, telefono_guardar)
                )
                cliente_id = cursor.fetchone()[0]

            # 3. Buscar o registrar motocicleta por placa normalizada
            cursor.execute("""
                SELECT MotoID, ClienteID
                FROM Motocicletas
                WHERE REPLACE(REPLACE(UPPER(Placa), ' ', ''), '-', '') = ?
            """, (placa,))
            moto = cursor.fetchone()
            if moto:
                moto_id = moto[0]
                if moto[1] != cliente_id:
                    flash(f"La placa {placa} ya se encuentra registrada con otro cliente y número de teléfono.", "error")
                    return _render_agendar_cita_form(form_data)
            else:
                cursor.execute("IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CHK_Moto_Marca') ALTER TABLE Motocicletas DROP CONSTRAINT CHK_Moto_Marca;")
                cursor.execute(
                    "INSERT INTO Motocicletas (ClienteID, Marca, Modelo, Anio, Placa, Cilindraje) OUTPUT INSERTED.MotoID VALUES (?, ?, ?, ?, ?, ?)",
                    (cliente_id, marca, modelo, anio, placa, cilindraje)
                )
                moto_id = cursor.fetchone()[0]

            # 4. Capacidad horaria: máximo 2 mecánicos en el mismo bloque
            fecha_hora_str = f"{fecha}T{hora}:00"
            cursor.execute("""
                SELECT COUNT(*) FROM CitasWhatsApp
                WHERE FechaProgramada = ? AND Estado != 'Cancelada'
            """, (fecha_hora_str,))
            citas_simultaneas = cursor.fetchone()[0]
            if citas_simultaneas >= 2:
                flash(f"Capacidad completa para las {hora}: nuestros 2 mecánicos certificados ya tienen servicio asignado en ese horario. Selecciona otra hora.", "error")
                return _render_agendar_cita_form(form_data)

            # 5. Guardar cita Web (separada de Citas WhatsApp)
            cursor.execute("""
                INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Origen)
                VALUES (?, ?, ?, ?, 'Pendiente', 'Web')
            """, (cliente_id, moto_id, fecha_hora_str, tipo_servicio))

            conn.commit()
            flash("Tu cita de taller ha sido agendada con éxito. Nuestro equipo y bahía técnica te esperan en la fecha y hora reservadas.", "success")
            return redirect(url_for('auth.agendar_cita'))

        except Exception as e:
            conn.rollback()
            err_lower = str(e).lower()
            print(f"[agendar_cita] Error SQL/Proceso: {e}")
            if 'placa' in err_lower or 'unique' in err_lower:
                flash(f"La placa {placa} o identificación ingresada ya existe en el sistema con otro registro.", "error")
            elif 'chk_moto_cilindraje' in err_lower:
                flash("El cilindraje de la motocicleta debe estar entre 49 cc y 400 cc.", "error")
            elif 'tipomantenimiento' in err_lower:
                flash("El paquete de mantenimiento seleccionado no es válido.", "error")
            else:
                flash("No pudimos completar tu registro por una inconsistencia en los datos enviados. Verifica tu placa, teléfono y fecha e inténtalo de nuevo.", "error")
            return _render_agendar_cita_form(form_data)
        finally:
            conn.close()

    return _render_agendar_cita_form()

@auth_bp.route('/api/search_client')
def search_client():
    query = request.args.get('q', '')
    conn = get_db_connection()
    if not conn:
        return jsonify([])
        
    cursor = conn.cursor()
    if query:
        cursor.execute("""
            SELECT c.ClienteID, c.NombreCompleto, c.Telefono, 
                   m.Marca, m.Modelo, m.Anio, m.Placa, m.Cilindraje
            FROM Clientes c
            LEFT JOIN Motocicletas m ON c.ClienteID = m.ClienteID
            WHERE c.NombreCompleto NOT LIKE 'Cliente WA%'
              AND (c.Telefono LIKE ? OR c.NombreCompleto LIKE ? OR m.Placa LIKE ?)
            ORDER BY c.NombreCompleto ASC
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("""
            SELECT c.ClienteID, c.NombreCompleto, c.Telefono, 
                   m.Marca, m.Modelo, m.Anio, m.Placa, m.Cilindraje
            FROM Clientes c
            LEFT JOIN Motocicletas m ON c.ClienteID = m.ClienteID
            WHERE c.NombreCompleto NOT LIKE 'Cliente WA%'
            ORDER BY c.NombreCompleto ASC
        """)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'nombre': row[1] or '',
            'telefono': row[2] or '',
            'marca': row[3] or '',
            'modelo': row[4] or '',
            'anio': row[5] or '',
            'placa': row[6] or '',
            'cilindraje': row[7] or ''
        })
    conn.close()
    return jsonify(results)

@auth_bp.route('/enviar_queja', methods=['POST'])
def enviar_queja():
    nombre = request.form.get('nombre', 'Anónimo')
    telefono = request.form.get('telefono', 'N/A')
    asunto = request.form.get('asunto', 'Sugerencia/Queja')
    mensaje = request.form.get('mensaje')
    
    if not mensaje:
        return jsonify({'status': 'error', 'message': 'El mensaje es obligatorio.'})
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Asegurar que la tabla existe si no se ha corrido el script setup_atencion_db.py
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AtencionTickets' and xtype='U')
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
            cursor.execute("""
                INSERT INTO AtencionTickets (ClienteNombre, Telefono, Asunto, Mensaje, Estado)
                VALUES (?, ?, ?, ?, 'Pendiente')
            """, (nombre, telefono, asunto, mensaje))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Su mensaje ha sido enviado exitosamente a Atención al Cliente. Gracias por ayudarnos a mejorar.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Ocurrió un error al enviar el mensaje: {e}"})
        finally:
            conn.close()
            
    return jsonify({'status': 'error', 'message': 'Error de conexión.'})

@auth_bp.route('/api/horarios_disponibles')
def horarios_disponibles():
    fecha = request.args.get('fecha')
    if not fecha:
        return jsonify({})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({})
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT FechaProgramada
            FROM CitasWhatsApp
            WHERE CAST(FechaProgramada AS DATE) = ? AND Estado != 'Cancelada'
        """, (fecha,))
        rows = cursor.fetchall()
        
        ocupacion = {}
        for r in rows:
            fp = r[0]
            if hasattr(fp, 'strftime'):
                h_str = fp.strftime('%H:%M')
            else:
                s = str(fp).replace('T', ' ')
                parts = s.split(' ')
                h_str = parts[1][:5] if len(parts) > 1 else ''
            if h_str:
                ocupacion[h_str] = ocupacion.get(h_str, 0) + 1
        
        # Calcular fecha y hora actual en zona horaria de Managua, Nicaragua (UTC-6)
        now_nicaragua = datetime.now(NICARAGUA_TZ)
        today_str = now_nicaragua.strftime('%Y-%m-%d')
        now_time_str = now_nicaragua.strftime('%H:%M')
        
        es_hoy = (fecha == today_str)
        es_pasado = (fecha < today_str)
        es_hoy_o_pasado = (fecha <= today_str)

        response_data = {
            'ocupacion': ocupacion,
            'fecha_hoy': today_str,
            'hora_actual': now_time_str,
            'es_hoy': es_hoy,
            'es_pasado': es_pasado,
            'es_hoy_o_pasado': es_hoy_o_pasado
        }
        # Incluir ocupación a nivel raíz para compatibilidad con código existente
        response_data.update(ocupacion)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()


def _normalizar_tel_wa(tel_raw):
    digits = re.sub(r'\D', '', (tel_raw or '').strip())
    if digits.startswith('505') and len(digits) == 11:
        digits = digits[3:]
    return digits


@auth_bp.route('/api/public/whatsapp_chat', methods=['GET', 'POST'])
def public_whatsapp_chat():
    """Asistente WhatsApp en vivo dentro del sistema (conecta Login con MensajesWhatsApp y CitasWhatsApp)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar con la base de datos.'}), 500

    try:
        cursor = conn.cursor()

        if request.method == 'GET':
            tel = _normalizar_tel_wa(request.args.get('telefono', ''))
            if not re.match(r'^[2578]\d{7}$', tel):
                return jsonify({'status': 'error', 'message': 'Ingresa un teléfono de Nicaragua válido (8 dígitos).'}), 400
            cursor.execute("""
                SELECT TOP 25 Direccion, Contenido, FechaHora, EsAutoRespuesta
                FROM MensajesWhatsApp
                WHERE TelefonoCliente = ? OR TelefonoCliente LIKE ?
                ORDER BY MensajeID ASC
            """, (tel, f"%{tel}"))
            mensajes = []
            for r in cursor.fetchall():
                mensajes.append({
                    'direccion': r[0] or 'Entrante',
                    'contenido': r[1] or '',
                    'fecha': r[2].strftime('%d/%m %H:%M') if r[2] else '',
                    'es_bot': bool(r[3]),
                })
            return jsonify({'status': 'success', 'telefono': tel, 'mensajes': mensajes})

        data = request.get_json(force=True, silent=True) or {}
        tel = _normalizar_tel_wa(data.get('telefono', ''))
        if not re.match(r'^[2578]\d{7}$', tel):
            return jsonify({'status': 'error', 'message': 'Ingresa tu número de WhatsApp válido de Nicaragua (8 dígitos iniciando en 2, 5, 7 u 8).'}), 400

        nombre = ' '.join((data.get('nombre') or '').split())
        modo = (data.get('modo') or 'mensaje').strip().lower()
        mensaje = ' '.join((data.get('mensaje') or '').split())
        tel_fmt = f"+505 {tel}"

        cursor.execute("SELECT TOP 1 ClienteID, NombreCompleto FROM Clientes WHERE Telefono LIKE ? OR Telefono = ?", (f"%{tel}", tel))
        cli_row = cursor.fetchone()
        cliente_id = cli_row[0] if cli_row else None
        cliente_nombre = cli_row[1] if cli_row else (nombre or f"Cliente {tel}")

        respuesta_bot = ''
        cita_id_creada = None

        if modo == 'cita':
            moto_modelo = ' '.join((data.get('moto_modelo') or '').split())
            tipo_servicio = (data.get('tipo_servicio') or 'Preventivo').strip()
            fecha_str = (data.get('fecha') or '').strip()
            hora_str = (data.get('hora') or '').strip()

            if len(nombre) < 5 or len([w for w in nombre.split(' ') if w]) < 2 or any(ch.isdigit() for ch in nombre):
                return jsonify({'status': 'error', 'message': 'Ingresa tu nombre completo válido (nombre y apellido, sin números).'}), 400
            if len(moto_modelo) < 2 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{2,}', moto_modelo):
                return jsonify({'status': 'error', 'message': 'Especifica el modelo de tu motocicleta (Ej: Genesis KA 150).'}), 400
            if tipo_servicio not in TIPOS_SERVICIO_VALIDOS:
                tipo_servicio = 'Preventivo'
            if hora_str not in HORARIOS_TALLER_VALIDOS:
                return jsonify({'status': 'error', 'message': 'Selecciona un horario de taller válido (08:00 a 17:00).'}), 400

            try:
                fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Fecha de cita inválida (YYYY-MM-DD).'}), 400

            hoy_ni = datetime.now(NICARAGUA_TZ).date()
            if fecha_dt <= hoy_ni:
                return jsonify({'status': 'error', 'message': 'Las citas por asistente deben agendarse a partir de mañana.'}), 400
            if fecha_dt.weekday() == 6:
                return jsonify({'status': 'error', 'message': 'El taller permanece cerrado los domingos. Elige de Lunes a Sábado.'}), 400

            if not cliente_id:
                ident = f"TEL-{tel}"
                cursor.execute("SELECT TOP 1 ClienteID FROM Clientes WHERE Identificacion = ?", (ident,))
                ex = cursor.fetchone()
                if ex:
                    cliente_id = ex[0]
                else:
                    cursor.execute("""
                        INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email, CitasNoAsistidas)
                        OUTPUT INSERTED.ClienteID
                        VALUES (?, ?, ?, '', 0)
                    """, (ident, nombre, tel))
                    cliente_id = int(cursor.fetchone()[0])

            cursor.execute("SELECT TOP 1 MotoID FROM Motocicletas WHERE ClienteID = ?", (cliente_id,))
            m_row = cursor.fetchone()
            if m_row:
                moto_id = m_row[0]
            else:
                import random
                placa_temp = f"M{random.randint(100000, 999999)}"
                cursor.execute("IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CHK_Moto_Marca') ALTER TABLE Motocicletas DROP CONSTRAINT CHK_Moto_Marca;")
                cursor.execute("""
                    INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje)
                    OUTPUT INSERTED.MotoID
                    VALUES (?, ?, 'Genesis', ?, ?, 150)
                """, (cliente_id, placa_temp, moto_modelo[:50], hoy_ni.year))
                moto_id = int(cursor.fetchone()[0])

            h_int, m_int = [int(p) for p in hora_str.split(':')[:2]]
            fecha_prog_dt = datetime.combine(fecha_dt, time(h_int, m_int))
            notas_cita = f"Solicitud desde Asistente WhatsApp en Login • Moto: {moto_modelo}"
            cursor.execute("""
                INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Notas, Origen, FechaCreacion)
                OUTPUT INSERTED.CitaID
                VALUES (?, ?, ?, ?, 'Pendiente', ?, 'WhatsApp', GETDATE())
            """, (cliente_id, moto_id, fecha_prog_dt, tipo_servicio, notas_cita))
            cita_id_creada = int(cursor.fetchone()[0])

            msg_entrante = f"[Solicitud de Cita] {nombre} • Moto: {moto_modelo} • {tipo_servicio} • {fecha_str} {hora_str}"
            cursor.execute("""
                INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID, FechaHora)
                VALUES (?, ?, 'Entrante', ?, 0, ?, GETDATE())
            """, (tel, cliente_id, msg_entrante, cita_id_creada))

            respuesta_bot = (
                f"Cita #{cita_id_creada} registrada en Atención al Cliente para {nombre} "
                f"({moto_modelo}) el {fecha_dt.strftime('%d/%m/%Y')} a las {hora_str} ({tipo_servicio}). "
                f"Nuestro equipo confirmará tu espacio desde este mismo chat."
            )
            cursor.execute("""
                INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID, FechaHora)
                VALUES (?, ?, 'Saliente', ?, 1, ?, GETDATE())
            """, (tel, cliente_id, respuesta_bot, cita_id_creada))
            conn.commit()
            return jsonify({'status': 'success', 'cita_id': cita_id_creada, 'respuesta': respuesta_bot, 'telefono': tel})

        if not mensaje:
            mensaje = 'Consultar estado de mi cita / motocicleta' if modo == 'estado' else 'Hola, necesito información del taller.'

        cursor.execute("""
            INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, FechaHora)
            VALUES (?, ?, 'Entrante', ?, 0, GETDATE())
        """, (tel, cliente_id, mensaje))

        low = mensaje.lower()
        if modo == 'estado' or any(k in low for k in ('estado', 'cita', 'orden', 'moto', 'lista', 'repar')):
            partes = []
            cursor.execute("""
                SELECT TOP 2 cw.CitaID, cw.FechaProgramada, cw.TipoMantenimiento, cw.Estado
                FROM CitasWhatsApp cw
                JOIN Clientes c ON cw.ClienteID = c.ClienteID
                WHERE c.Telefono LIKE ?
                ORDER BY cw.CitaID DESC
            """, (f"%{tel}",))
            c_rows = cursor.fetchall()
            for cr in c_rows:
                fstr = cr[1].strftime('%d/%m/%Y %H:%M') if hasattr(cr[1], 'strftime') else str(cr[1])
                partes.append(f"Cita #{cr[0]} ({cr[2]}) para {fstr} -> Estado: {cr[3]}")

            cursor.execute("""
                SELECT TOP 2 ot.OrdenID, m.Marca, m.Modelo, ot.Estado
                FROM OrdenesTrabajo ot
                JOIN Motocicletas m ON ot.MotoID = m.MotoID
                JOIN Clientes c ON m.ClienteID = c.ClienteID
                WHERE c.Telefono LIKE ?
                ORDER BY ot.OrdenID DESC
            """, (f"%{tel}",))
            o_rows = cursor.fetchall()
            for orow in o_rows:
                partes.append(f"Orden #{orow[0]} ({orow[1]} {orow[2]}) -> {orow[3]}")

            if partes:
                respuesta_bot = f"Hola {cliente_nombre}, estado actualizado en Taller CR: " + " | ".join(partes)
            else:
                respuesta_bot = (
                    f"No encontramos citas u órdenes activas asociadas al {tel_fmt}. "
                    "Puedes usar 'Solicitar Cita por Chat' aquí mismo para agendar al instante."
                )
        elif any(k in low for k in ('precio', 'costo', 'mantenimiento', 'aceite', 'servicio')):
            cursor.execute("SELECT TOP 4 Tipo, PrecioBase FROM CatalogoMantenimientos WHERE PrecioBase > 0 ORDER BY PrecioBase ASC")
            cat_rows = cursor.fetchall()
            if cat_rows:
                resumen_p = ", ".join(f"{r[0]} desde C$ {float(r[1]):,.2f}" for r in cat_rows)
                respuesta_bot = f"Tarifas oficiales en Taller CR: {resumen_p}. Tu consulta ya llegó a nuestra bandeja de WhatsApp."
            else:
                respuesta_bot = "Ofrecemos Mantenimiento Preventivo, General y Correctivo. Un asesor te responderá por aquí."
        elif any(k in low for k in ('horario', 'ubicacion', 'hora', 'abierto', 'direccion')):
            respuesta_bot = "Atendemos de Lunes a Sábado de 8:00 AM a 5:00 PM (Domingos cerrado) • Canal Virtual Taller CR. Puedes trazar tu ruta GPS desde la tarjeta 'Ubicación del Taller'."
        else:
            respuesta_bot = (
                f"¡Mensaje recibido, {cliente_nombre}! Tu consulta ({mensaje[:80]}) quedó registrada en nuestra bandeja interna "
                f"de Atención al Cliente. Un asesor te responderá aquí mismo en breve."
            )

        cursor.execute("""
            INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, FechaHora)
            VALUES (?, ?, 'Saliente', ?, 1, GETDATE())
        """, (tel, cliente_id, respuesta_bot))
        conn.commit()
        return jsonify({'status': 'success', 'respuesta': respuesta_bot, 'telefono': tel})
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        print(f"[public_whatsapp_chat ERROR]: {e}")
        return jsonify({'status': 'error', 'message': f'Error al procesar: {e}'}), 500
    finally:
        conn.close()
