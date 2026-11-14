from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from database import get_db_connection
from functools import wraps
from werkzeug.security import generate_password_hash
import math
import datetime
import re

planilla_bp = Blueprint('planilla', __name__)

def _normalizar_telefono_nic(telefono_raw):
    digits = re.sub(r'\D', '', (telefono_raw or '').strip())
    if digits.startswith('505') and len(digits) == 11:
        digits = digits[3:]
    return digits


def _validar_datos_rrhh(
    *,
    nombre=None,
    requerir_nombre=False,
    cedula=None,
    telefono=None,
    domicilio=None,
    cargo=None,
    requerir_cargo=True,
    departamento=None,
    requerir_departamento=True,
    salario_raw=None,
    fecha_inicio_raw=None,
    requerir_fecha=True,
    jornada=None,
    horario=None,
    requerir_jornada_horario=False,
    email=None,
    requerir_email=False,
    password=None,
    requerir_password=False,
    tipo_contrato=None,
    estado=None,
):
    """Valida estrictamente datos de colaboradores y contratos laborales (Nicaragua)."""
    errores = []
    nombre_clean = ' '.join((nombre or '').split())
    cedula_clean = (cedula or '').strip().upper()
    tel_digits = _normalizar_telefono_nic(telefono)
    dom_clean = ' '.join((domicilio or '').split())
    cargo_clean = ' '.join((cargo or '').split())
    depto_clean = ' '.join((departamento or '').split())
    jornada_clean = ' '.join((jornada or '').split())
    horario_clean = ' '.join((horario or '').split())
    email_clean = (email or '').strip()

    if requerir_nombre or nombre_clean:
        palabras = [w for w in nombre_clean.split(' ') if w]
        if len(nombre_clean) < 5 or len(nombre_clean) > 100 or len(palabras) < 2:
            errores.append('El Nombre Completo debe incluir al menos nombre y apellido (mínimo 5 caracteres).')
        elif not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñüÜ\s.]+$', nombre_clean):
            errores.append('El Nombre Completo solo puede contener letras y espacios (sin números ni símbolos).')

    if not re.match(r'^\d{3}-\d{6}-\d{4}[A-Z]$', cedula_clean):
        errores.append('La Cédula debe seguir el formato oficial de Nicaragua: 001-DDMMAA-0000X (Ej: 001-150595-0023A).')
    else:
        partes_ced = cedula_clean.split('-')
        medio = partes_ced[1]
        dia, mes = int(medio[0:2]), int(medio[2:4])
        if medio == '000000' or partes_ced[2][:4] == '0000' or len(set(medio)) == 1 or dia < 1 or dia > 31 or mes < 1 or mes > 12:
            errores.append('La Cédula ingresada contiene una fecha de nacimiento o secuencia inválida (no se aceptan ceros ni datos ficticios).')

    if not tel_digits or not re.match(r'^[2578]\d{7}$', tel_digits):
        errores.append('El Teléfono debe tener exactamente 8 dígitos válidos de Nicaragua iniciando en 2, 5, 7 u 8 (Ej: 88887777 o +505 88887777).')
    tel_formateado = f"+505 {tel_digits[:4]} {tel_digits[4:]}" if len(tel_digits) == 8 else ''

    if not dom_clean or len(dom_clean) < 6 or len(dom_clean) > 200 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', dom_clean):
        errores.append('El Domicilio es obligatorio, debe tener mínimo 6 caracteres y describir una dirección válida con letras.')

    if requerir_cargo or cargo_clean:
        if len(cargo_clean) < 3 or len(cargo_clean) > 80 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', cargo_clean):
            errores.append('El Cargo / Puesto debe tener al menos 3 letras válidas.')

    if requerir_departamento or depto_clean:
        if len(depto_clean) < 3 or len(depto_clean) > 80 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', depto_clean):
            errores.append('El Departamento debe tener al menos 3 letras válidas.')

    try:
        salario_val = float(salario_raw)
        if not math.isfinite(salario_val) or salario_val < 1000 or salario_val > 500000:
            errores.append('El Salario Base/Pactado debe estar entre C$ 1,000.00 y C$ 500,000.00.')
    except (TypeError, ValueError):
        salario_val = 0.0
        errores.append('El Salario Base/Pactado debe ser un monto numérico válido.')

    fecha_obj = None
    fecha_raw_clean = (fecha_inicio_raw or '').strip()
    if requerir_fecha or fecha_raw_clean:
        try:
            fecha_obj = datetime.date.fromisoformat(fecha_raw_clean)
            hoy = datetime.date.today()
            if fecha_obj < datetime.date(1990, 1, 1) or fecha_obj > hoy + datetime.timedelta(days=365):
                errores.append('La Fecha de Inicio debe estar entre 1990 y máximo 1 año a futuro.')
        except ValueError:
            errores.append('La Fecha de Inicio ingresada no tiene un formato válido (YYYY-MM-DD).')

    if requerir_jornada_horario:
        if not jornada_clean or len(jornada_clean) < 4 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', jornada_clean):
            errores.append('La Jornada laboral es obligatoria (mínimo 4 caracteres con letras).')
        if not horario_clean or len(horario_clean) < 4:
            errores.append('El Horario laboral es obligatorio (mínimo 4 caracteres).')

    if requerir_email or email_clean:
        if len(email_clean) < 4 or len(email_clean) > 80 or ' ' in email_clean or not re.match(r'^[A-Za-z0-9._@-]+$', email_clean):
            errores.append('El Usuario / Correo de Acceso debe tener entre 4 y 80 caracteres sin espacios (letras, números, ".", "_", "@", "-").')

    if requerir_password or (password is not None and len(password) > 0):
        if len(password or '') < 6:
            errores.append('La Contraseña de acceso debe tener al menos 6 caracteres.')

    if tipo_contrato is not None and tipo_contrato not in ('Tiempo Indeterminado', 'Plazo Determinado', 'Por Obra o Servicio Determinado'):
        errores.append('El Tipo de Contrato seleccionado no es válido.')

    if estado is not None and estado not in ('Vigente', 'En Revisión', 'Finalizado'):
        errores.append('El Estado del Contrato seleccionado no es válido.')

    return errores, {
        'nombre': nombre_clean,
        'cedula': cedula_clean,
        'telefono': tel_formateado,
        'domicilio': dom_clean,
        'cargo': cargo_clean,
        'departamento': depto_clean,
        'salario': round(salario_val, 2),
        'fecha_inicio': fecha_obj.isoformat() if fecha_obj else None,
        'jornada': jornada_clean,
        'horario': horario_clean,
        'email': email_clean,
    }

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificación de permisos para RRHH y Contabilidad
        # Acceso a Dirección (1, 5), RRHH (1007) y Contabilidad/Finanzas (roles 4, 6, 'carlos.contabilidad', 'carlos.finanzas')
        rol = session.get('rol_id')
        uname = session.get('username')
        rol_nom = session.get('rol_nombre', '') or ''
        roles_permitidos = (1, 4, 5, 6, 1007)
        tiene_acceso = (rol in roles_permitidos) or ('Contador' in rol_nom) or (uname in ('carlos.contabilidad', 'carlos.finanzas'))
        if 'usuario_id' not in session or not tiene_acceso:
            flash('Acceso restringido. El módulo de Recursos Humanos es de uso exclusivo para Dirección y RRHH.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# MARCO NORMATIVO DGI (LEY N° 822 DE CONCERTACIÓN TRIBUTARIA - ARTÍCULO 23)
# ==============================================================================
TABLA_DGI_LEY_822 = [
    {
        'tramo': 1,
        'estrato': 'De C$ 0.01 a C$ 100,000.00',
        'limite_inferior': 0.0,
        'limite_superior': 100000.0,
        'impuesto_base': 0.0,
        'porcentaje': 0,
        'sobre_exceso': 0.0,
        'descripcion': 'Exento de retención salarial según Art. 23 Ley 822.'
    },
    {
        'tramo': 2,
        'estrato': 'De C$ 100,000.01 a C$ 200,000.00',
        'limite_inferior': 100000.0,
        'limite_superior': 200000.0,
        'impuesto_base': 0.0,
        'porcentaje': 15,
        'sobre_exceso': 100000.0,
        'descripcion': 'Aplica el 15% sobre el exceso de C$ 100,000.00.'
    },
    {
        'tramo': 3,
        'estrato': 'De C$ 200,000.01 a C$ 350,000.00',
        'limite_inferior': 200000.0,
        'limite_superior': 350000.0,
        'impuesto_base': 15000.0,
        'porcentaje': 20,
        'sobre_exceso': 200000.0,
        'descripcion': 'C$ 15,000.00 base + 20% sobre el exceso de C$ 200,000.00.'
    },
    {
        'tramo': 4,
        'estrato': 'De C$ 350,000.01 a C$ 500,000.00',
        'limite_inferior': 350000.0,
        'limite_superior': 500000.0,
        'impuesto_base': 45000.0,
        'porcentaje': 25,
        'sobre_exceso': 350000.0,
        'descripcion': 'C$ 45,000.00 base + 25% sobre el exceso de C$ 350,000.00.'
    },
    {
        'tramo': 5,
        'estrato': 'De C$ 500,000.01 a más',
        'limite_inferior': 500000.0,
        'limite_superior': None,
        'impuesto_base': 82500.0,
        'porcentaje': 30,
        'sobre_exceso': 500000.0,
        'descripcion': 'C$ 82,500.00 base + 30% sobre el exceso de C$ 500,000.00.'
    }
]

def calcular_desglose_laboral_y_dgi(salario_bruto, meses_acumulados=0):
    """
    Calcula de manera exacta y auditable las deducciones al trabajador y cargas
    patronales de acuerdo a la Ley 185 (Código del Trabajo de Nicaragua), la Ley 822
    (Ley de Concertación Tributaria de la DGI) y la Ley de Seguridad Social (INSS).
    """
    salario_bruto = float(salario_bruto or 0.0)
    meses_acumulados = int(meses_acumulados or 0)

    # 1. Deducción INSS Laboral (7%) - No gravable según Art. 19 Ley 822 DGI
    inss_laboral = round(salario_bruto * 0.07, 2)

    # 2. Base Imponible Mensual para el cálculo del IR
    base_imponible_mensual = round(salario_bruto - inss_laboral, 2)

    # 3. Proyección Anual de la Renta Gravable
    renta_anual_proyectada = round(base_imponible_mensual * 12.0, 2)

    # 4. Tabla Progresiva DGI (Art. 23 Ley 822)
    tramo_aplicable = 1
    tasa_dgi = 0
    impuesto_base_dgi = 0.0
    sobre_exceso_dgi = 0.0
    exceso_dgi = 0.0
    ir_anual = 0.0

    if renta_anual_proyectada <= 100000.00:
        tramo_aplicable = 1
        tasa_dgi = 0
        impuesto_base_dgi = 0.0
        sobre_exceso_dgi = 0.0
        exceso_dgi = 0.0
        ir_anual = 0.0
    elif renta_anual_proyectada <= 200000.00:
        tramo_aplicable = 2
        tasa_dgi = 15
        impuesto_base_dgi = 0.0
        sobre_exceso_dgi = 100000.00
        exceso_dgi = round(renta_anual_proyectada - 100000.00, 2)
        ir_anual = round(exceso_dgi * 0.15, 2)
    elif renta_anual_proyectada <= 350000.00:
        tramo_aplicable = 3
        tasa_dgi = 20
        impuesto_base_dgi = 15000.00
        sobre_exceso_dgi = 200000.00
        exceso_dgi = round(renta_anual_proyectada - 200000.00, 2)
        ir_anual = round(15000.00 + (exceso_dgi * 0.20), 2)
    elif renta_anual_proyectada <= 500000.00:
        tramo_aplicable = 4
        tasa_dgi = 25
        impuesto_base_dgi = 45000.00
        sobre_exceso_dgi = 350000.00
        exceso_dgi = round(renta_anual_proyectada - 350000.00, 2)
        ir_anual = round(45000.00 + (exceso_dgi * 0.25), 2)
    else:
        tramo_aplicable = 5
        tasa_dgi = 30
        impuesto_base_dgi = 82500.00
        sobre_exceso_dgi = 500000.00
        exceso_dgi = round(renta_anual_proyectada - 500000.00, 2)
        ir_anual = round(82500.00 + (exceso_dgi * 0.30), 2)

    # 5. Retención Mensual del IR a declarar en DGI
    ir_mensual = round(ir_anual / 12.0, 2)

    # 6. Salario Neto Líquido a Pagar al Trabajador
    salario_neto = round(salario_bruto - inss_laboral - ir_mensual, 2)

    # 7. Aportes Patronales (Costos de Empresa)
    # INSS Patronal: 22.5% (Taller CR, Decreto de Seguridad Social)
    inss_patronal = round(salario_bruto * 0.225, 2)
    # INATEC: 2.0% (Capacitación Técnica Obligatoria)
    inatec = round(salario_bruto * 0.02, 2)

    # 8. Provisiones Sociales y Prestaciones Laborales (Ley 185)
    # Décimo Tercer Mes (Aguinaldo) - Art. 93 Ley 185 (8.333% mensual)
    meses_aguinaldo = (meses_acumulados - 1) % 12 + 1 if meses_acumulados > 0 else 0
    aguinaldo_acumulado = round((salario_bruto / 12.0) * meses_aguinaldo, 2)
    aguinaldo_mensual = round(salario_bruto / 12.0, 2)

    # Vacaciones Remuneradas - Arts. 76-81 Ley 185 (30 días anuales = 8.333% mensual)
    vacaciones_acumuladas = round((salario_bruto / 12.0) * meses_acumulados, 2)
    vacaciones_mensuales = round(salario_bruto / 12.0, 2)

    # Indemnización por Años de Servicio - Art. 45 Ley 185 (8.333% mensual)
    indemnizacion_acumulada = round((salario_bruto / 12.0) * meses_acumulados, 2)
    indemnizacion_mensual = round(salario_bruto / 12.0, 2)

    total_provisiones_acumuladas = round(aguinaldo_acumulado + vacaciones_acumuladas + indemnizacion_acumulada, 2)
    total_provisiones_mensuales = round(aguinaldo_mensual + vacaciones_mensuales + indemnizacion_mensual, 2)
    costo_total_empleador = round(salario_bruto + inss_patronal + inatec + total_provisiones_mensuales, 2)

    return {
        'salario_bruto': salario_bruto,
        'inss_laboral': inss_laboral,
        'base_imponible_mensual': base_imponible_mensual,
        'renta_anual_proyectada': renta_anual_proyectada,
        'tramo_dgi': tramo_aplicable,
        'tasa_dgi': tasa_dgi,
        'impuesto_base_dgi': impuesto_base_dgi,
        'sobre_exceso_dgi': sobre_exceso_dgi,
        'exceso_dgi': exceso_dgi,
        'ir_anual': ir_anual,
        'ir_mensual': ir_mensual,
        'salario_neto': salario_neto,
        'inss_patronal': inss_patronal,
        'inatec': inatec,
        'meses_acumulados': meses_acumulados,
        'meses_aguinaldo': meses_aguinaldo,
        'aguinaldo': aguinaldo_acumulado,
        'aguinaldo_mensual': aguinaldo_mensual,
        'vacaciones': vacaciones_acumuladas,
        'vacaciones_mensuales': vacaciones_mensuales,
        'indemnizacion': indemnizacion_acumulada,
        'indemnizacion_mensual': indemnizacion_mensual,
        'total_provisiones': total_provisiones_acumuladas,
        'total_provisiones_mensuales': total_provisiones_mensuales,
        'costo_total_empleador': costo_total_empleador
    }

# ==============================================================================
# SUBMÓDULO 1: OBTENCIÓN Y CÁLCULO DE NÓMINA MENSUAL (RECURSOS HUMANOS / DGI)
# ==============================================================================
def obtener_totales_nomina_mes(mes=None, anio=None):
    """
    Consolida la nómina legal de Taller y Lubricantes CR (MIPYME) conforme a:
    - Ley N° 185 (Código del Trabajo de Nicaragua)
    - Ley N° 822 (Ley de Concertación Tributaria de la DGI)
    - Sistema de Productividad para Mecánicos (Bono de C$ 500 por cada 5 vehículos atendidos)
    - Deducciones por inasistencias/faltas: (Salario Base / 30) * Días faltados
    - Deducciones y bonos extraordinarios editables en tiempo real.
    - Exclusión estricta de Elvin Alexander (UsuarioID: 1) por ser el creador/administrador técnico.
    """
    now = datetime.datetime.now()
    mes = int(mes) if mes else now.month
    anio = int(anio) if anio else now.year

    conn = get_db_connection()
    if not conn:
        return {
            'planilla_permanentes': [],
            'planilla_asesores': [],
            'todos': [],
            'totales': {
                'salario_base': 0.0, 'dias_faltados': 0, 'deduccion_faltas': 0.0,
                'bono_vehiculos': 0.0, 'bonos_extras': 0.0, 'otras_deducciones': 0.0,
                'salario_bruto': 0.0, 'inss_laboral': 0.0, 'base_imponible_ir': 0.0,
                'ir': 0.0, 'salario_neto': 0.0, 'inss_patronal': 0.0, 'inatec': 0.0,
                'cargas_patronales': 0.0, 'provisiones_acumuladas': 0.0,
                'provisiones_mensuales': 0.0, 'costo_total_empleador': 0.0,
                'vehiculos_atendidos': 0
            },
            'totales_permanentes': {'cantidad': 0, 'salario_base': 0.0, 'salario_bruto': 0.0, 'inss_laboral': 0.0, 'base_imponible_ir': 0.0, 'ir': 0.0, 'salario_neto': 0.0, 'inss_patronal': 0.0, 'inatec': 0.0, 'cargas_patronales': 0.0, 'provisiones_mensuales': 0.0, 'costo_total_empleador': 0.0},
            'totales_asesores': {'cantidad': 0, 'salario_base': 0.0, 'salario_bruto': 0.0, 'inss_laboral': 0.0, 'base_imponible_ir': 0.0, 'ir': 0.0, 'salario_neto': 0.0, 'inss_patronal': 0.0, 'inatec': 0.0, 'cargas_patronales': 0.0, 'provisiones_mensuales': 0.0, 'costo_total_empleador': 0.0},
            'resumen_dgi': {'total_renta_gravable': 0.0, 'total_retenido_ir': 0.0, 'empleados_con_retencion': 0, 'empleados_exentos': 0},
            'mes': mes,
            'anio': anio
        }

    cursor = conn.cursor()
    # Empleados activos (Excluye a Elvin Alexander Méndez Cruz y a carlos.contabilidad)
    cursor.execute("""
        SELECT U.UsuarioID, U.NombreCompleto, R.NombreRol, U.SalarioBase, U.MesesAcumulados, U.Email,
               C.NumeroContrato, C.Cargo, C.Departamento, C.CedulaIdentidad,
               C.TipoContrato, C.Jornada, C.Horario, C.FechaInicio
        FROM Usuarios U
        JOIN Roles R ON U.RolID = R.RolID
        LEFT JOIN ContratosLaborales C ON U.UsuarioID = C.UsuarioID
        WHERE U.Activo = 1 AND U.UsuarioID != 1 AND U.Email NOT IN ('carlos.contabilidad', 'elvin.admin')
        ORDER BY U.UsuarioID ASC
    """)
    empleados = cursor.fetchall()

    cursor.execute("""
        SELECT UsuarioID, DiasFaltados, DeduccionFaltas, OtrasDeducciones, MotivoDeduccion,
               BonosExtras, MotivoBono, VehiculosAtendidos, BonoVehiculos, TasaBonoVehiculo, Pagado
        FROM NovedadesNomina
        WHERE Mes = ? AND Anio = ?
    """, (mes, anio))
    novedades_map = {}
    for r in cursor.fetchall():
        novedades_map[r[0]] = {
            'dias_faltados': int(r[1] or 0),
            'deduccion_faltas': float(r[2] or 0.0),
            'otras_deducciones': float(r[3] or 0.0),
            'motivo_deduccion': r[4] or '',
            'bonos_extras': float(r[5] or 0.0),
            'motivo_bono': r[6] or '',
            'vehiculos_atendidos': int(r[7] or 0),
            'bono_vehiculos': float(r[8] or 0.0),
            'tasa_bono_vehiculo': float(r[9] or 500.0),
            'pagado': bool(r[10]) if len(r) > 10 and r[10] is not None else False
        }

    cursor.execute("""
        SELECT MecanicoID, COUNT(*) 
        FROM OrdenesTrabajo 
        WHERE MecanicoID IS NOT NULL AND MecanicoID != 1
        GROUP BY MecanicoID
    """)
    ordenes_map = dict(cursor.fetchall())
    conn.close()

    planilla_permanentes = []
    planilla_asesores = []

    totales = {
        'cantidad_pagados': 0,
        'cantidad_pendientes': 0,
        'salario_base': 0.0,
        'salario_base_total': 0.0,
        'dias_faltados': 0,
        'deduccion_faltas': 0.0,
        'bono_vehiculos': 0.0,
        'bonos_extras': 0.0,
        'otras_deducciones': 0.0,
        'salario_bruto': 0.0,
        'inss_laboral': 0.0,
        'base_imponible_ir': 0.0,
        'ir': 0.0,
        'salario_neto': 0.0,
        'inss_patronal': 0.0,
        'inatec': 0.0,
        'cargas_patronales': 0.0,
        'provisiones_acumuladas': 0.0,
        'provisiones_mensuales': 0.0,
        'costo_total_empleador': 0.0,
        'vehiculos_atendidos': 0
    }

    totales_permanentes = {
        'cantidad': 0,
        'cantidad_pagados': 0,
        'cantidad_pendientes': 0,
        'salario_base': 0.0,
        'salario_base_total': 0.0,
        'dias_faltados': 0,
        'deduccion_faltas': 0.0,
        'bono_vehiculos': 0.0,
        'bonos_extras': 0.0,
        'otras_deducciones': 0.0,
        'vehiculos_atendidos': 0,
        'salario_bruto': 0.0,
        'inss_laboral': 0.0,
        'base_imponible_ir': 0.0,
        'ir': 0.0,
        'salario_neto': 0.0,
        'inss_patronal': 0.0,
        'inatec': 0.0,
        'cargas_patronales': 0.0,
        'provisiones_acumuladas': 0.0,
        'provisiones_mensuales': 0.0,
        'costo_total_empleador': 0.0
    }

    totales_asesores = {
        'cantidad': 0,
        'cantidad_pagados': 0,
        'cantidad_pendientes': 0,
        'salario_base': 0.0,
        'salario_base_total': 0.0,
        'dias_faltados': 0,
        'deduccion_faltas': 0.0,
        'bono_vehiculos': 0.0,
        'bonos_extras': 0.0,
        'otras_deducciones': 0.0,
        'vehiculos_atendidos': 0,
        'salario_bruto': 0.0,
        'inss_laboral': 0.0,
        'base_imponible_ir': 0.0,
        'ir': 0.0,
        'salario_neto': 0.0,
        'inss_patronal': 0.0,
        'inatec': 0.0,
        'cargas_patronales': 0.0,
        'provisiones_acumuladas': 0.0,
        'provisiones_mensuales': 0.0,
        'costo_total_empleador': 0.0
    }

    resumen_dgi = {
        'total_renta_gravable': 0.0,
        'total_retenido_ir': 0.0,
        'empleados_con_retencion': 0,
        'empleados_exentos': 0
    }

    for emp in empleados:
        usuario_id = emp[0]
        nombre = emp[1]
        rol = emp[2]
        salario_base = float(emp[3]) if emp[3] else 0.0
        meses_acumulados = int(emp[4]) if emp[4] else 0
        email = emp[5]
        num_contrato = emp[6] or f"CTR-TCR-{usuario_id:03d}"
        cargo_contrato = emp[7] or rol
        depto = emp[8] or 'Operaciones'
        cedula = emp[9] or 'N/D'
        tipo_contrato = emp[10]
        jornada = emp[11]
        horario = emp[12]
        fecha_inicio_c = emp[13] if len(emp) > 13 else None

        # Si meses_acumulados no fue fijado manualmente o es 0, calcular automáticamente por antigüedad
        if (meses_acumulados <= 0) and fecha_inicio_c:
            diff_m = (anio - fecha_inicio_c.year) * 12 + (mes - fecha_inicio_c.month) + 1
            if diff_m > 0:
                meses_acumulados = diff_m
        elif meses_acumulados <= 0:
            meses_acumulados = 10 # Default 2026 actual periodo Jan-Oct

        is_asesor = (email in ('carlos.finanzas', 'martha.estadistica')) or ('Asesor' in (cargo_contrato or '')) or ('Asesoría' in (tipo_contrato or ''))
        is_mecanico = ('Mecánico' in rol) or ('Mecánico' in (cargo_contrato or ''))

        nov = novedades_map.get(usuario_id)
        if nov:
            dias_faltados = nov['dias_faltados']
            deduccion_faltas = nov['deduccion_faltas']
            otras_deducciones = nov['otras_deducciones']
            motivo_deduccion = nov['motivo_deduccion']
            bonos_extras = nov['bonos_extras']
            motivo_bono = nov['motivo_bono']
            vehiculos_atendidos = nov['vehiculos_atendidos']
            tasa_bono_vehiculo = nov['tasa_bono_vehiculo']
            bono_vehiculos = nov['bono_vehiculos']
            pagado = nov['pagado']
        else:
            dias_faltados = 0
            deduccion_faltas = 0.0
            otras_deducciones = 0.0
            motivo_deduccion = ''
            bonos_extras = 0.0
            motivo_bono = ''
            vehiculos_atendidos = ordenes_map.get(usuario_id, 0) if is_mecanico else 0
            tasa_bono_vehiculo = 500.0
            bono_vehiculos = (vehiculos_atendidos // 5) * tasa_bono_vehiculo
            pagado = False

        # Días que vino a trabajar en el mes (base comercial de 30 días según Código del Trabajo Ley 185)
        dias_trabajados = max(0, 30 - dias_faltados)
        porcentaje_asistencia = round((dias_trabajados / 30.0) * 100, 1)

        # Si hubo inasistencias y no se registró monto manual, aplicar deducción legal: (Salario Base / 30) * Días Faltados
        if dias_faltados > 0 and deduccion_faltas == 0.0:
            deduccion_faltas = round((salario_base / 30.0) * dias_faltados, 2)

        # Cálculo completo y fidedigno según Código del Trabajo (Ley 185) y DGI (Ley 822)
        total_bonos = round(bonos_extras + bono_vehiculos, 2)
        total_deducciones = round(deduccion_faltas + otras_deducciones, 2)
        calc_salario_bruto = round(max(0.0, salario_base + total_bonos - total_deducciones), 2)

        calc = calcular_desglose_laboral_y_dgi(calc_salario_bruto, meses_acumulados)

        # Si NO se ha presionado el botón Pagar, todos los montos de desembolso salarial están en 0.00
        # hasta que se accione el botón Pagar
        if pagado:
            salario_bruto_activo = calc['salario_bruto']
            inss_laboral_activo = calc['inss_laboral']
            base_imponible_activa = calc['base_imponible_mensual']
            tramo_dgi_activo = calc['tramo_dgi']
            tasa_dgi_activa = calc['tasa_dgi']
            ir_activo = calc['ir_mensual']
            salario_neto_activo = calc['salario_neto']
            inss_patronal_activo = calc['inss_patronal']
            inatec_activo = calc['inatec']
            cargas_patronales_activas = round(calc['inss_patronal'] + calc['inatec'], 2)
            aguinaldo_activo = calc['aguinaldo']
            vacaciones_activas = calc['vacaciones']
            indemnizacion_activa = calc['indemnizacion']
            total_provisiones_activas = calc['total_provisiones']
            total_provisiones_mensuales_activas = calc['total_provisiones_mensuales']
            costo_total_empleador_activo = calc['costo_total_empleador']
            deduccion_faltas_activa = deduccion_faltas
            total_bonos_activo = total_bonos
            total_deducciones_ajustes_activo = total_deducciones
        else:
            salario_bruto_activo = 0.0
            inss_laboral_activo = 0.0
            base_imponible_activa = 0.0
            tramo_dgi_activo = 'Pendiente'
            tasa_dgi_activa = 0.0
            ir_activo = 0.0
            salario_neto_activo = 0.0
            inss_patronal_activo = 0.0
            inatec_activo = 0.0
            cargas_patronales_activas = 0.0
            aguinaldo_activo = 0.0
            vacaciones_activas = 0.0
            indemnizacion_activa = 0.0
            total_provisiones_activas = 0.0
            total_provisiones_mensuales_activas = 0.0
            costo_total_empleador_activo = 0.0
            deduccion_faltas_activa = 0.0
            total_bonos_activo = 0.0
            total_deducciones_ajustes_activo = 0.0

        empleado_item = {
            'id': usuario_id,
            'nombre': nombre,
            'email': email,
            'rol': rol,
            'cargo': cargo_contrato,
            'depto': depto,
            'cedula': cedula,
            'num_contrato': num_contrato,
            'es_asesor': is_asesor,
            'es_mecanico': is_mecanico,
            'categoria_codigo': 'asesor' if is_asesor else 'permanente',
            'categoria_nombre': 'Asesor Externo de Cierre Mensual' if is_asesor else 'Personal Permanente de Planta',
            'modalidad': '1 Día al Mes (Cierre Mensual - Pago Único)' if is_asesor else 'Presencial Diario (Lunes a Sábado)',
            'tipo_pago': 'Honorario Único de Cierre' if is_asesor else 'Salario Fijo Mensual',
            'tipo_contrato': tipo_contrato or ('Asesoría Externa / Cierre Mensual' if is_asesor else 'Tiempo Indeterminado'),
            'jornada': jornada or ('Periódica Mensual (1 día al mes - Cierre)' if is_asesor else 'Diurna Ordinaria (48 hrs)'),
            'horario': horario or ('Día de Cierre de Mes: 8:00 AM - 5:00 PM' if is_asesor else 'Lunes a Sábado: 8:00 AM - 5:00 PM'),
            'salario_base': salario_base,
            'dias_trabajados': dias_trabajados,
            'porcentaje_asistencia': porcentaje_asistencia,
            'dias_faltados': dias_faltados,
            'pagado': pagado,
            # Valores activos en pantalla (en 0.00 si no se ha pagado)
            'salario_bruto': salario_bruto_activo,
            'inss_laboral': inss_laboral_activo,
            'base_imponible_mensual': base_imponible_activa,
            'tramo_dgi': tramo_dgi_activo,
            'tasa_dgi': tasa_dgi_activa,
            'ir': ir_activo,
            'salario_neto': salario_neto_activo,
            'inss_patronal': inss_patronal_activo,
            'inatec': inatec_activo,
            'cargas_patronales': cargas_patronales_activas,
            'aguinaldo': aguinaldo_activo,
            'vacaciones': vacaciones_activas,
            'indemnizacion': indemnizacion_activa,
            'total_provisiones': total_provisiones_activas,
            'total_provisiones_mensuales': total_provisiones_mensuales_activas,
            'costo_total_empleador': costo_total_empleador_activo,
            'deduccion_faltas': deduccion_faltas_activa,
            'total_bonos': total_bonos_activo,
            'total_deducciones_ajustes': total_deducciones_ajustes_activo,
            'otras_deducciones': otras_deducciones if pagado else 0.0,
            'bonos_extras': bonos_extras if pagado else 0.0,
            'bono_vehiculos': bono_vehiculos if pagado else 0.0,
            'motivo_deduccion': motivo_deduccion,
            'motivo_bono': motivo_bono,
            'vehiculos_atendidos': vehiculos_atendidos,
            'tasa_bono_vehiculo': tasa_bono_vehiculo,
            'meses': calc['meses_acumulados'],
            'impuesto_base_dgi': calc['impuesto_base_dgi'] if pagado else 0.0,
            'sobre_exceso_dgi': calc['sobre_exceso_dgi'] if pagado else 0.0,
            'exceso_dgi': calc['exceso_dgi'] if pagado else 0.0,
            'ir_anual': calc['ir_anual'] if pagado else 0.0,
            'renta_anual_proyectada': calc['renta_anual_proyectada'] if pagado else 0.0,
            # Valores calculados potenciales (calculados al activar Pagar)
            'calc_salario_bruto': calc['salario_bruto'],
            'calc_inss_laboral': calc['inss_laboral'],
            'calc_base_imponible_mensual': calc['base_imponible_mensual'],
            'calc_renta_anual_proyectada': calc['renta_anual_proyectada'],
            'calc_tramo_dgi': calc['tramo_dgi'],
            'calc_tasa_dgi': calc['tasa_dgi'],
            'calc_ir': calc['ir_mensual'],
            'calc_salario_neto': calc['salario_neto'],
            'calc_inss_patronal': calc['inss_patronal'],
            'calc_inatec': calc['inatec'],
            'calc_cargas_patronales': round(calc['inss_patronal'] + calc['inatec'], 2),
            'calc_aguinaldo': calc['aguinaldo'],
            'calc_vacaciones': calc['vacaciones'],
            'calc_indemnizacion': calc['indemnizacion'],
            'calc_total_provisiones': calc['total_provisiones'],
            'calc_total_provisiones_mensuales': calc['total_provisiones_mensuales'],
            'calc_costo_total_empleador': calc['costo_total_empleador'],
            'calc_total_bonos': total_bonos,
            'calc_total_deducciones': total_deducciones,
            'calc_deduccion_faltas': deduccion_faltas,
            'calc_bono_vehiculos': bono_vehiculos,
            'calc_bonos_extras': bonos_extras,
            'calc_otras_deducciones': otras_deducciones
        }

        if is_asesor:
            planilla_asesores.append(empleado_item)
            subtot = totales_asesores
        else:
            planilla_permanentes.append(empleado_item)
            subtot = totales_permanentes

        subtot['cantidad'] += 1
        subtot['salario_base_total'] += salario_base
        totales['salario_base_total'] += salario_base

        if pagado:
            subtot['cantidad_pagados'] += 1
            totales['cantidad_pagados'] += 1

            subtot['salario_base'] += salario_base
            subtot['dias_faltados'] += dias_faltados
            subtot['deduccion_faltas'] += deduccion_faltas
            subtot['bono_vehiculos'] += bono_vehiculos
            subtot['bonos_extras'] += bonos_extras
            subtot['otras_deducciones'] += otras_deducciones
            subtot['vehiculos_atendidos'] += vehiculos_atendidos
            subtot['salario_bruto'] += calc['salario_bruto']
            subtot['inss_laboral'] += calc['inss_laboral']
            subtot['base_imponible_ir'] += calc['base_imponible_mensual']
            subtot['ir'] += calc['ir_mensual']
            subtot['salario_neto'] += calc['salario_neto']
            subtot['inss_patronal'] += calc['inss_patronal']
            subtot['inatec'] += calc['inatec']
            subtot['cargas_patronales'] += round(calc['inss_patronal'] + calc['inatec'], 2)
            subtot['provisiones_acumuladas'] += calc['total_provisiones']
            subtot['provisiones_mensuales'] += calc['total_provisiones_mensuales']
            subtot['costo_total_empleador'] += calc['costo_total_empleador']

            totales['salario_base'] += salario_base
            totales['dias_faltados'] += dias_faltados
            totales['deduccion_faltas'] += deduccion_faltas
            totales['bono_vehiculos'] += bono_vehiculos
            totales['bonos_extras'] += bonos_extras
            totales['otras_deducciones'] += otras_deducciones
            totales['vehiculos_atendidos'] += vehiculos_atendidos
            totales['salario_bruto'] += calc['salario_bruto']
            totales['inss_laboral'] += calc['inss_laboral']
            totales['base_imponible_ir'] += calc['base_imponible_mensual']
            totales['ir'] += calc['ir_mensual']
            totales['salario_neto'] += calc['salario_neto']
            totales['inss_patronal'] += calc['inss_patronal']
            totales['inatec'] += calc['inatec']
            totales['cargas_patronales'] += round(calc['inss_patronal'] + calc['inatec'], 2)
            totales['provisiones_acumuladas'] += calc['total_provisiones']
            totales['provisiones_mensuales'] += calc['total_provisiones_mensuales']
            totales['costo_total_empleador'] += calc['costo_total_empleador']

            resumen_dgi['total_renta_gravable'] += calc['base_imponible_mensual']
            resumen_dgi['total_retenido_ir'] += calc['ir_mensual']
            if calc['ir_mensual'] > 0:
                resumen_dgi['empleados_con_retencion'] += 1
            else:
                resumen_dgi['empleados_exentos'] += 1
        else:
            subtot['cantidad_pendientes'] += 1
            totales['cantidad_pendientes'] += 1

    return {
        'planilla_permanentes': planilla_permanentes,
        'planilla_asesores': planilla_asesores,
        'todos': planilla_permanentes + planilla_asesores,
        'totales': totales,
        'totales_permanentes': totales_permanentes,
        'totales_asesores': totales_asesores,
        'resumen_dgi': resumen_dgi,
        'mes': mes,
        'anio': anio
    }

# ==============================================================================
# SUBMÓDULO 1.1: VISTA PRINCIPAL DE LA PLANILLA DE PAGO MENSUAL
# ==============================================================================
@planilla_bp.route('/admin/planilla')
@admin_required
def index():
    mes = request.args.get('mes', type=int) or datetime.datetime.now().month
    anio = request.args.get('anio', type=int) or datetime.datetime.now().year

    data = obtener_totales_nomina_mes(mes, anio)

    return render_template(
        'admin/planilla.html', 
        planilla=data['todos'],
        planilla_permanentes=data['planilla_permanentes'],
        planilla_asesores=data['planilla_asesores'],
        totales=data['totales'],
        totales_permanentes=data['totales_permanentes'],
        totales_asesores=data['totales_asesores'],
        resumen_dgi=data['resumen_dgi'],
        tabla_dgi=TABLA_DGI_LEY_822,
        mes_seleccionado=mes,
        anio_seleccionado=anio
    )

# ==============================================================================
# SUBMÓDULO 1.15: ACCIÓN DE PAGO (PAGAR / NO PAGAR) POR EMPLEADO O EN LOTE (JSON)
# ==============================================================================
@planilla_bp.route('/admin/planilla/toggle_pago', methods=['POST'])
@admin_required
def toggle_pago():
    data = request.get_json() or {}
    usuario_id = data.get('usuario_id')
    pagado_val = 1 if data.get('pagado') else 0
    todos = bool(data.get('todos', False))

    now = datetime.datetime.now()
    mes = int(data.get('mes') or now.month)
    anio = int(data.get('anio') or now.year)

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'No se pudo conectar a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        if todos:
            cursor.execute("""
                SELECT UsuarioID FROM Usuarios 
                WHERE Activo = 1 AND UsuarioID != 1 AND Email NOT IN ('carlos.contabilidad', 'elvin.admin')
            """)
            emp_ids = [r[0] for r in cursor.fetchall()]
            for uid in emp_ids:
                cursor.execute("""
                    IF EXISTS (SELECT 1 FROM NovedadesNomina WHERE UsuarioID = ? AND Mes = ? AND Anio = ?)
                    BEGIN
                        UPDATE NovedadesNomina SET Pagado = ? WHERE UsuarioID = ? AND Mes = ? AND Anio = ?
                    END
                    ELSE
                    BEGIN
                        INSERT INTO NovedadesNomina (UsuarioID, Mes, Anio, Pagado)
                        VALUES (?, ?, ?, ?)
                    END
                """, (uid, mes, anio, pagado_val, uid, mes, anio, uid, mes, anio, pagado_val))
        else:
            if not usuario_id:
                conn.close()
                return jsonify({'success': False, 'message': 'ID de colaborador requerido'}), 400
            uid = int(usuario_id)
            cursor.execute("""
                IF EXISTS (SELECT 1 FROM NovedadesNomina WHERE UsuarioID = ? AND Mes = ? AND Anio = ?)
                BEGIN
                    UPDATE NovedadesNomina SET Pagado = ? WHERE UsuarioID = ? AND Mes = ? AND Anio = ?
                END
                ELSE
                BEGIN
                    INSERT INTO NovedadesNomina (UsuarioID, Mes, Anio, Pagado)
                    VALUES (?, ?, ?, ?)
                END
            """, (uid, mes, anio, pagado_val, uid, mes, anio, uid, mes, anio, pagado_val))

        # Invalidar reportes contables cacheados para recalcular Estado de Resultados y Balance de inmediato
        cursor.execute("DELETE FROM ReportesContables WHERE Mes = ? AND Anio = ?", (mes, anio))
        conn.commit()
        conn.close()

        # Obtener los totales recalculados en tiempo real
        nuevos_datos = obtener_totales_nomina_mes(mes, anio)
        emp_actualizado = None
        if not todos and usuario_id:
            for e in nuevos_datos['todos']:
                if e['id'] == int(usuario_id):
                    emp_actualizado = e
                    break

        return jsonify({
            'success': True,
            'pagado': bool(pagado_val),
            'todos': bool(todos),
            'usuario_id': usuario_id,
            'empleado': emp_actualizado,
            'totales': nuevos_datos['totales'],
            'totales_permanentes': nuevos_datos['totales_permanentes'],
            'totales_asesores': nuevos_datos['totales_asesores'],
            'resumen_dgi': nuevos_datos['resumen_dgi'],
            'planilla': nuevos_datos['todos']
        })
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Error al procesar pago: {e}'}), 500



# ==============================================================================
# SUBMÓDULO 1.2: API OBTENER INFORMACIÓN DE AJUSTE / EDICIÓN DE NÓMINA (JSON)
# ==============================================================================
@planilla_bp.route('/admin/planilla/ajuste_info/<int:id>')
@admin_required
def ajuste_info(id):
    if id == 1:
        return jsonify({'error': 'El creador y administrador del sistema no forma parte de la nómina laboral.'}), 400

    mes = request.args.get('mes', type=int) or datetime.datetime.now().month
    anio = request.args.get('anio', type=int) or datetime.datetime.now().year

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT U.UsuarioID, U.NombreCompleto, R.NombreRol, U.SalarioBase, U.MesesAcumulados,
               C.Cargo, C.Departamento, C.CedulaIdentidad, C.NumeroContrato
        FROM Usuarios U
        JOIN Roles R ON U.RolID = R.RolID
        LEFT JOIN ContratosLaborales C ON U.UsuarioID = C.UsuarioID
        WHERE U.UsuarioID = ? AND U.Activo = 1
    """, (id,))
    emp = cursor.fetchone()

    if not emp:
        conn.close()
        return jsonify({'error': 'Colaborador no encontrado'}), 404

    cursor.execute("""
        SELECT DiasFaltados, DeduccionFaltas, OtrasDeducciones, MotivoDeduccion,
               BonosExtras, MotivoBono, VehiculosAtendidos, BonoVehiculos, TasaBonoVehiculo
        FROM NovedadesNomina
        WHERE UsuarioID = ? AND Mes = ? AND Anio = ?
    """, (id, mes, anio))
    nov = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE MecanicoID = ?", (id,))
    vehiculos_ordenes = cursor.fetchone()[0] or 0
    conn.close()

    cargo = emp[5] or emp[2]
    rol = emp[2]
    is_mecanico = ('Mecánico' in rol) or ('Mecánico' in cargo)
    salario_base = float(emp[3] or 0.0)

    if nov:
        dias_faltados = int(nov[0] or 0)
        deduccion_faltas = float(nov[1] or 0.0)
        otras_deducciones = float(nov[2] or 0.0)
        motivo_deduccion = nov[3] or ''
        bonos_extras = float(nov[4] or 0.0)
        motivo_bono = nov[5] or ''
        vehiculos_atendidos = int(nov[6] or 0)
        bono_vehiculos = float(nov[7] or 0.0)
        tasa_bono_vehiculo = float(nov[8] or 500.0)
    else:
        dias_faltados = 0
        deduccion_faltas = 0.0
        otras_deducciones = 0.0
        motivo_deduccion = ''
        bonos_extras = 0.0
        motivo_bono = ''
        vehiculos_atendidos = vehiculos_ordenes if is_mecanico else 0
        tasa_bono_vehiculo = 500.0
        bono_vehiculos = (vehiculos_atendidos // 5) * tasa_bono_vehiculo

    total_bonos = round(bonos_extras + bono_vehiculos, 2)
    total_deducciones = round(deduccion_faltas + otras_deducciones, 2)
    salario_bruto = round(max(0.0, salario_base + total_bonos - total_deducciones), 2)
    calc = calcular_desglose_laboral_y_dgi(salario_bruto, emp[4] or 0)

    return jsonify({
        'usuario_id': emp[0],
        'nombre': emp[1],
        'rol': emp[2],
        'cargo': cargo,
        'departamento': emp[6] or 'Operaciones',
        'cedula': emp[7] or 'N/D',
        'num_contrato': emp[8] or f"CTR-TCR-{emp[0]:03d}",
        'salario_base': salario_base,
        'salario_diario': round(salario_base / 30.0, 2),
        'es_mecanico': is_mecanico,
        'mes': mes,
        'anio': anio,
        'dias_faltados': dias_faltados,
        'deduccion_faltas': deduccion_faltas,
        'otras_deducciones': otras_deducciones,
        'motivo_deduccion': motivo_deduccion,
        'bonos_extras': bonos_extras,
        'motivo_bono': motivo_bono,
        'vehiculos_atendidos': vehiculos_atendidos,
        'tasa_bono_vehiculo': tasa_bono_vehiculo,
        'bono_vehiculos': bono_vehiculos,
        'total_bonos': total_bonos,
        'total_deducciones': total_deducciones,
        'salario_bruto': salario_bruto,
        'inss_laboral': calc['inss_laboral'],
        'ir_mensual': calc['ir_mensual'],
        'salario_neto': calc['salario_neto'],
        'inss_patronal': calc['inss_patronal'],
        'inatec': calc['inatec'],
        'costo_total_empleador': calc['costo_total_empleador']
    })

# ==============================================================================
# SUBMÓDULO 1.3: GUARDAR AJUSTES DE NÓMINA (SALARIO BASE, FALTAS, BONOS Y MECÁNICOS)
# ==============================================================================
@planilla_bp.route('/admin/planilla/guardar_ajuste', methods=['POST'])
@admin_required
def guardar_ajuste():
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    usuario_id = int(data.get('usuario_id', 0))
    if usuario_id == 1:
        msg = 'El creador y administrador del sistema no forma parte de la nómina laboral.'
        if is_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('planilla.index'))

    now = datetime.datetime.now()
    mes = int(data.get('mes', now.month))
    anio = int(data.get('anio', now.year))

    try:
        salario_base = float(data.get('salario_base', 0.0))
        dias_faltados = int(data.get('dias_faltados', 0))
        otras_deducciones = float(data.get('otras_deducciones', 0.0))
        motivo_deduccion = str(data.get('motivo_deduccion', '')).strip()
        bonos_extras = float(data.get('bonos_extras', 0.0))
        motivo_bono = str(data.get('motivo_bono', '')).strip()
        vehiculos_atendidos = int(data.get('vehiculos_atendidos', 0))
        tasa_bono_vehiculo = float(data.get('tasa_bono_vehiculo', 500.0))
    except (ValueError, TypeError) as e:
        msg = f'Datos numéricos inválidos: {e}'
        if is_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('planilla.index'))

    # Deducción matemática de faltas: (Salario Base / 30) * Días Faltados
    deduccion_faltas = round((salario_base / 30.0) * dias_faltados, 2)

    # Bono para mecánicos por cada 5 vehículos atendidos
    bono_vehiculos = round((vehiculos_atendidos // 5) * tasa_bono_vehiculo, 2)

    conn = get_db_connection()
    if not conn:
        msg = 'Error de conexión a la base de datos.'
        if is_json:
            return jsonify({'success': False, 'message': msg}), 500
        flash(msg, 'error')
        return redirect(url_for('planilla.index'))

    try:
        cursor = conn.cursor()

        # Actualizar Salario Base pactado en Usuarios y ContratosLaborales si fue modificado
        cursor.execute("UPDATE Usuarios SET SalarioBase = ? WHERE UsuarioID = ?", (salario_base, usuario_id))
        cursor.execute("UPDATE ContratosLaborales SET SalarioPactado = ? WHERE UsuarioID = ?", (salario_base, usuario_id))

        # Registrar o actualizar la novedad del mes en NovedadesNomina
        cursor.execute("""
            IF EXISTS (SELECT 1 FROM NovedadesNomina WHERE UsuarioID = ? AND Mes = ? AND Anio = ?)
            BEGIN
                UPDATE NovedadesNomina
                SET DiasFaltados = ?, DeduccionFaltas = ?, OtrasDeducciones = ?, MotivoDeduccion = ?,
                    BonosExtras = ?, MotivoBono = ?, VehiculosAtendidos = ?, BonoVehiculos = ?,
                    TasaBonoVehiculo = ?, FechaRegistro = GETDATE()
                WHERE UsuarioID = ? AND Mes = ? AND Anio = ?
            END
            ELSE
            BEGIN
                INSERT INTO NovedadesNomina (
                    UsuarioID, Mes, Anio, DiasFaltados, DeduccionFaltas, OtrasDeducciones, MotivoDeduccion,
                    BonosExtras, MotivoBono, VehiculosAtendidos, BonoVehiculos, TasaBonoVehiculo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            END
        """, (
            usuario_id, mes, anio,
            dias_faltados, deduccion_faltas, otras_deducciones, motivo_deduccion,
            bonos_extras, motivo_bono, vehiculos_atendidos, bono_vehiculos, tasa_bono_vehiculo,
            usuario_id, mes, anio,
            usuario_id, mes, anio, dias_faltados, deduccion_faltas, otras_deducciones, motivo_deduccion,
            bonos_extras, motivo_bono, vehiculos_atendidos, bono_vehiculos, tasa_bono_vehiculo
        ))

        conn.commit()
        conn.close()

        msg = f"Ajustes de nómina guardados exitosamente. El salario neto y los estados financieros se han actualizado en tiempo real."
        if is_json:
            return jsonify({'success': True, 'message': msg})
        flash(msg, 'success')
        return redirect(url_for('planilla.index', mes=mes, anio=anio))

    except Exception as e:
        conn.rollback()
        conn.close()
        msg = f"Error al guardar ajustes de nómina: {e}"
        if is_json:
            return jsonify({'success': False, 'message': msg}), 500
        flash(msg, 'error')
        return redirect(url_for('planilla.index', mes=mes, anio=anio))

# ==============================================================================
# SUBMÓDULO 1.4: COLILLA DE PAGO INDIVIDUAL
# ==============================================================================
@planilla_bp.route('/admin/planilla/colilla/<int:id>')
@admin_required
def colilla(id):
    if id == 1:
        flash("El creador del sistema no forma parte de la nómina laboral ni emite colilla.", "warning")
        return redirect(url_for('planilla.index'))

    mes = request.args.get('mes', type=int) or datetime.datetime.now().month
    anio = request.args.get('anio', type=int) or datetime.datetime.now().year

    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('planilla.index'))
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT U.UsuarioID, U.NombreCompleto, R.NombreRol, U.SalarioBase, U.MesesAcumulados, U.Email,
               C.NumeroContrato, C.Cargo, C.Departamento, C.CedulaIdentidad, C.FechaInicio, C.Jornada,
               C.TipoContrato, C.Horario
        FROM Usuarios U
        JOIN Roles R ON U.RolID = R.RolID
        LEFT JOIN ContratosLaborales C ON U.UsuarioID = C.UsuarioID
        WHERE U.UsuarioID = ? AND U.Activo = 1 AND U.UsuarioID != 1
    """, (id,))
    
    emp = cursor.fetchone()
    if not emp:
        conn.close()
        flash("Empleado no encontrado o inactivo en nómina.", "error")
        return redirect(url_for('planilla.index'))

    cursor.execute("""
        SELECT DiasFaltados, DeduccionFaltas, OtrasDeducciones, MotivoDeduccion,
               BonosExtras, MotivoBono, VehiculosAtendidos, BonoVehiculos, TasaBonoVehiculo, Pagado
        FROM NovedadesNomina
        WHERE UsuarioID = ? AND Mes = ? AND Anio = ?
    """, (id, mes, anio))
    nov = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE MecanicoID = ?", (id,))
    vehiculos_ordenes = cursor.fetchone()[0] or 0
    conn.close()

    salario_base = float(emp[3]) if emp[3] else 0.0
    meses_acumulados = int(emp[4]) if emp[4] else 0
    email = emp[5]
    cargo_contrato = emp[7] or emp[2]
    rol = emp[2]
    tipo_contrato = emp[12]
    horario = emp[13] or '8:00 AM - 5:00 PM'

    is_asesor = (email in ('carlos.finanzas', 'martha.estadistica')) or ('Asesor' in (cargo_contrato or '')) or ('Asesoría' in (tipo_contrato or ''))
    is_mecanico = ('Mecánico' in rol) or ('Mecánico' in (cargo_contrato or ''))

    pagado = bool(nov[9]) if (nov and len(nov) > 9 and nov[9] is not None) else False

    if nov:
        dias_faltados = int(nov[0] or 0)
        deduccion_faltas = float(nov[1] or 0.0)
        otras_deducciones = float(nov[2] or 0.0)
        motivo_deduccion = nov[3] or ''
        bonos_extras = float(nov[4] or 0.0)
        motivo_bono = nov[5] or ''
        vehiculos_atendidos = int(nov[6] or 0)
        bono_vehiculos = float(nov[7] or 0.0)
        tasa_bono_vehiculo = float(nov[8] or 500.0)
    else:
        dias_faltados = 0
        deduccion_faltas = 0.0
        otras_deducciones = 0.0
        motivo_deduccion = ''
        bonos_extras = 0.0
        motivo_bono = ''
        vehiculos_atendidos = vehiculos_ordenes if is_mecanico else 0
        tasa_bono_vehiculo = 500.0
        bono_vehiculos = (vehiculos_atendidos // 5) * tasa_bono_vehiculo

    dias_trabajados = max(0, 30 - dias_faltados)
    porcentaje_asistencia = round((dias_trabajados / 30.0) * 100.0, 1)

    total_bonos = round(bonos_extras + bono_vehiculos, 2)
    total_deducciones = round(deduccion_faltas + otras_deducciones, 2)
    salario_bruto_potencial = round(max(0.0, salario_base + total_bonos - total_deducciones), 2)

    calc = calcular_desglose_laboral_y_dgi(salario_bruto_potencial, meses_acumulados)
    mes_actual_str = datetime.date(anio, mes, 1).strftime('%B %Y').capitalize()

    # Si NO está pagado, todos los importes en colilla se fijan en C$ 0.00
    if not pagado:
        salario_base_display = 0.0
        salario_bruto_display = 0.0
        inss_laboral_display = 0.0
        base_imponible_display = 0.0
        renta_anual_display = 0.0
        tramo_dgi_display = 1
        tasa_dgi_display = 0
        ir_display = 0.0
        salario_neto_display = 0.0
        aguinaldo_display = 0.0
        vacaciones_display = 0.0
        indemnizacion_display = 0.0
        inss_patronal_display = 0.0
        inatec_display = 0.0
        costo_total_display = 0.0
        bono_vehiculos_display = 0.0
        bonos_extras_display = 0.0
        deduccion_faltas_display = 0.0
        otras_deducciones_display = 0.0
        total_bonos_display = 0.0
        total_deducciones_display = 0.0
    else:
        salario_base_display = salario_base
        salario_bruto_display = calc['salario_bruto']
        inss_laboral_display = calc['inss_laboral']
        base_imponible_display = calc['base_imponible_mensual']
        renta_anual_display = calc['renta_anual_proyectada']
        tramo_dgi_display = calc['tramo_dgi']
        tasa_dgi_display = calc['tasa_dgi']
        ir_display = calc['ir_mensual']
        salario_neto_display = calc['salario_neto']
        aguinaldo_display = calc['aguinaldo']
        vacaciones_display = calc['vacaciones']
        indemnizacion_display = calc['indemnizacion']
        inss_patronal_display = calc['inss_patronal']
        inatec_display = calc['inatec']
        costo_total_display = calc['costo_total_empleador']
        bono_vehiculos_display = bono_vehiculos
        bonos_extras_display = bonos_extras
        deduccion_faltas_display = deduccion_faltas
        otras_deducciones_display = otras_deducciones
        total_bonos_display = total_bonos
        total_deducciones_display = total_deducciones
    
    data = {
        'id': emp[0],
        'nombre': emp[1],
        'rol': emp[2],
        'email': email,
        'num_contrato': emp[6] or f"CTR-TCR-{emp[0]:03d}",
        'cargo': cargo_contrato,
        'depto': emp[8] or 'Operaciones',
        'cedula': emp[9] or 'N/D',
        'fecha_ingreso': emp[10].strftime('%d/%m/%Y') if emp[10] else 'N/D',
        'jornada': emp[11] or ('Periódica Mensual (1 día al mes - Cierre)' if is_asesor else 'Diurna Ordinaria (48 hrs)'),
        'tipo_contrato': tipo_contrato or ('Asesoría Externa / Cierre Mensual' if is_asesor else 'Tiempo Indeterminado'),
        'horario': horario,
        'es_asesor': is_asesor,
        'es_mecanico': is_mecanico,
        'categoria_codigo': 'asesor' if is_asesor else 'permanente',
        'categoria_nombre': 'Asesor Externo de Cierre Mensual' if is_asesor else 'Personal Permanente de Planta',
        'modalidad': '1 Día al Mes (Cierre Contable - Pago Único)' if is_asesor else 'Presencial Diario (Lunes a Sábado)',
        'tipo_pago_label': 'Honorarios por Cierre Mensual (1 Día/Mes)' if is_asesor else 'Salario Base Ordinario Mensual',
        'mes_periodo': mes_actual_str,
        'pagado': pagado,
        'dias_trabajados': dias_trabajados,
        'porcentaje_asistencia': porcentaje_asistencia,
        'salario_base': salario_base_display,
        'calc_salario_base': salario_base,
        'dias_faltados': dias_faltados,
        'deduccion_faltas': deduccion_faltas_display,
        'otras_deducciones': otras_deducciones_display,
        'motivo_deduccion': motivo_deduccion,
        'bonos_extras': bonos_extras_display,
        'motivo_bono': motivo_bono,
        'vehiculos_atendidos': vehiculos_atendidos,
        'tasa_bono_vehiculo': tasa_bono_vehiculo,
        'bono_vehiculos': bono_vehiculos_display,
        'total_bonos': total_bonos_display,
        'total_deducciones_ajustes': total_deducciones_display,
        'salario_bruto': salario_bruto_display,
        'inss_laboral': inss_laboral_display,
        'base_imponible_mensual': base_imponible_display,
        'renta_anual_proyectada': renta_anual_display,
        'tramo_dgi': tramo_dgi_display,
        'tasa_dgi': tasa_dgi_display,
        'ir': ir_display,
        'salario_neto': salario_neto_display,
        'meses': meses_acumulados,
        'aguinaldo': aguinaldo_display,
        'vacaciones': vacaciones_display,
        'indemnizacion': indemnizacion_display,
        'inss_patronal': inss_patronal_display,
        'inatec': inatec_display,
        'costo_total_empleador': costo_total_display,
        # Cálculos potenciales para auditoría o previa
        'calc_salario_bruto': calc['salario_bruto'],
        'calc_inss_laboral': calc['inss_laboral'],
        'calc_base_imponible_mensual': calc['base_imponible_mensual'],
        'calc_renta_anual_proyectada': calc['renta_anual_proyectada'],
        'calc_tramo_dgi': calc['tramo_dgi'],
        'calc_tasa_dgi': calc['tasa_dgi'],
        'calc_ir': calc['ir_mensual'],
        'calc_salario_neto': calc['salario_neto'],
        'calc_costo_total_empleador': calc['costo_total_empleador']
    }
    
    return render_template('admin/colilla.html', data=data)

# ==============================================================================
# SUBMÓDULO 2: CONTRATOS LABORALES DE CADA TRABAJADOR (LEY N° 185)
# ==============================================================================
@planilla_bp.route('/admin/contratos')
@admin_required
def contratos():
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('index'))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.ContratoID, C.NumeroContrato, U.UsuarioID, U.NombreCompleto, R.NombreRol,
               C.Cargo, C.Departamento, C.TipoContrato, C.FechaInicio, C.FechaFin,
               C.SalarioPactado, C.Jornada, C.CedulaIdentidad, C.EstadoContrato,
               C.TelefonoContacto, C.DireccionDomicilio, U.MesesAcumulados, U.Email, C.Horario
        FROM ContratosLaborales C
        JOIN Usuarios U ON C.UsuarioID = U.UsuarioID
        JOIN Roles R ON U.RolID = R.RolID
        WHERE U.Activo = 1 AND U.UsuarioID != 1 AND U.Email NOT IN ('carlos.contabilidad', 'elvin.admin')
        ORDER BY C.ContratoID ASC
    """)
    rows = cursor.fetchall()

    contratos_lista = []
    contratos_permanentes = []
    contratos_asesores = []
    total_salarios = 0.0
    nomina_permanentes = 0.0
    nomina_asesores = 0.0
    vigentes_count = 0

    for r in rows:
        salario = float(r[10]) if r[10] else 0.0
        total_salarios += salario
        estado = r[13] or 'Vigente'
        if estado == 'Vigente':
            vigentes_count += 1

        email = r[17]
        cargo = r[5]
        tipo_contrato = r[7]
        is_asesor = (email in ('carlos.finanzas', 'martha.estadistica')) or ('Asesor' in (cargo or '')) or ('Asesoría' in (tipo_contrato or ''))

        calc = calcular_desglose_laboral_y_dgi(salario, r[16] or 0)

        contrato_item = {
            'contrato_id': r[0],
            'numero_contrato': r[1],
            'usuario_id': r[2],
            'nombre': r[3],
            'rol': r[4],
            'cargo': cargo,
            'departamento': r[6],
            'tipo_contrato': tipo_contrato,
            'fecha_inicio': r[8].strftime('%d/%m/%Y') if r[8] else 'N/D',
            'fecha_inicio_iso': r[8].strftime('%Y-%m-%d') if r[8] else '2026-01-01',
            'fecha_fin': r[9].strftime('%d/%m/%Y') if r[9] else 'Indefinido',
            'salario_pactado': salario,
            'jornada': r[11],
            'horario': r[18] or '8:00 AM - 5:00 PM',
            'cedula': r[12],
            'estado': estado,
            'telefono': r[14] or 'N/D',
            'domicilio': r[15] or 'Managua',
            'email': email,
            'es_asesor': is_asesor,
            'categoria_codigo': 'asesor' if is_asesor else 'permanente',
            'categoria_nombre': 'Asesoría de Cierre' if is_asesor else 'Planta Permanente',
            'modalidad': '1 Día al Mes (Cierre Mensual - Pago Único)' if is_asesor else 'Presencial Diario (Lunes a Sábado)',
            'inss_laboral': calc['inss_laboral'],
            'ir_mensual': calc['ir_mensual'],
            'salario_neto': calc['salario_neto']
        }

        contratos_lista.append(contrato_item)
        if is_asesor:
            contratos_asesores.append(contrato_item)
            nomina_asesores += salario
        else:
            contratos_permanentes.append(contrato_item)
            nomina_permanentes += salario

    # Lista de usuarios activos para el modal de nuevo contrato (excluye al creador Elvin Alexander)
    cursor.execute("""
        SELECT U.UsuarioID, U.NombreCompleto, R.NombreRol, U.SalarioBase
        FROM Usuarios U
        JOIN Roles R ON U.RolID = R.RolID
        WHERE U.Activo = 1 AND U.UsuarioID != 1 AND U.Email NOT IN ('carlos.contabilidad', 'elvin.admin')
        ORDER BY U.NombreCompleto ASC
    """)
    usuarios_activos = cursor.fetchall()
    conn.close()

    resumen = {
        'total_contratos': len(contratos_lista),
        'vigentes': vigentes_count,
        'total_nomina': total_salarios,
        'salario_promedio': round(total_salarios / len(contratos_lista), 2) if contratos_lista else 0.0,
        'total_permanentes': len(contratos_permanentes),
        'nomina_permanentes': nomina_permanentes,
        'total_asesores': len(contratos_asesores),
        'nomina_asesores': nomina_asesores
    }

    return render_template(
        'admin/contratos.html',
        contratos=contratos_lista,
        contratos_permanentes=contratos_permanentes,
        contratos_asesores=contratos_asesores,
        resumen=resumen,
        usuarios_activos=usuarios_activos,
        tabla_dgi=TABLA_DGI_LEY_822
    )

# ==============================================================================
# SUBMÓDULO 2.1: VER CONTRATO FORMAL INDIVIDUAL (LEY N° 185)
# ==============================================================================
@planilla_bp.route('/admin/contratos/ver/<int:id>')
@admin_required
def ver_contrato(id):
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('planilla.contratos'))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.ContratoID, C.NumeroContrato, U.UsuarioID, U.NombreCompleto, R.NombreRol,
               C.Cargo, C.Departamento, C.TipoContrato, C.FechaInicio, C.FechaFin,
               C.SalarioPactado, C.Jornada, C.Horario, C.PeriodoPruebaDias,
               C.LugarTrabajo, C.CedulaIdentidad, C.DireccionDomicilio, C.TelefonoContacto,
               C.EstadoContrato, C.ClausulasAdicionales, C.FechaRegistro, U.MesesAcumulados
        FROM ContratosLaborales C
        JOIN Usuarios U ON C.UsuarioID = U.UsuarioID
        JOIN Roles R ON U.RolID = R.RolID
        WHERE C.ContratoID = ?
    """, (id,))
    c = cursor.fetchone()
    conn.close()

    if not c:
        flash("Contrato no encontrado.", "error")
        return redirect(url_for('planilla.contratos'))

    salario = float(c[10]) if c[10] else 0.0
    calc = calcular_desglose_laboral_y_dgi(salario, c[21] or 0)

    contrato = {
        'contrato_id': c[0],
        'numero_contrato': c[1],
        'usuario_id': c[2],
        'nombre_trabajador': c[3],
        'rol': c[4],
        'cargo': c[5],
        'departamento': c[6],
        'tipo_contrato': c[7],
        'fecha_inicio': c[8].strftime('%d de %B de %Y') if c[8] else 'N/D',
        'fecha_inicio_iso': c[8].strftime('%Y-%m-%d') if c[8] else '',
        'fecha_fin': c[9].strftime('%d de %B de %Y') if c[9] else 'Indefinido',
        'fecha_fin_iso': c[9].strftime('%Y-%m-%d') if c[9] else '',
        'salario_pactado': salario,
        'jornada': c[11],
        'horario': c[12],
        'periodo_prueba_dias': c[13] or 30,
        'lugar_trabajo': c[14] or 'Instalaciones de Taller y Lubricantes CR, Managua',
        'cedula': c[15],
        'domicilio': c[16] or 'Managua, Nicaragua',
        'telefono': c[17] or 'N/D',
        'estado': c[18] or 'Vigente',
        'clausulas_adicionales': c[19] or '',
        'fecha_registro': c[20].strftime('%d/%m/%Y') if c[20] else 'N/D',
        # Cálculos de deducciones conforme a Ley 185 y DGI
        'inss_laboral': calc['inss_laboral'],
        'base_imponible_ir': calc['base_imponible_mensual'],
        'renta_anual_proyectada': calc['renta_anual_proyectada'],
        'tramo_dgi': calc['tramo_dgi'],
        'tasa_dgi': calc['tasa_dgi'],
        'ir_mensual': calc['ir_mensual'],
        'salario_neto': calc['salario_neto'],
        'inss_patronal': calc['inss_patronal'],
        'inatec': calc['inatec']
    }

    return render_template('admin/contrato_detalle.html', c=contrato, tabla_dgi=TABLA_DGI_LEY_822)

# ==============================================================================
# SUBMÓDULO 2.2: IMPRESIÓN OFICIAL DEL CONTRATO (FORMATO LEY 185)
# ==============================================================================
@planilla_bp.route('/admin/contratos/imprimir/<int:id>')
@admin_required
def imprimir_contrato(id):
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('planilla.contratos'))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.ContratoID, C.NumeroContrato, U.UsuarioID, U.NombreCompleto, R.NombreRol,
               C.Cargo, C.Departamento, C.TipoContrato, C.FechaInicio, C.FechaFin,
               C.SalarioPactado, C.Jornada, C.Horario, C.PeriodoPruebaDias,
               C.LugarTrabajo, C.CedulaIdentidad, C.DireccionDomicilio, C.TelefonoContacto,
               C.EstadoContrato, C.ClausulasAdicionales, C.FechaRegistro, U.MesesAcumulados
        FROM ContratosLaborales C
        JOIN Usuarios U ON C.UsuarioID = U.UsuarioID
        JOIN Roles R ON U.RolID = R.RolID
        WHERE C.ContratoID = ?
    """, (id,))
    c = cursor.fetchone()
    conn.close()

    if not c:
        flash("Contrato no encontrado.", "error")
        return redirect(url_for('planilla.contratos'))

    salario = float(c[10]) if c[10] else 0.0
    calc = calcular_desglose_laboral_y_dgi(salario, c[21] or 0)

    contrato = {
        'contrato_id': c[0],
        'numero_contrato': c[1],
        'usuario_id': c[2],
        'nombre_trabajador': c[3],
        'rol': c[4],
        'cargo': c[5],
        'departamento': c[6],
        'tipo_contrato': c[7],
        'fecha_inicio': c[8].strftime('%d de %B de %Y') if c[8] else 'N/D',
        'fecha_fin': c[9].strftime('%d de %B de %Y') if c[9] else 'Tiempo Indeterminado',
        'salario_pactado': salario,
        'jornada': c[11],
        'horario': c[12],
        'periodo_prueba_dias': c[13] or 30,
        'lugar_trabajo': c[14] or 'Instalaciones de Taller y Lubricantes CR, Managua',
        'cedula': c[15],
        'domicilio': c[16] or 'Managua, Nicaragua',
        'telefono': c[17] or 'N/D',
        'estado': c[18] or 'Vigente',
        'clausulas_adicionales': c[19] or '',
        'fecha_registro': c[20].strftime('%d/%m/%Y') if c[20] else 'N/D',
        'inss_laboral': calc['inss_laboral'],
        'ir_mensual': calc['ir_mensual'],
        'salario_neto': calc['salario_neto']
    }

    return render_template('admin/contrato_impresion.html', c=contrato)

# ==============================================================================
# SUBMÓDULO 2.3: EDITAR / ACTUALIZAR CONTRATO LABORAL
# ==============================================================================
@planilla_bp.route('/admin/contratos/editar/<int:id>', methods=['POST'])
@admin_required
def editar_contrato(id):
    cargo = request.form.get('cargo', '')
    departamento = request.form.get('departamento', '')
    tipo_contrato = request.form.get('tipo_contrato', 'Tiempo Indeterminado')
    jornada = request.form.get('jornada', '')
    horario = request.form.get('horario', '')
    salario_str = request.form.get('salario_pactado', '0')
    fecha_inicio = request.form.get('fecha_inicio', '')
    cedula = request.form.get('cedula', '')
    domicilio = request.form.get('domicilio', '')
    telefono = request.form.get('telefono', '')
    estado = request.form.get('estado', 'Vigente')
    clausulas = request.form.get('clausulas', '').strip()

    errores, datos = _validar_datos_rrhh(
        cedula=cedula,
        telefono=telefono,
        domicilio=domicilio,
        cargo=cargo,
        requerir_cargo=True,
        departamento=departamento,
        requerir_departamento=True,
        salario_raw=salario_str,
        fecha_inicio_raw=fecha_inicio,
        requerir_fecha=True,
        jornada=jornada,
        horario=horario,
        requerir_jornada_horario=True,
        tipo_contrato=tipo_contrato,
        estado=estado,
    )
    if errores:
        flash(' • '.join(errores), 'error')
        return redirect(url_for('planilla.contratos'))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT TOP 1 ContratoID FROM ContratosLaborales WHERE UPPER(CedulaIdentidad) = UPPER(?) AND ContratoID <> ?",
                (datos['cedula'], id),
            )
            if cursor.fetchone():
                flash(f"La cédula {datos['cedula']} ya pertenece a otro contrato registrado.", 'error')
                return redirect(url_for('planilla.contratos'))

            cursor.execute("""
                UPDATE ContratosLaborales
                SET Cargo = ?, Departamento = ?, TipoContrato = ?, Jornada = ?, Horario = ?,
                    SalarioPactado = ?, CedulaIdentidad = ?, DireccionDomicilio = ?, 
                    TelefonoContacto = ?, EstadoContrato = ?, ClausulasAdicionales = ?,
                    FechaInicio = ?
                WHERE ContratoID = ?
            """, (
                datos['cargo'], datos['departamento'], tipo_contrato, datos['jornada'], datos['horario'],
                datos['salario'], datos['cedula'], datos['domicilio'], datos['telefono'], estado, clausulas,
                datos['fecha_inicio'], id
            ))
            cursor.execute("""
                UPDATE Usuarios
                SET SalarioBase = ?
                WHERE UsuarioID = (SELECT UsuarioID FROM ContratosLaborales WHERE ContratoID = ?)
            """, (datos['salario'], id))
            conn.commit()
            flash("Contrato laboral actualizado exitosamente.", "success")
        except Exception:
            conn.rollback()
            flash("No se pudo actualizar el contrato. Verifica los campos ingresados.", "error")
        finally:
            conn.close()

    return redirect(url_for('planilla.contratos'))

# ==============================================================================
# SUBMÓDULO 2.4: REGISTRAR NUEVO CONTRATO LABORAL
# ==============================================================================
@planilla_bp.route('/admin/contratos/nuevo', methods=['POST'])
@admin_required
def nuevo_contrato():
    try:
        usuario_id = int(request.form.get('usuario_id', '0'))
    except ValueError:
        usuario_id = 0
    cargo = request.form.get('cargo', '')
    departamento = request.form.get('departamento', '')
    tipo_contrato = request.form.get('tipo_contrato', 'Tiempo Indeterminado')
    fecha_inicio = request.form.get('fecha_inicio', datetime.date.today().strftime('%Y-%m-%d'))
    jornada = request.form.get('jornada', 'Diurna Ordinaria (48 hrs semanales)')
    horario = request.form.get('horario', 'Lunes a Viernes: 8:00 AM - 5:00 PM, Sábado: 8:00 AM - 12:00 MD')
    salario_str = request.form.get('salario_pactado', '0')
    cedula = request.form.get('cedula', '')
    domicilio = request.form.get('domicilio', '')
    telefono = request.form.get('telefono', '')

    if usuario_id <= 0:
        flash("Debe seleccionar un colaborador válido para formalizar el contrato.", "error")
        return redirect(url_for('planilla.contratos'))

    errores, datos = _validar_datos_rrhh(
        cedula=cedula,
        telefono=telefono,
        domicilio=domicilio,
        cargo=cargo,
        requerir_cargo=True,
        departamento=departamento,
        requerir_departamento=True,
        salario_raw=salario_str,
        fecha_inicio_raw=fecha_inicio,
        requerir_fecha=True,
        jornada=jornada,
        horario=horario,
        requerir_jornada_horario=True,
        tipo_contrato=tipo_contrato,
    )
    if errores:
        flash(' • '.join(errores), 'error')
        return redirect(url_for('planilla.contratos'))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 1 UsuarioID FROM Usuarios WHERE UsuarioID = ?", (usuario_id,))
            if not cursor.fetchone():
                flash("El colaborador seleccionado no existe.", "error")
                return redirect(url_for('planilla.contratos'))

            cursor.execute("SELECT TOP 1 ContratoID FROM ContratosLaborales WHERE UsuarioID = ?", (usuario_id,))
            if cursor.fetchone():
                flash("Este colaborador ya tiene un contrato registrado en el directorio.", "error")
                return redirect(url_for('planilla.contratos'))

            cursor.execute("SELECT TOP 1 ContratoID FROM ContratosLaborales WHERE UPPER(CedulaIdentidad) = UPPER(?)", (datos['cedula'],))
            if cursor.fetchone():
                flash(f"La cédula {datos['cedula']} ya está asignada a otro contrato.", "error")
                return redirect(url_for('planilla.contratos'))

            cursor.execute("SELECT ISNULL(MAX(ContratoID), 0) + 1 FROM ContratosLaborales")
            total = cursor.fetchone()[0]
            num_contrato = f"CTR-TCR-{datetime.date.today().year}-{total:03d}"

            cursor.execute("""
                INSERT INTO ContratosLaborales (
                    UsuarioID, NumeroContrato, TipoContrato, FechaInicio, Cargo, 
                    Departamento, Jornada, Horario, SalarioPactado, PeriodoPruebaDias, 
                    LugarTrabajo, CedulaIdentidad, DireccionDomicilio, TelefonoContacto, 
                    EstadoContrato, ClausulasAdicionales
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 30, 'Instalaciones de Taller y Lubricantes CR, Managua', ?, ?, ?, 'Vigente', ?)
            """, (
                usuario_id, num_contrato, tipo_contrato, datos['fecha_inicio'], datos['cargo'],
                datos['departamento'], datos['jornada'], datos['horario'], datos['salario'],
                datos['cedula'], datos['domicilio'], datos['telefono'],
                'Conforme a la Ley 185 (Código del Trabajo de Nicaragua), se garantizan todas las prestaciones sociales y se aplican las deducciones de INSS (7%) e IR de la DGI (Ley 822).'
            ))
            cursor.execute("UPDATE Usuarios SET SalarioBase = ? WHERE UsuarioID = ?", (datos['salario'], usuario_id))
            conn.commit()
            flash(f"Contrato #{num_contrato} registrado exitosamente.", "success")
        except Exception:
            conn.rollback()
            flash("No se pudo registrar el contrato. Verifica que los datos sean válidos.", "error")
        finally:
            conn.close()

    return redirect(url_for('planilla.contratos'))


# ==============================================================================
# SUBMÓDULO 3: REGISTRO MENSUAL Y CIERRES DE NÓMINA (LEY 185 / LEY 822)
# ==============================================================================
@planilla_bp.route('/admin/rrhh/registro_mensual')
@planilla_bp.route('/admin/planilla/registro_mensual')
@admin_required
def registro_mensual():
    now = datetime.datetime.now()
    mes = request.args.get('mes', type=int) or now.month
    anio = request.args.get('anio', type=int) or now.year

    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    conn = get_db_connection()
    cierre_actual = None
    historial_cierres = []

    if conn:
        try:
            cursor = conn.cursor()
            # Cierre del mes seleccionado
            cursor.execute("""
                SELECT CierreID, Mes, Anio, PeriodoTexto, FechaCierre, UsuarioCierreID,
                       UsuarioCierreNombre, TotalColaboradores, TotalPagados, TotalPendientes,
                       MasaSalarialBruta, TotalInssLaboral, TotalBaseImponibleIr, TotalIrDgi,
                       TotalSalarioNeto, TotalInssPatronal, TotalInatec, TotalCargasPatronales,
                       TotalProvisionesAcumuladas, CostoTotalEmpleador, Estado, Observaciones
                FROM CierresMensualesNomina
                WHERE Mes = ? AND Anio = ?
            """, (mes, anio))
            row = cursor.fetchone()
            if row:
                cierre_actual = {
                    'CierreID': row[0], 'Mes': row[1], 'Anio': row[2], 'PeriodoTexto': row[3],
                    'FechaCierre': row[4], 'UsuarioCierreID': row[5], 'UsuarioCierreNombre': row[6],
                    'TotalColaboradores': row[7], 'TotalPagados': row[8], 'TotalPendientes': row[9],
                    'MasaSalarialBruta': float(row[10] or 0), 'TotalInssLaboral': float(row[11] or 0),
                    'TotalBaseImponibleIr': float(row[12] or 0), 'TotalIrDgi': float(row[13] or 0),
                    'TotalSalarioNeto': float(row[14] or 0), 'TotalInssPatronal': float(row[15] or 0),
                    'TotalInatec': float(row[16] or 0), 'TotalCargasPatronales': float(row[17] or 0),
                    'TotalProvisionesAcumuladas': float(row[18] or 0), 'CostoTotalEmpleador': float(row[19] or 0),
                    'Estado': row[20], 'Observaciones': row[21]
                }

            # Historial de todos los cierres
            cursor.execute("""
                SELECT CierreID, Mes, Anio, PeriodoTexto, FechaCierre, UsuarioCierreID,
                       UsuarioCierreNombre, TotalColaboradores, TotalPagados, TotalPendientes,
                       MasaSalarialBruta, TotalInssLaboral, TotalBaseImponibleIr, TotalIrDgi,
                       TotalSalarioNeto, TotalInssPatronal, TotalInatec, TotalCargasPatronales,
                       TotalProvisionesAcumuladas, CostoTotalEmpleador, Estado, Observaciones
                FROM CierresMensualesNomina
                ORDER BY Anio DESC, Mes DESC
            """)
            for r in cursor.fetchall():
                historial_cierres.append({
                    'CierreID': r[0], 'Mes': r[1], 'Anio': r[2], 'PeriodoTexto': r[3],
                    'FechaCierre': r[4], 'UsuarioCierreID': r[5], 'UsuarioCierreNombre': r[6],
                    'TotalColaboradores': r[7], 'TotalPagados': r[8], 'TotalPendientes': r[9],
                    'MasaSalarialBruta': float(r[10] or 0), 'TotalInssLaboral': float(r[11] or 0),
                    'TotalBaseImponibleIr': float(r[12] or 0), 'TotalIrDgi': float(r[13] or 0),
                    'TotalSalarioNeto': float(r[14] or 0), 'TotalInssPatronal': float(r[15] or 0),
                    'TotalInatec': float(r[16] or 0), 'TotalCargasPatronales': float(r[17] or 0),
                    'TotalProvisionesAcumuladas': float(r[18] or 0), 'CostoTotalEmpleador': float(r[19] or 0),
                    'Estado': r[20], 'Observaciones': r[21]
                })
        except Exception as e:
            print("Error al consultar cierres:", e)
        finally:
            conn.close()

    resumen = obtener_totales_nomina_mes(mes, anio)
    totales_actuales = resumen['totales']

    return render_template('admin/registro_mensual.html',
                           mes_seleccionado=mes,
                           anio_seleccionado=anio,
                           meses_nombres=meses_nombres,
                           cierre_actual=cierre_actual,
                           historial_cierres=historial_cierres,
                           totales_actuales=totales_actuales)


@planilla_bp.route('/admin/rrhh/ejecutar_cierre', methods=['POST'])
@admin_required
def ejecutar_cierre_mensual():
    import json
    now = datetime.datetime.now()
    mes = request.form.get('mes', type=int) or now.month
    anio = request.form.get('anio', type=int) or now.year
    observaciones = request.form.get('observaciones', '').strip()

    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    periodo_texto = f"{meses_nombres[mes - 1]} {anio}"

    usuario_id = session.get('usuario_id')
    user_name = session.get('username') or 'Super Administrador'

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT NombreCompleto FROM Usuarios WHERE UsuarioID = ?", (usuario_id,))
        u_row = cursor.fetchone()
        if u_row and u_row[0]:
            user_name = u_row[0]

        # Obtener los totales exactos del mes
        datos = obtener_totales_nomina_mes(mes, anio)
        tot = datos['totales']
        todos_empleados = datos['todos']

        snapshot_json = json.dumps([{
            'id': e['id'], 'nombre': e['nombre'], 'cargo': e['cargo'],
            'pagado': e['pagado'], 'salario_base': e['salario_base'],
            'dias_trabajados': e['dias_trabajados'], 'salario_bruto': e['salario_bruto'],
            'inss_laboral': e['inss_laboral'], 'ir': e['ir'], 'salario_neto': e['salario_neto']
        } for e in todos_empleados])

        cursor.execute("""
            IF EXISTS (SELECT 1 FROM CierresMensualesNomina WHERE Mes = ? AND Anio = ?)
            BEGIN
                UPDATE CierresMensualesNomina
                SET PeriodoTexto = ?, FechaCierre = GETDATE(), UsuarioCierreID = ?,
                    UsuarioCierreNombre = ?, TotalColaboradores = 10,
                    TotalPagados = ?, TotalPendientes = ?, MasaSalarialBruta = ?,
                    TotalInssLaboral = ?, TotalBaseImponibleIr = ?, TotalIrDgi = ?,
                    TotalSalarioNeto = ?, TotalInssPatronal = ?, TotalInatec = ?,
                    TotalCargasPatronales = ?, TotalProvisionesAcumuladas = ?,
                    CostoTotalEmpleador = ?, Estado = 'CERRADO', Observaciones = ?,
                    DetalleSnapshotJson = ?
                WHERE Mes = ? AND Anio = ?
            END
            ELSE
            BEGIN
                INSERT INTO CierresMensualesNomina (
                    Mes, Anio, PeriodoTexto, FechaCierre, UsuarioCierreID, UsuarioCierreNombre,
                    TotalColaboradores, TotalPagados, TotalPendientes, MasaSalarialBruta,
                    TotalInssLaboral, TotalBaseImponibleIr, TotalIrDgi, TotalSalarioNeto,
                    TotalInssPatronal, TotalInatec, TotalCargasPatronales,
                    TotalProvisionesAcumuladas, CostoTotalEmpleador, Estado, Observaciones,
                    DetalleSnapshotJson
                )
                VALUES (?, ?, ?, GETDATE(), ?, ?, 10, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CERRADO', ?, ?)
            END
        """, (
            mes, anio,
            periodo_texto, usuario_id, user_name, tot.get('cantidad_pagados', 0), tot.get('cantidad_pendientes', 0),
            tot.get('salario_bruto', 0.0), tot.get('inss_laboral', 0.0), tot.get('base_imponible_ir', 0.0),
            tot.get('ir', 0.0), tot.get('salario_neto', 0.0), tot.get('inss_patronal', 0.0), tot.get('inatec', 0.0),
            tot.get('cargas_patronales', 0.0), tot.get('provisiones_acumuladas', 0.0),
            tot.get('costo_total_empleador', 0.0), observaciones, snapshot_json,
            mes, anio,
            mes, anio, periodo_texto, usuario_id, user_name,
            tot.get('cantidad_pagados', 0), tot.get('cantidad_pendientes', 0),
            tot.get('salario_bruto', 0.0), tot.get('inss_laboral', 0.0), tot.get('base_imponible_ir', 0.0),
            tot.get('ir', 0.0), tot.get('salario_neto', 0.0), tot.get('inss_patronal', 0.0), tot.get('inatec', 0.0),
            tot.get('cargas_patronales', 0.0), tot.get('provisiones_acumuladas', 0.0),
            tot.get('costo_total_empleador', 0.0), observaciones, snapshot_json
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Cierre contable de {periodo_texto} ejecutado con éxito. Se ha emitido el acta oficial.'
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Error al registrar cierre: {str(e)}'}), 500


@planilla_bp.route('/admin/rrhh/reabrir_cierre/<int:cierre_id>', methods=['POST'])
@admin_required
def reabrir_cierre(cierre_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CierresMensualesNomina WHERE CierreID = ?", (cierre_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Período contable reabierto exitosamente para nuevos ajustes y pagos.'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Error al reabrir período: {str(e)}'}), 500


@planilla_bp.route('/admin/rrhh/acta_cierre/<int:cierre_id>')
@admin_required
def acta_cierre(cierre_id):
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('planilla.registro_mensual'))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT CierreID, Mes, Anio, PeriodoTexto, FechaCierre, UsuarioCierreID,
               UsuarioCierreNombre, TotalColaboradores, TotalPagados, TotalPendientes,
               MasaSalarialBruta, TotalInssLaboral, TotalBaseImponibleIr, TotalIrDgi,
               TotalSalarioNeto, TotalInssPatronal, TotalInatec, TotalCargasPatronales,
               TotalProvisionesAcumuladas, CostoTotalEmpleador, Estado, Observaciones
        FROM CierresMensualesNomina
        WHERE CierreID = ?
    """, (cierre_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash("Acta de cierre no encontrada.", "warning")
        return redirect(url_for('planilla.registro_mensual'))

    cierre = {
        'CierreID': row[0], 'Mes': row[1], 'Anio': row[2], 'PeriodoTexto': row[3],
        'FechaCierre': row[4], 'UsuarioCierreID': row[5], 'UsuarioCierreNombre': row[6],
        'TotalColaboradores': row[7], 'TotalPagados': row[8], 'TotalPendientes': row[9],
        'MasaSalarialBruta': float(row[10] or 0), 'TotalInssLaboral': float(row[11] or 0),
        'TotalBaseImponibleIr': float(row[12] or 0), 'TotalIrDgi': float(row[13] or 0),
        'TotalSalarioNeto': float(row[14] or 0), 'TotalInssPatronal': float(row[15] or 0),
        'TotalInatec': float(row[16] or 0), 'TotalCargasPatronales': float(row[17] or 0),
        'TotalProvisionesAcumuladas': float(row[18] or 0), 'CostoTotalEmpleador': float(row[19] or 0),
        'Estado': row[20], 'Observaciones': row[21]
    }

    return render_template('admin/acta_cierre.html', cierre=cierre)


# ==============================================================================
# SUBMÓDULO 4: ADMINISTRACIÓN INTEGRAL DE COLABORADORES (RECURSOS HUMANOS)
# ==============================================================================
@planilla_bp.route('/admin/rrhh/empleados', methods=['GET', 'POST'])
@admin_required
def empleados():
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('planilla.index'))

    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'crear_empleado':
            nombre = request.form.get('nombre_completo', '')
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            rol_raw = request.form.get('rol_id', '0')
            salario_str = request.form.get('salario_base', '0')
            fecha_inicio = request.form.get('fecha_inicio', datetime.date.today().isoformat())
            cargo = request.form.get('cargo', '')
            departamento = request.form.get('departamento', '')
            tipo_contrato = request.form.get('tipo_contrato', 'Tiempo Indeterminado')
            cedula = request.form.get('cedula', '')
            telefono = request.form.get('telefono', '')
            domicilio = request.form.get('domicilio', '')
            jornada = request.form.get('jornada', 'Diurna Ordinaria (48 hrs semanales)').strip()
            horario = request.form.get('horario', 'Lunes a Viernes: 8:00 AM - 5:00 PM, Sábado: 8:00 AM - 12:00 MD').strip()

            errores, datos = _validar_datos_rrhh(
                nombre=nombre,
                requerir_nombre=True,
                cedula=cedula,
                telefono=telefono,
                domicilio=domicilio,
                cargo=cargo,
                requerir_cargo=False,
                departamento=departamento,
                requerir_departamento=False,
                salario_raw=salario_str,
                fecha_inicio_raw=fecha_inicio,
                requerir_fecha=True,
                email=email,
                requerir_email=True,
                password=password,
                requerir_password=True,
                tipo_contrato=tipo_contrato,
            )
            try:
                rol_id = int(rol_raw)
            except ValueError:
                rol_id = 0

            nombre_rol = 'Especialista'
            if rol_id <= 0:
                errores.append("Debe seleccionar un Rol del sistema válido.")
            else:
                cursor.execute("SELECT NombreRol FROM Roles WHERE RolID = ?", (rol_id,))
                rol_row = cursor.fetchone()
                if not rol_row:
                    errores.append("El Rol seleccionado no existe en el sistema.")
                else:
                    nombre_rol = rol_row[0]

            if not errores:
                cursor.execute("SELECT TOP 1 UsuarioID FROM Usuarios WHERE LOWER(Email) = LOWER(?)", (datos['email'],))
                if cursor.fetchone():
                    errores.append(f"El nombre de usuario / correo '{datos['email']}' ya se encuentra registrado.")
                cursor.execute("SELECT TOP 1 ContratoID FROM ContratosLaborales WHERE UPPER(CedulaIdentidad) = UPPER(?)", (datos['cedula'],))
                if cursor.fetchone():
                    errores.append(f"Ya existe un colaborador con la cédula {datos['cedula']}.")

            if errores:
                flash(' • '.join(errores), 'error')
                conn.close()
                return redirect(url_for('planilla.empleados'))

            try:
                cargo_final = datos['cargo'] or nombre_rol
                depto_final = datos['departamento']
                if not depto_final:
                    if rol_id == 3:
                        depto_final = 'Operaciones / Taller Mecánico'
                    elif rol_id == 2:
                        depto_final = 'Caja y Facturación'
                    elif rol_id == 5:
                        depto_final = 'Gerencia y Dirección'
                    elif rol_id == 7:
                        depto_final = 'Logística y Abastecimiento'
                    elif rol_id == 1007:
                        depto_final = 'Recursos Humanos y Nómina'
                    elif rol_id == 1008:
                        depto_final = 'Atención al Cliente'
                    elif rol_id in (6, 1009):
                        depto_final = 'Control y Finanzas'
                    elif rol_id == 1010:
                        depto_final = 'Mercadotecnia y Publicidad'
                    else:
                        depto_final = 'Operaciones Generales'

                hoy = datetime.date.today()
                fi_date = datetime.date.fromisoformat(datos['fecha_inicio'])
                meses_calc = max(1, (hoy.year - fi_date.year) * 12 + (hoy.month - fi_date.month) + 1)

                hashed_pass = generate_password_hash(password, method='scrypt')
                cursor.execute("""
                    INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo, SalarioBase, MesesAcumulados)
                    OUTPUT INSERTED.UsuarioID
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                """, (datos['nombre'], datos['email'], hashed_pass, rol_id, datos['salario'], meses_calc))
                inserted_id = cursor.fetchone()[0]

                cursor.execute("SELECT ISNULL(MAX(ContratoID), 0) + 1 FROM ContratosLaborales")
                next_c_id = cursor.fetchone()[0]
                num_contrato = f"CTR-TCR-{hoy.year}-{next_c_id:03d}"

                cursor.execute("""
                    INSERT INTO ContratosLaborales (
                        UsuarioID, NumeroContrato, TipoContrato, FechaInicio, FechaFin,
                        Cargo, Departamento, Jornada, Horario, SalarioPactado,
                        PeriodoPruebaDias, LugarTrabajo, CedulaIdentidad, DireccionDomicilio,
                        TelefonoContacto, EstadoContrato, ClausulasAdicionales, FechaRegistro
                    ) VALUES (
                        ?, ?, ?, ?, NULL,
                        ?, ?, ?, ?, ?,
                        30, 'Taller y Lubricantes CR - Managua', ?, ?,
                        ?, 'Vigente', 'Contrato laboral registrado en el Sistema de Recursos Humanos.', GETDATE()
                    )
                """, (
                    inserted_id, num_contrato, tipo_contrato, datos['fecha_inicio'],
                    cargo_final, depto_final, jornada, horario, datos['salario'],
                    datos['cedula'], datos['domicilio'], datos['telefono']
                ))

                conn.commit()
                flash(f"Colaborador '{datos['nombre']}' registrado con éxito con Contrato {num_contrato}.", "success")
            except Exception:
                conn.rollback()
                flash("No se pudo registrar el colaborador. Verifica los datos ingresados.", "error")
            finally:
                conn.close()
            return redirect(url_for('planilla.empleados'))

        elif action == 'editar_empleado':
            try:
                usuario_id = int(request.form.get('usuario_id', '0'))
            except ValueError:
                usuario_id = 0
            nombre = request.form.get('nombre_completo', '')
            email = request.form.get('email', '')
            rol_raw = request.form.get('rol_id', '0')
            salario_str = request.form.get('salario_base', '0')
            meses_str = request.form.get('meses_acumulados', '1')
            activo = 1 if request.form.get('activo') in ('1', 'on', 'true') else 0
            nueva_password = request.form.get('nueva_password', '').strip()

            cargo = request.form.get('cargo', '')
            departamento = request.form.get('departamento', '')
            tipo_contrato = request.form.get('tipo_contrato', 'Tiempo Indeterminado')
            fecha_inicio = request.form.get('fecha_inicio', '')
            cedula = request.form.get('cedula', '')
            telefono = request.form.get('telefono', '')
            domicilio = request.form.get('domicilio', '')
            jornada = request.form.get('jornada', '').strip()
            horario = request.form.get('horario', '').strip()

            errores, datos = _validar_datos_rrhh(
                nombre=nombre,
                requerir_nombre=True,
                cedula=cedula,
                telefono=telefono,
                domicilio=domicilio,
                cargo=cargo,
                requerir_cargo=True,
                departamento=departamento,
                requerir_departamento=True,
                salario_raw=salario_str,
                fecha_inicio_raw=fecha_inicio,
                requerir_fecha=bool(fecha_inicio.strip()),
                email=email,
                requerir_email=True,
                password=nueva_password if nueva_password else None,
                requerir_password=False,
            )
            try:
                rol_id = int(rol_raw)
            except ValueError:
                rol_id = 0
            try:
                meses = int(meses_str)
                if meses < 0 or meses > 600:
                    errores.append("Los meses acumulados deben estar entre 0 y 600.")
            except ValueError:
                meses = 1
                errores.append("Los meses acumulados deben ser un número entero válido.")

            if usuario_id <= 0:
                errores.append("Identificador de colaborador inválido.")
            if rol_id <= 0:
                errores.append("Debe seleccionar un Rol válido.")
            else:
                cursor.execute("SELECT TOP 1 RolID FROM Roles WHERE RolID = ?", (rol_id,))
                if not cursor.fetchone():
                    errores.append("El Rol seleccionado no existe.")

            if not errores:
                cursor.execute("SELECT TOP 1 UsuarioID FROM Usuarios WHERE LOWER(Email) = LOWER(?) AND UsuarioID <> ?", (datos['email'], usuario_id))
                if cursor.fetchone():
                    errores.append(f"El usuario / correo '{datos['email']}' ya está asignado a otro colaborador.")
                cursor.execute("SELECT TOP 1 ContratoID FROM ContratosLaborales WHERE UPPER(CedulaIdentidad) = UPPER(?) AND UsuarioID <> ?", (datos['cedula'], usuario_id))
                if cursor.fetchone():
                    errores.append(f"La cédula {datos['cedula']} ya está registrada para otro colaborador.")

            if errores:
                flash(' • '.join(errores), 'error')
                conn.close()
                return redirect(url_for('planilla.empleados'))

            try:
                if nueva_password:
                    hashed_new = generate_password_hash(nueva_password, method='scrypt')
                    cursor.execute("""
                        UPDATE Usuarios
                        SET NombreCompleto = ?, Email = ?, RolID = ?, SalarioBase = ?, MesesAcumulados = ?, Activo = ?, PasswordHash = ?
                        WHERE UsuarioID = ?
                    """, (datos['nombre'], datos['email'], rol_id, datos['salario'], meses, activo, hashed_new, usuario_id))
                else:
                    cursor.execute("""
                        UPDATE Usuarios
                        SET NombreCompleto = ?, Email = ?, RolID = ?, SalarioBase = ?, MesesAcumulados = ?, Activo = ?
                        WHERE UsuarioID = ?
                    """, (datos['nombre'], datos['email'], rol_id, datos['salario'], meses, activo, usuario_id))

                if datos['fecha_inicio']:
                    cursor.execute("""
                        UPDATE ContratosLaborales
                        SET Cargo = ?, Departamento = ?, TipoContrato = ?, Jornada = COALESCE(NULLIF(?, ''), Jornada),
                            Horario = COALESCE(NULLIF(?, ''), Horario), SalarioPactado = ?, CedulaIdentidad = ?,
                            DireccionDomicilio = ?, TelefonoContacto = ?, FechaInicio = ?, EstadoContrato = ?
                        WHERE UsuarioID = ?
                    """, (
                        datos['cargo'], datos['departamento'], tipo_contrato, jornada, horario,
                        datos['salario'], datos['cedula'], datos['domicilio'], datos['telefono'], datos['fecha_inicio'],
                        'Vigente' if activo == 1 else 'Inactivo', usuario_id
                    ))
                else:
                    cursor.execute("""
                        UPDATE ContratosLaborales
                        SET Cargo = ?, Departamento = ?, TipoContrato = ?, Jornada = COALESCE(NULLIF(?, ''), Jornada),
                            Horario = COALESCE(NULLIF(?, ''), Horario), SalarioPactado = ?, CedulaIdentidad = ?,
                            DireccionDomicilio = ?, TelefonoContacto = ?, EstadoContrato = ?
                        WHERE UsuarioID = ?
                    """, (
                        datos['cargo'], datos['departamento'], tipo_contrato, jornada, horario,
                        datos['salario'], datos['cedula'], datos['domicilio'], datos['telefono'],
                        'Vigente' if activo == 1 else 'Inactivo', usuario_id
                    ))

                conn.commit()
                flash(f"Colaborador '{datos['nombre']}' actualizado exitosamente.", "success")
            except Exception:
                conn.rollback()
                flash("No se pudo actualizar el colaborador. Verifica los campos ingresados.", "error")
            finally:
                conn.close()
            return redirect(url_for('planilla.empleados'))

        elif action == 'toggle_estado':
            usuario_id = request.form.get('usuario_id')
            if str(usuario_id) == str(session.get('usuario_id')) or str(usuario_id) == '1':
                flash("No puedes modificar el estado de tu propia cuenta de acceso.", "error")
                conn.close()
                return redirect(url_for('planilla.empleados'))
            try:
                cursor.execute("SELECT Activo, NombreCompleto FROM Usuarios WHERE UsuarioID = ?", (usuario_id,))
                user_row = cursor.fetchone()
                if user_row:
                    nuevo_estado = 0 if user_row[0] else 1
                    cursor.execute("UPDATE Usuarios SET Activo = ? WHERE UsuarioID = ?", (nuevo_estado, usuario_id))
                    cursor.execute("UPDATE ContratosLaborales SET EstadoContrato = ? WHERE UsuarioID = ?", (
                        'Vigente' if nuevo_estado == 1 else 'Inactivo', usuario_id
                    ))
                    conn.commit()
                    estado_txt = "activado" if nuevo_estado == 1 else "desactivado"
                    flash(f"El colaborador '{user_row[1]}' ha sido {estado_txt} en el sistema.", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error al cambiar estado: {str(e)}", "error")
            finally:
                conn.close()
            return redirect(url_for('planilla.empleados'))

        elif action == 'eliminar_empleado':
            usuario_id = request.form.get('usuario_id')
            if str(usuario_id) == str(session.get('usuario_id')) or str(usuario_id) == '1':
                flash("No es posible eliminar al Administrador ni a tu propio usuario activo.", "error")
                conn.close()
                return redirect(url_for('planilla.empleados'))

            try:
                # Comprobar historial operativo (Órdenes de Trabajo, Ventas)
                cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE MecanicoID = ?", (usuario_id,))
                ordenes_cnt = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM Ventas WHERE UsuarioID = ?", (usuario_id,))
                ventas_cnt = cursor.fetchone()[0]

                if ordenes_cnt > 0 or ventas_cnt > 0:
                    cursor.execute("UPDATE Usuarios SET Activo = 0 WHERE UsuarioID = ?", (usuario_id,))
                    cursor.execute("UPDATE ContratosLaborales SET EstadoContrato = 'Finalizado' WHERE UsuarioID = ?", (usuario_id,))
                    conn.commit()
                    flash("El colaborador cuenta con historial operativo y facturación; ha sido dado de baja (Inactivo) preservando la integridad de las auditorías contables.", "info")
                else:
                    cursor.execute("DELETE FROM ContratosLaborales WHERE UsuarioID = ?", (usuario_id,))
                    cursor.execute("DELETE FROM Usuarios WHERE UsuarioID = ?", (usuario_id,))
                    conn.commit()
                    flash("Colaborador eliminado del sistema correctamente.", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error al eliminar colaborador: {str(e)}", "error")
            finally:
                conn.close()
            return redirect(url_for('planilla.empleados'))

    # ==================== GET: LISTADO Y ESTADÍSTICAS LUXURY ATELIER ====================
    cursor.execute("""
        SELECT U.UsuarioID, U.NombreCompleto, U.Email, U.RolID, R.NombreRol,
               U.Activo, U.SalarioBase, U.MesesAcumulados,
               C.ContratoID, C.NumeroContrato, C.Cargo, C.Departamento, C.TipoContrato,
               C.FechaInicio, C.CedulaIdentidad, C.TelefonoContacto, C.DireccionDomicilio,
               C.Jornada, C.Horario, C.EstadoContrato
        FROM Usuarios U
        JOIN Roles R ON U.RolID = R.RolID
        LEFT JOIN ContratosLaborales C ON U.UsuarioID = C.UsuarioID
        WHERE U.UsuarioID != 1 AND U.Email NOT IN ('carlos.contabilidad', 'elvin.admin')
        ORDER BY U.Activo DESC, U.UsuarioID ASC
    """)
    rows = cursor.fetchall()

    empleados_lista = []
    total_activos = 0
    total_inactivos = 0
    total_nomina_base = 0.0
    total_mecanicos = 0
    total_admin = 0

    for r in rows:
        activo = bool(r[5])
        salario = float(r[6]) if r[6] else 0.0
        cargo = r[10] or r[4]
        rol_id = r[3]
        email = r[2]

        is_mecanico = (rol_id == 3) or ('Mecánico' in cargo)
        is_asesor = (email in ('carlos.finanzas', 'martha.estadistica')) or ('Asesor' in (cargo or ''))

        if activo:
            total_activos += 1
            total_nomina_base += salario
            if is_mecanico:
                total_mecanicos += 1
            else:
                total_admin += 1
        else:
            total_inactivos += 1

        calc = calcular_desglose_laboral_y_dgi(salario, r[7] or 10)

        emp_item = {
            'usuario_id': r[0],
            'nombre': r[1],
            'email': r[2],
            'rol_id': r[3],
            'rol_nombre': r[4],
            'activo': activo,
            'salario_base': salario,
            'meses_acumulados': r[7] or 10,
            'contrato_id': r[8],
            'numero_contrato': r[9] or f"CTR-TCR-2026-{r[0]:03d}",
            'cargo': cargo,
            'departamento': r[11] or 'Operaciones',
            'tipo_contrato': r[12] or 'Tiempo Indeterminado',
            'fecha_inicio': r[13].strftime('%d/%m/%Y') if r[13] else '01/01/2026',
            'fecha_inicio_iso': r[13].strftime('%Y-%m-%d') if r[13] else '2026-01-01',
            'cedula': r[14] or 'N/D',
            'telefono': r[15] or 'N/D',
            'domicilio': r[16] or 'Managua',
            'jornada': r[17] or 'Diurna Ordinaria (48 hrs semanales)',
            'horario': r[18] or 'Lunes a Viernes: 8:00 AM - 5:00 PM, Sábado: 8:00 AM - 12:00 MD',
            'estado_contrato': r[19] or ('Vigente' if activo else 'Inactivo'),
            'is_mecanico': is_mecanico,
            'is_asesor': is_asesor,
            'inss_laboral': calc['inss_laboral'],
            'salario_neto': calc['salario_neto'],
            'inss_patronal': calc['inss_patronal'],
            'inatec': calc['inatec'],
            'aguinaldo_mensual': calc['aguinaldo_mensual'],
            'vacaciones_mensuales': calc['vacaciones_mensuales'],
            'indemnizacion_mensual': calc['indemnizacion_mensual'],
            'total_cargas_patronales': round(calc['inss_patronal'] + calc['inatec'], 2),
            'costo_total_empleador': calc['costo_total_empleador']
        }
        empleados_lista.append(emp_item)

    # Cargas y provisiones consolidadas
    total_cargas_patronales = round(total_nomina_base * 0.245, 2) # INSS 22.5% + INATEC 2%
    total_provisiones_mensuales = round(total_nomina_base * 0.25, 2) # 25% (Aguinaldo + Vacaciones + Indemnización)
    costo_total_empresa = round(total_nomina_base + total_cargas_patronales + total_provisiones_mensuales, 2)

    # Roles disponibles para selects
    cursor.execute("SELECT RolID, NombreRol FROM Roles WHERE RolID != 1 ORDER BY NombreRol ASC")
    roles = cursor.fetchall()
    conn.close()

    kpis = {
        'total_activos': total_activos,
        'total_inactivos': total_inactivos,
        'total_nomina_base': total_nomina_base,
        'total_cargas_patronales': total_cargas_patronales,
        'total_provisiones_mensuales': total_provisiones_mensuales,
        'costo_total_empresa': costo_total_empresa,
        'total_mecanicos': total_mecanicos,
        'total_admin': total_admin
    }

    return render_template(
        'admin/empleados_rrhh.html',
        empleados=empleados_lista,
        kpis=kpis,
        roles=roles
    )
