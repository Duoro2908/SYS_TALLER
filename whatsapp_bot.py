import re
import datetime
import requests
import os
from database import get_db_connection

OFFICIAL_PHONE_NUMBER = "Canal Virtual Taller CR"

def get_whatsapp_config():
    """
    Obtiene la configuración actual de WhatsApp desde la base de datos (ConfiguracionWhatsApp).
    Si no existe o falla la BD, retorna valores por defecto.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 BotActivo, TelefonoNumero, MetaAccessToken, MetaPhoneNumberID, VerifyToken, MensajeBienvenida, WebhookUrl
                FROM ConfiguracionWhatsApp
                ORDER BY ConfigID DESC
            """)
            row = cursor.fetchone()
            if row:
                return {
                    'bot_activo': bool(row[0]),
                    'telefono_numero': row[1] or OFFICIAL_PHONE_NUMBER,
                    'meta_access_token': row[2] or os.environ.get('META_ACCESS_TOKEN', ''),
                    'meta_phone_number_id': row[3] or os.environ.get('META_PHONE_NUMBER_ID', ''),
                    'verify_token': row[4] or 'taller_cr_whatsapp_token_2026',
                    'mensaje_bienvenida': row[5] or '¡Hola! Bienvenido a Taller y Lubricantes CR. ¿En qué podemos ayudarte?',
                    'webhook_url': row[6] or ''
                }
        except Exception as e:
            print(f"Error al obtener configuración de WhatsApp: {e}")
        finally:
            conn.close()
            
    return {
        'bot_activo': True,
        'telefono_numero': OFFICIAL_PHONE_NUMBER,
        'meta_access_token': os.environ.get('META_ACCESS_TOKEN', ''),
        'meta_phone_number_id': os.environ.get('META_PHONE_NUMBER_ID', ''),
        'verify_token': 'taller_cr_whatsapp_token_2026',
        'mensaje_bienvenida': '¡Hola! Bienvenido a Taller y Lubricantes CR.',
        'webhook_url': ''
    }

def set_bot_status(nuevo_estado: bool):
    """
    Enciende o apaga el bot de WhatsApp en la base de datos.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE ConfiguracionWhatsApp SET BotActivo = ?, FechaActualizacion = GETDATE()", (1 if nuevo_estado else 0,))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO ConfiguracionWhatsApp (BotActivo) VALUES (?)", (1 if nuevo_estado else 0,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar estado del bot: {e}")
        return False
    finally:
        conn.close()

def save_whatsapp_config(telefono, token=None, phone_id=None, bienvenida=None, webhook_url=None):
    """
    Guarda o actualiza las credenciales, teléfono y URL de Webhook de WhatsApp de forma segura.
    Si token, phone_id o webhook_url vienen vacíos, preserva los valores existentes para evitar pérdida de credenciales.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MetaAccessToken, MetaPhoneNumberID, TelefonoNumero, MensajeBienvenida, WebhookUrl FROM ConfiguracionWhatsApp")
        row = cursor.fetchone()
        
        existing_token = row[0] if row else ''
        existing_phone_id = row[1] if row else ''
        existing_tel = row[2] if row else ''
        existing_bienvenida = row[3] if row else ''
        existing_webhook = row[4] if (row and len(row) > 4) else ''
        
        final_tel = telefono.strip() if (telefono and telefono.strip()) else existing_tel
        final_token = token.strip() if (token and token.strip()) else existing_token
        final_phone_id = phone_id.strip() if (phone_id and phone_id.strip()) else existing_phone_id
        final_bienvenida = bienvenida.strip() if (bienvenida is not None and bienvenida.strip()) else existing_bienvenida
        final_webhook = webhook_url.strip() if (webhook_url is not None and webhook_url.strip()) else existing_webhook
        
        cursor.execute("""
            UPDATE ConfiguracionWhatsApp
            SET TelefonoNumero = ?,
                MetaAccessToken = ?,
                MetaPhoneNumberID = ?,
                MensajeBienvenida = ?,
                WebhookUrl = ?,
                FechaActualizacion = GETDATE()
        """, (final_tel, final_token, final_phone_id, final_bienvenida, final_webhook))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO ConfiguracionWhatsApp (TelefonoNumero, MetaAccessToken, MetaPhoneNumberID, MensajeBienvenida, WebhookUrl)
                VALUES (?, ?, ?, ?, ?)
            """, (final_tel, final_token, final_phone_id, final_bienvenida, final_webhook))
            
        conn.commit()
        safe_print(f"[WHATSAPP CONFIG] Configuración guardada correctamente en BD (Tel: {final_tel}, PhoneID: {final_phone_id}, Webhook: {final_webhook})")
        return True
    except Exception as e:
        conn.rollback()
        safe_print(f"[ERROR] Error al guardar configuración de WhatsApp: {e}")
        return False
    finally:
        conn.close()

def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            pass

def send_whatsapp_message_detailed(to_phone, message_text):
    """
    Envía un mensaje de texto real a través de la API Oficial de Meta WhatsApp Cloud.
    Retorna una tupla: (exito: bool, detalle: str)
    """
    cfg = get_whatsapp_config()
    token = cfg.get('meta_access_token')
    phone_id = cfg.get('meta_phone_number_id')
    
    # Limpiar el número de teléfono (quitar el + si lo tiene para la API de WhatsApp)
    to_phone_clean = re.sub(r'\D', '', str(to_phone))
    
    if not token or token == 'AQUI_TU_TOKEN_DE_META' or not phone_id or phone_id == 'AQUI_TU_PHONE_NUMBER_ID':
        err = f"Credenciales de Meta no configuradas para envío automático a {to_phone_clean}."
        safe_print(f"[WHATSAPP OFICIAL] {err}")
        return False, err
        
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone_clean,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        res_json = {}
        try:
            res_json = response.json()
        except Exception:
            pass

        if response.status_code == 200:
            safe_print(f"[OK] Mensaje de WhatsApp enviado exitosamente a {to_phone_clean}")
            return True, f"Mensaje entregado con éxito a {to_phone_clean}"
        else:
            err_obj = res_json.get('error', {})
            err_msg = err_obj.get('message', response.text)
            err_code = err_obj.get('code')
            safe_print(f"[ERROR META {response.status_code}]: Code {err_code} - {err_msg}")
            
            if err_code == 190 or 'expired' in err_msg.lower():
                user_msg = "El Token de Meta ha expirado (error 190). Por favor genera un nuevo token en Meta Developers (WhatsApp > Primeros pasos) y guárdalo."
            elif 'recipient' in err_msg.lower() or err_code == 131030:
                user_msg = f"El número {to_phone_clean} no está en la lista de destinatarios autorizados en Meta Developers Sandbox."
            else:
                user_msg = f"Error de Meta API ({response.status_code}): {err_msg}"
                
            return False, user_msg
    except requests.exceptions.RequestException as e:
        safe_print(f"[ERROR] Error de conexión enviando WhatsApp a {to_phone_clean}: {e}")
        return False, f"Error de conexión de red: {str(e)}"

def send_whatsapp_message(to_phone, message_text):
    """
    Función de compatibilidad: retorna True si se envió o False si falló.
    """
    ok, _ = send_whatsapp_message_detailed(to_phone, message_text)
    return ok

def es_mensaje_de_taller(mensaje_texto):
    """
    Determina si un mensaje entrante tiene relación con servicios de taller,
    citas, motos, reparaciones o mantenimiento.
    Si no tiene que ver con el taller, retorna False ('no le pone mente' a crear cita).
    """
    if not mensaje_texto:
        return False
        
    text_lower = mensaje_texto.lower()
    
    palabras_clave = [
        # Conceptos de agendamiento
        "cita", "agendar", "apartar", "turno", "reservar", "hora", "fecha", "horario",
        # Taller y servicio
        "taller", "mecanico", "mecánico", "servicio", "revision", "revisión", "revisar",
        "chequeo", "chequear", "diagnostico", "diagnóstico", "inspeccion", "inspección",
        # Tipos de mantenimiento
        "mantenimiento", "preventivo", "correctivo", "general", "express", "overhaul",
        "afinar", "afinacion", "afinación", "sintonizar", "calibrar",
        # Motos y componentes
        "moto", "motocicleta", "motoneta", "scooter", "motor", "aceite", "filtro",
        "freno", "frenos", "pastilla", "pastillas", "disco", "bujia", "bujía", "cadena",
        "llanta", "llantas", "neumatico", "neumático", "rueda", "luces", "faro", "bombillo",
        "bateria", "batería", "carburador", "inyeccion", "inyección", "valvula", "válvula",
        "embrague", "clutch", "transmision", "transmisión", "escape", "mufla",
        # Problemas / averías
        "fuga", "ruido", "fallo", "falla", "averia", "avería", "daño", "dañado",
        "reparar", "reparacion", "reparación", "cambio de", "cambiar", "no arranca",
        "se apaga", "humo", "calienta"
    ]
    
    return any(p in text_lower for p in palabras_clave)

def parse_appointment_details(text, base_dt=None):
    """
    Analiza el texto en español para extraer:
    - Fecha programada (datetime)
    - Tipo de mantenimiento ('Preventivo', 'General', 'Correctivo', 'Express')
    - Resumen interpretado
    """
    if base_dt is None:
        base_dt = datetime.datetime.now()
        
    text_lower = text.lower()
    
    # 1. Determinar Tipo de Mantenimiento (Únicamente Preventivo o General)
    tipo_mantenimiento = "Preventivo" # Valor por defecto
    if any(k in text_lower for k in ["general", "overhaul", "completo", "afinar", "reparar", "frenos", "freno", "fuga", "fallo", "averia"]):
        tipo_mantenimiento = "General"
    else:
        tipo_mantenimiento = "Preventivo"
        
    # 2. Extracción de Fecha
    target_date = base_dt.date()
    
    # Expresiones relativas
    if "pasado mañana" in text_lower or "pasado manana" in text_lower:
        target_date = base_dt.date() + datetime.timedelta(days=2)
    elif "mañana" in text_lower or "manana" in text_lower:
        target_date = base_dt.date() + datetime.timedelta(days=1)
    elif "hoy" in text_lower:
        target_date = base_dt.date()
    else:
        # Días de la semana
        dias_semana = {
            "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
            "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
        }
        found_day = False
        for dia, day_num in dias_semana.items():
            if dia in text_lower:
                current_day_num = base_dt.weekday()
                days_ahead = (day_num - current_day_num) % 7
                if days_ahead == 0:
                    days_ahead = 7 # Próximo mismo día de la semana que viene
                target_date = base_dt.date() + datetime.timedelta(days=days_ahead)
                found_day = True
                break
                
        if not found_day:
            # Buscar fecha explícita YYYY-MM-DD o DD/MM o DD-MM
            iso_match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text)
            ddmm_match = re.search(r'(\d{1,2})[-/](\d{1,2})', text)
            if iso_match:
                try:
                    y, m, d = map(int, iso_match.groups())
                    target_date = datetime.date(y, m, d)
                except ValueError:
                    pass
            elif ddmm_match:
                try:
                    d, m = map(int, ddmm_match.groups())
                    y = base_dt.year
                    target_date = datetime.date(y, m, d)
                except ValueError:
                    pass
            else:
                # Si no especifica día, agendar para el día siguiente por defecto
                target_date = base_dt.date() + datetime.timedelta(days=1)
                
    # 3. Extracción de Hora
    hour = 9 # Hora por defecto: 9:00 AM
    minute = 0
    
    # Buscar formato "10:30 am", "2:00 pm", "14:00", "9 am", "3 pm", "a las 10"
    time_match = re.search(r'(?:a las\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|de la mañana|de la tarde|de la noche)?', text_lower)
    if time_match:
        try:
            h_str, m_str, ampm = time_match.groups()
            h_val = int(h_str)
            m_val = int(m_str) if m_str else 0
            
            if ampm:
                ampm = ampm.strip()
                if ampm in ['pm', 'de la tarde', 'de la noche'] and h_val < 12:
                    h_val += 12
                elif ampm in ['am', 'de la mañana'] and h_val == 12:
                    h_val = 0
            elif h_val >= 7 and h_val <= 18:
                # Hora comercial asumida
                pass
            
            if 0 <= h_val <= 23 and 0 <= m_val <= 59:
                hour = h_val
                minute = m_val
        except (ValueError, TypeError):
            pass

    fecha_programada = datetime.datetime.combine(target_date, datetime.time(hour, minute))
    
    # Asegurar que la fecha no sea del pasado absoluto
    if fecha_programada < base_dt - datetime.timedelta(hours=1):
        fecha_programada = base_dt + datetime.timedelta(days=1)
        fecha_programada = fecha_programada.replace(hour=hour, minute=minute)

    return {
        'fecha_programada': fecha_programada,
        'tipo_mantenimiento': tipo_mantenimiento
    }

def process_incoming_whatsapp_message(telefono_raw, mensaje_texto):
    """
    Procesa un mensaje entrante de WhatsApp para la línea oficial de Taller CR:
    1. Normaliza teléfono y encuentra/crea Cliente.
    2. Evalúa si el mensaje tiene relación con el taller/citas/mantenimiento.
       - Si NO tiene relación: Solo se guarda en el historial para atención manual. NO genera cita ('no le pone mente').
       - Si SÍ tiene relación y el Bot está Activo: Genera la cita, envía auto-respuesta y actualiza en vivo.
    """
    if not telefono_raw or not mensaje_texto:
        return {'success': False, 'error': 'Teléfono y mensaje son obligatorios.'}
        
    # Clean phone
    telefono_clean = re.sub(r'[^\d+]', '', str(telefono_raw))
    if not telefono_clean.startswith('+') and len(telefono_clean) == 8:
        telefono_clean = f"+505{telefono_clean}"
    elif not telefono_clean.startswith('+'):
        telefono_clean = f"+{telefono_clean}"
        
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'Error de conexión con la base de datos.'}
        
    try:
        cursor = conn.cursor()
        
        # Obtener configuración actual del bot
        config = get_whatsapp_config()
        bot_activo = config.get('bot_activo', True)
        
        # 1. Buscar o Crear Cliente
        cursor.execute("SELECT ClienteID, NombreCompleto FROM Clientes WHERE Telefono LIKE ? OR Telefono = ?", 
                       (f"%{telefono_clean[-8:]}", telefono_clean))
        cliente = cursor.fetchone()
        
        if cliente:
            cliente_id = cliente[0]
            nombre_cliente = cliente[1]
        else:
            # Crear nuevo cliente automáticamente con Identificación única para evitar conflicto UNIQUE KEY
            nombre_cliente = f"Cliente WA ({telefono_clean})"
            ident_auto = f"WA-{telefono_clean[-8:]}"
            cursor.execute("""
                INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email)
                OUTPUT INSERTED.ClienteID
                VALUES (?, ?, ?, '')
            """, (ident_auto, nombre_cliente, telefono_clean))
            cliente_id = cursor.fetchone()[0]
            conn.commit()
            
        # Evaluar si el mensaje tiene relación con el taller o citas
        tiene_que_ver_con_taller = es_mensaje_de_taller(mensaje_texto)
        
        # --- CASO 1: EL MENSAJE NO TIENE QUE VER CON EL TALLER ("NO LE PONGA MENTE") ---
        if not tiene_que_ver_con_taller:
            # Se guarda el mensaje en MensajesWhatsApp para que el taller pueda verlo y contestar manual
            cursor.execute("""
                INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID)
                VALUES (?, ?, 'Entrante', ?, 0, NULL)
            """, (telefono_clean, cliente_id, mensaje_texto))
            conn.commit()
            return {
                'success': True,
                'es_taller': False,
                'bot_activo': bot_activo,
                'cliente_id': cliente_id,
                'nombre_cliente': nombre_cliente,
                'telefono': telefono_clean,
                'mensaje': 'Mensaje general recibido. NO tiene relación con citas o taller, por lo que no se generó cita.',
                'respuesta_bot': 'Sin cita agendada (mensaje no relacionado a taller)'
            }
            
        # --- CASO 2: SÍ ES DE TALLER, PERO EL BOT ESTÁ APAGADO ---
        if not bot_activo:
            cursor.execute("""
                INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID)
                VALUES (?, ?, 'Entrante', ?, 0, NULL)
            """, (telefono_clean, cliente_id, mensaje_texto))
            conn.commit()
            return {
                'success': True,
                'es_taller': True,
                'bot_activo': False,
                'cliente_id': cliente_id,
                'nombre_cliente': nombre_cliente,
                'telefono': telefono_clean,
                'mensaje': 'El bot está APAGADO. La solicitud se guardó en el historial para atención manual por el equipo.',
                'respuesta_bot': 'Bot apagado (atención manual requerida)'
            }
            
        # --- CASO 3: SÍ ES DE TALLER Y EL BOT ESTÁ ENCENDIDO (ACTIVO) ---
        # 2. Buscar motocicleta asignada al cliente
        cursor.execute("SELECT TOP 1 MotoID, Marca, Modelo FROM Motocicletas WHERE ClienteID = ?", (cliente_id,))
        moto = cursor.fetchone()
        moto_id = moto[0] if moto else None
        
        # 3. Analizar Fecha y Tipo de Servicio (NLP extractor)
        parsed = parse_appointment_details(mensaje_texto)
        fecha_prog = parsed['fecha_programada']
        tipo_mantenimiento = parsed['tipo_mantenimiento']
        
        # 4. Insertar Cita en CitasWhatsApp
        cursor.execute("""
            INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Notas, Origen)
            OUTPUT INSERTED.CitaID
            VALUES (?, ?, ?, ?, 'Pendiente', ?, 'WhatsApp')
        """, (cliente_id, moto_id, fecha_prog, tipo_mantenimiento, mensaje_texto))
        cita_id = cursor.fetchone()[0]
        
        # 5. Registrar Mensaje Entrante
        cursor.execute("""
            INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID)
            VALUES (?, ?, 'Entrante', ?, 0, ?)
        """, (telefono_clean, cliente_id, mensaje_texto, cita_id))
        
        # 6. Generar Auto-Respuesta del Bot y Enviar
        fecha_str = fecha_prog.strftime('%d/%m/%Y a las %I:%M %p')
        respuesta_bot = (
            "👋 ¡Hola! 🏍️\n\n"
            "¡Gracias por comunicarte con *Taller y Lubricantes CR*!\n\n"
            "Hemos registrado tu solicitud automáticamente:\n"
            f"📋 *Cita #:* {cita_id}\n"
            f"📅 *Fecha sugerida:* {fecha_str}\n"
            f"🔧 *Servicio:* {tipo_mantenimiento}\n\n"
            "Un asesor de nuestro equipo revisará tu cita y te confirmará en breve. ¡Te esperamos!"
        )
        
        # Enviar confirmación real vía API Oficial de Meta
        send_whatsapp_message(telefono_clean, respuesta_bot)
        
        # 7. Registrar Mensaje Saliente (AutoRespuesta)
        cursor.execute("""
            INSERT INTO MensajesWhatsApp (TelefonoCliente, ClienteID, Direccion, Contenido, EsAutoRespuesta, CitaID)
            VALUES (?, ?, 'Saliente', ?, 1, ?)
        """, (telefono_clean, cliente_id, respuesta_bot, cita_id))
        
        conn.commit()
        
        return {
            'success': True,
            'es_taller': True,
            'bot_activo': True,
            'cita_id': cita_id,
            'cliente_id': cliente_id,
            'nombre_cliente': nombre_cliente,
            'telefono': telefono_clean,
            'fecha_programada': fecha_prog.strftime('%Y-%m-%d %H:%M'),
            'tipo_mantenimiento': tipo_mantenimiento,
            'respuesta_bot': respuesta_bot
        }
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': f"Error al procesar cita: {str(e)}"}
    finally:
        conn.close()

if __name__ == '__main__':
    # Test simple
    res = process_incoming_whatsapp_message('+505 8888 7777', 'Hola, quiero una cita de mantenimiento preventivo para mañana a las 10 am')
    print("Resultado Bot WhatsApp:")
    print(f"Exito: {res.get('success')}, CitaID: {res.get('cita_id')}, Cliente: {res.get('nombre_cliente')}")

