import json
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from database import get_db_connection
from functools import wraps

contador_bp = Blueprint('contador', __name__, url_prefix='/contador')

MESES_ES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def contador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('rol_id') not in (1, 4, 5, 6):
            flash('Acceso denegado. Solo Contabilidad, Finanzas o Gerencia pueden ver esta sección.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def obtener_periodos_disponibles(conn=None):
    """Devuelve la lista ordenada de meses y años con movimientos contables registrados."""
    close_conn = False
    if not conn:
        conn = get_db_connection()
        close_conn = True

    periodos_set = set()
    ahora = datetime.now()
    periodos_set.add((ahora.year, ahora.month))

    if conn:
        try:
            cursor = conn.cursor()
            # Facturas
            cursor.execute("SELECT DISTINCT YEAR(FechaEmision), MONTH(FechaEmision) FROM Facturas WHERE Estado = 'Pagada' AND FechaEmision IS NOT NULL")
            for r in cursor.fetchall():
                if r[0] and r[1]:
                    periodos_set.add((int(r[0]), int(r[1])))
            
            # Gastos
            cursor.execute("SELECT DISTINCT YEAR(FechaGasto), MONTH(FechaGasto) FROM GastosOperativos WHERE FechaGasto IS NOT NULL")
            for r in cursor.fetchall():
                if r[0] and r[1]:
                    periodos_set.add((int(r[0]), int(r[1])))

            # Compras
            cursor.execute("SELECT DISTINCT YEAR(FechaCompra), MONTH(FechaCompra) FROM Compras WHERE FechaCompra IS NOT NULL")
            for r in cursor.fetchall():
                if r[0] and r[1]:
                    periodos_set.add((int(r[0]), int(r[1])))

            # Reportes cerrados
            cursor.execute("SELECT DISTINCT Anio, Mes FROM ReportesContables WHERE Anio IS NOT NULL AND Mes IS NOT NULL")
            for r in cursor.fetchall():
                if r[0] and r[1]:
                    periodos_set.add((int(r[0]), int(r[1])))
        except Exception as e:
            print(f"Error consultando periodos disponibles: {e}")
        finally:
            if close_conn:
                conn.close()

    # Ordenar descendente (año desc, mes desc)
    lista_ordenada = sorted(list(periodos_set), key=lambda x: (x[0], x[1]), reverse=True)
    resultado = []
    for a, m in lista_ordenada:
        resultado.append({
            'anio': a,
            'mes': m,
            'nombre_mes': MESES_ES[m] if 1 <= m <= 12 else str(m),
            'texto': f"{MESES_ES[m] if 1 <= m <= 12 else str(m)} {a}",
            'es_actual': (a == ahora.year and m == ahora.month)
        })
    return resultado

def obtener_datos_financieros_taller(mes=None, anio=None):
    """Consolida de forma 100% automatizada todas las cuentas contables del taller para un mes y año específicos."""
    ahora = datetime.now()
    if mes is None:
        mes = ahora.month
    else:
        mes = int(mes)
    if anio is None:
        anio = ahora.year
    else:
        anio = int(anio)

    conn = get_db_connection()
    nombre_mes = MESES_ES[mes] if 1 <= mes <= 12 else str(mes)
    periodo_texto = f"{nombre_mes} {anio}"

    datos = {
        'mes': mes,
        'anio': anio,
        'nombre_mes': nombre_mes,
        'periodo_texto': periodo_texto,
        'periodos_disponibles': [],
        # Ventas e Ingresos
        'ventas_brutas': 0.0,
        'descuentos': 0.0,
        'ventas_netas': 0.0,
        'iva_debito_fiscal': 0.0,
        'facturas_cantidad': 0,
        'mano_obra_mes': 0.0,
        'repuestos_taller_mes': 0.0,
        'mostrador_mes': 0.0,
        # Costos de Ventas
        'costo_repuestos_taller': 0.0,
        'costo_mostrador': 0.0,
        'compras_mes': 0.0,
        'costo_ventas': 0.0,
        'utilidad_bruta': 0.0,
        'margen_bruto_pct': 0.0,
        # Gastos Operativos
        'gastos_nomina_base': 0.0,
        'gastos_cargas_patronales': 0.0,
        'gastos_provisiones_laborales': 0.0,
        'gastos_nomina_total': 0.0,
        'gastos_servicios_basicos': 0.0,
        'gastos_alquiler': 0.0,
        'gastos_mantenimiento': 0.0,
        'gastos_otros': 0.0,
        'gastos_operativos': 0.0,
        'gastos_desglose': [],
        'utilidad_operativa': 0.0,
        'margen_operativo_pct': 0.0,
        # Impuestos y Utilidad Neta
        'impuesto_renta_ir': 0.0,
        'utilidad_neta': 0.0,
        'margen_neto_pct': 0.0,
        # Balance General - Activos Corrientes
        'efectivo_caja': 0.0,
        'cuentas_por_cobrar': 0.0,
        'inventario_costo': 0.0,
        'articulos_inventario': 0,
        'credito_fiscal_iva': 0.0,
        'activo_circulante': 0.0,
        # Balance General - Activos No Corrientes (Fijos)
        'activo_fijo_maquinaria': 145000.0,
        'activo_fijo_herramientas': 42000.0,
        'activo_fijo_mobiliario': 28000.0,
        'depreciacion_acumulada': -15000.0,
        'activo_fijo_total': 200000.0,
        'activo_fijo_estimado': 200000.0,
        'repuestos_mes': 0.0,
        'gastos_planilla': 0.0,
        'activo_total': 0.0,
        # Balance General - Pasivos
        'proveedores_por_pagar': 0.0,
        'iva_por_enterar': 0.0,
        'retenciones_dgi': 0.0,
        'obligaciones_laborales': 0.0,
        'pasivo_circulante': 0.0,
        'pasivo_largo_plazo': 0.0,
        'pasivo_total': 0.0,
        # Balance General - Patrimonio
        'capital_social': 150000.0,
        'utilidades_acumuladas': 0.0,
        'utilidad_ejercicio': 0.0,
        'patrimonio': 0.0,
        'pasivo_mas_patrimonio': 0.0,
        'diferencia_cuadre': 0.0,
        'cuadra': True,
        # Ratios / Razones
        'razon_circulante': 0.0,
        'capital_trabajo': 0.0,
        'endeudamiento_pct': 0.0,
        'autonomia_financiera': 0.0,
        'rotacion_inventario': 0.0,
        'dias_inventario': 0,
        'cierres_diarios': [],
        # IDs de Ajuste para cuentas base (permite edición y restablecimiento)
        'ajuste_id_efectivo_caja': None,
        'ajuste_id_cuentas_por_cobrar': None,
        'ajuste_id_inventario_costo': None,
        'ajuste_id_credito_fiscal_iva': None,
        'ajuste_id_activo_fijo_maquinaria': None,
        'ajuste_id_activo_fijo_herramientas': None,
        'ajuste_id_activo_fijo_mobiliario': None,
        'ajuste_id_depreciacion_acumulada': None,
        'ajuste_id_proveedores_por_pagar': None,
        'ajuste_id_iva_por_enterar': None,
        'ajuste_id_retenciones_dgi': None,
        'ajuste_id_obligaciones_laborales': None,
        'ajuste_id_pasivo_largo_plazo': None,
        'ajuste_id_capital_social': None,
        'ajuste_id_utilidades_acumuladas': None,
        'ajuste_id_mano_obra_mes': None,
        'ajuste_id_repuestos_taller_mes': None,
        'ajuste_id_mostrador_mes': None,
        'ajuste_id_costo_repuestos_taller': None,
        'ajuste_id_costo_mostrador': None,
        'ajuste_id_compras_mes': None,
        'ajuste_id_gastos_nomina_base': None,
        'ajuste_id_gastos_cargas_patronales': None,
        'ajuste_id_gastos_provisiones_laborales': None,
        'ajuste_id_gastos_servicios_basicos': None,
        'ajuste_id_gastos_alquiler': None,
        'ajuste_id_gastos_mantenimiento': None,
        'ajuste_id_gastos_otros': None,
        'ajuste_id_gastos_mercadotecnia': None
    }

    if not conn:
        return datos

    try:
        cursor = conn.cursor()
        datos['periodos_disponibles'] = obtener_periodos_disponibles(conn)

        # 1. Facturación del mes seleccionado (100% Real de Base de Datos)
        cursor.execute("""
            SELECT ISNULL(SUM(SubTotal), 0), ISNULL(SUM(TotalIVA), 0), ISNULL(SUM(TotalNeto), 0), ISNULL(SUM(DescuentoAplicado), 0), COUNT(*)
            FROM Facturas 
            WHERE Estado = 'Pagada' AND MONTH(FechaEmision) = ? AND YEAR(FechaEmision) = ?
        """, (mes, anio))
        row_fact = cursor.fetchone()
        subtotal_gravado_db = float(row_fact[0] or 0.0)
        total_iva_db = float(row_fact[1] or 0.0)
        total_bruto_db = float(row_fact[2] or 0.0)

        datos['ventas_netas'] = round(subtotal_gravado_db if subtotal_gravado_db > 0 else (total_bruto_db - total_iva_db), 2)
        datos['ventas_brutas'] = round(total_bruto_db if total_bruto_db > 0 else (subtotal_gravado_db + total_iva_db), 2)
        datos['iva_debito_fiscal'] = round(total_iva_db, 2)
        datos['descuentos'] = float(row_fact[3] or 0.0)
        datos['facturas_cantidad'] = int(row_fact[4] or 0)

        # 2. Desglose de Facturación por Fuentes (Mano de Obra en Taller)
        cursor.execute("""
            SELECT ISNULL(SUM(mo.CostoSugerido), 0)
            FROM OrdenManoObra mo
            JOIN OrdenesTrabajo ot ON mo.OrdenID = ot.OrdenID
            JOIN Facturas f ON ot.OrdenID = f.OrdenID
            WHERE f.Estado = 'Pagada' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
        """, (mes, anio))
        ingreso_mo = float(cursor.fetchone()[0] or 0.0)

        # Repuestos facturados en Órdenes de Trabajo (Venta y Costo)
        cursor.execute("""
            SELECT ISNULL(SUM(or_rep.Cantidad * p.PrecioVenta), 0),
                   ISNULL(SUM(or_rep.Cantidad * p.PrecioCompra), 0)
            FROM OrdenRepuestos or_rep
            JOIN Productos p ON or_rep.ProductoID = p.ProductoID
            JOIN OrdenesTrabajo ot ON or_rep.OrdenID = ot.OrdenID
            JOIN Facturas f ON ot.OrdenID = f.OrdenID
            WHERE f.Estado = 'Pagada' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
        """, (mes, anio))
        rep_row = cursor.fetchone()
        ingreso_rep_taller = float(rep_row[0] or 0.0)
        costo_rep_taller = float(rep_row[1] or 0.0)

        # Ventas directas de mostrador / tienda
        cursor.execute("""
            SELECT ISNULL(SUM(df.PrecioVentaAplicado * df.Cantidad), 0),
                   ISNULL(SUM(ISNULL(p.PrecioCompra, 0.0) * df.Cantidad), 0)
            FROM DetalleFactura df
            JOIN Facturas f ON df.FacturaID = f.FacturaID
            LEFT JOIN Productos p ON df.ProductoID = p.ProductoID
            WHERE f.Estado = 'Pagada' AND f.OrdenID IS NULL AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
        """, (mes, anio))
        most_row = cursor.fetchone()
        ingreso_mostrador = float(most_row[0] or 0.0)
        costo_mostrador = float(most_row[1] or 0.0)

        # Conciliación precisa de ingresos contra Ventas Netas
        suma_desglose = ingreso_mo + ingreso_rep_taller + ingreso_mostrador
        if datos['ventas_netas'] > 0 and suma_desglose > 0:
            factor = datos['ventas_netas'] / suma_desglose
            datos['mano_obra_mes'] = round(ingreso_mo * factor, 2)
            datos['repuestos_taller_mes'] = round(ingreso_rep_taller * factor, 2)
            datos['mostrador_mes'] = round(datos['ventas_netas'] - datos['mano_obra_mes'] - datos['repuestos_taller_mes'], 2)
        else:
            datos['mano_obra_mes'] = 0.0
            datos['repuestos_taller_mes'] = 0.0
            datos['mostrador_mes'] = 0.0
        datos['repuestos_mes'] = round(datos['repuestos_taller_mes'] + datos['mostrador_mes'], 2)

        # 3. Compras de Inventario y Bodega del mes
        cursor.execute("""
            SELECT ISNULL(SUM(TotalCompra), 0) FROM Compras 
            WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?
        """, (mes, anio))
        datos['compras_mes'] = float(cursor.fetchone()[0] or 0.0)

        # Costo de Ventas Real (COGS 100% Automatizado)
        datos['costo_repuestos_taller'] = round(costo_rep_taller, 2)
        datos['costo_mostrador'] = round(costo_mostrador, 2)
        datos['costo_ventas'] = round(costo_rep_taller + costo_mostrador, 2)
        datos['utilidad_bruta'] = round(datos['ventas_netas'] - datos['costo_ventas'], 2)
        datos['margen_bruto_pct'] = round((datos['utilidad_bruta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        # 4. Gastos Operativos Reales (Sin valores quemados)
        cursor.execute("""
            SELECT Categoria, ISNULL(SUM(Monto), 0) 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            GROUP BY Categoria
        """, (mes, anio))
        gastos_bd = dict(cursor.fetchall())

        datos['gastos_servicios_basicos'] = float(gastos_bd.get('Servicios Basicos', 0.0) or 0.0)
        datos['gastos_alquiler'] = float(gastos_bd.get('Alquiler', 0.0) or 0.0)
        datos['gastos_mantenimiento'] = float(gastos_bd.get('Mantenimiento Local', 0.0) or 0.0)
        datos['gastos_otros'] = float(gastos_bd.get('Otros', 0.0) or 0.0)
        
        # Automatización con Mercadotecnia: Campañas publicitarias + Costo de Premios entregados en Rifas
        datos['gastos_mercadotecnia_directos'] = float(gastos_bd.get('Mercadotecnia', 0) or gastos_bd.get('Publicidad', 0) or 0.0)
        try:
            cursor.execute("""
                SELECT ISNULL(SUM(p.PrecioCompra), 0)
                FROM RifaPremios r
                JOIN Productos p ON r.ProductoID = p.ProductoID
                WHERE (r.MesPeriodo = ? OR (r.FechaSorteo IS NOT NULL AND MONTH(r.FechaSorteo) = ? AND YEAR(r.FechaSorteo) = ?))
                  AND r.Estado IN ('Entregado', 'Sorteado')
            """, (f"{mes}/{anio}", mes, anio))
            costo_premios = float(cursor.fetchone()[0] or 0.0)
        except Exception:
            costo_premios = 0.0
        datos['costo_premios_rifas'] = costo_premios
        datos['gastos_mercadotecnia'] = round(datos['gastos_mercadotecnia_directos'] + costo_premios, 2)

        cursor.execute("""
            SELECT Categoria, Descripcion, Monto, FechaGasto 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            ORDER BY FechaGasto DESC
        """, (mes, anio))
        datos['gastos_desglose'] = [
            {'categoria': r[0], 'descripcion': r[1], 'monto': float(r[2]), 'fecha': r[3].strftime('%d/%m/%Y')}
            for r in cursor.fetchall()
        ]

        # 5. Nómina Operativa y Cargas Sociales (Leyes Laborales de Nicaragua - MIPYME en Tiempo Real)
        from routes.planilla import obtener_totales_nomina_mes
        totales_nom = obtener_totales_nomina_mes(mes, anio)
        tot_nom = totales_nom['totales']

        # Automatización en tiempo real vinculada a Recursos Humanos / Planilla de Pago
        # Refleja de inmediato los salarios y cargas sociales de colaboradores pagados
        if not datos.get('ajuste_id_gastos_nomina_base'):
            datos['gastos_nomina_base'] = float(tot_nom.get('salario_bruto', 0.0) or 0.0)
        if not datos.get('ajuste_id_gastos_cargas_patronales'):
            datos['gastos_cargas_patronales'] = float(tot_nom.get('cargas_patronales', 0.0) or 0.0) # INSS Patronal (22.5%) + INATEC (2%)
        if not datos.get('ajuste_id_gastos_provisiones_laborales'):
            datos['gastos_provisiones_laborales'] = float(tot_nom.get('provisiones_mensuales', 0.0) or 0.0) # Ley 185 (Aguinaldo, Vacaciones, Indemnización)

        datos['gastos_nomina_total'] = round(datos['gastos_nomina_base'] + datos['gastos_cargas_patronales'] + datos['gastos_provisiones_laborales'], 2)
        datos['gastos_planilla'] = datos['gastos_nomina_total']

        # 6. Cuentas Contables Personalizadas y Ajustes Dinámicos (CuentasContablesAjustes)
        datos['cuentas_pers_activo_corriente'] = []
        datos['cuentas_pers_activo_no_corriente'] = []
        datos['cuentas_pers_pasivo_corriente'] = []
        datos['cuentas_pers_pasivo_no_corriente'] = []
        datos['cuentas_pers_patrimonio'] = []
        datos['cuentas_pers_ingresos'] = []
        datos['cuentas_pers_costos'] = []
        datos['cuentas_pers_gastos'] = []
        datos['cuentas_pers_otros'] = []

        import unicodedata
        def _norm_cont(s):
            if not s: return ""
            return "".join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

        MAPA_BASE_BALANCE = {
            'efectivo_caja': ['efectivo y equivalentes de efectivo', 'caja general y bancos', 'efectivo en caja', 'caja general', 'caja'],
            'cuentas_por_cobrar': ['cuentas por cobrar comerciales', 'cuentas por cobrar', 'ordenes pendientes de cobro'],
            'inventario_costo': ['inventario de mercaderias', 'repuestos y lubricantes al costo', 'inventario'],
            'credito_fiscal_iva': ['credito fiscal iva por acreditar', 'credito fiscal iva', 'credito fiscal'],
            'activo_fijo_maquinaria': ['maquinaria, rampas y elevadores', 'maquinaria', 'rampas'],
            'activo_fijo_herramientas': ['herramientas especializadas y scanners', 'herramientas especializadas', 'herramientas'],
            'activo_fijo_mobiliario': ['mobiliario de atencion, mostrador', 'mobiliario de atencion', 'mobiliario'],
            'depreciacion_acumulada': ['depreciacion acumulada'],
            'proveedores_por_pagar': ['cuentas por pagar comerciales', 'proveedores de repuestos', 'proveedores por pagar', 'proveedores'],
            'iva_por_enterar': ['debito fiscal iva por enterar', 'iva por enterar', 'debito fiscal'],
            'retenciones_dgi': ['retenciones fiscales en la fuente por pagar', 'retenciones fiscales', 'retenciones dgi'],
            'obligaciones_laborales': ['obligaciones laborales y cargas sociales', 'obligaciones laborales', 'inss laboral y patronal'],
            'pasivo_largo_plazo': ['prestamos bancarios y financiamiento', 'prestamos bancarios', 'pasivo largo plazo'],
            'capital_social': ['capital social suscrito y pagado', 'capital social'],
            'utilidades_acumuladas': ['resultados y utilidades acumuladas', 'utilidades acumuladas', 'utilidades retenidas', 'ejercicios anteriores']
        }

        MAPA_BASE_ESTADO = {
            'mano_obra_mes': ['ingresos por servicios mecanicos', 'mano de obra', 'servicios mecanicos'],
            'repuestos_taller_mes': ['ingresos por venta de repuestos y lubricantes en taller', 'repuestos aplicados en ordenes', 'repuestos y lubricantes en taller'],
            'mostrador_mes': ['ingresos por venta de repuestos y accesorios en mostrador', 'mostrador / tienda', 'mostrador'],
            'costo_repuestos_taller': ['costo de repuestos y materiales aplicados', 'costo de adquisicion de repuestos'],
            'costo_mostrador': ['costo de mercaderias vendidas en mostrador', 'costo de articulos despachados'],
            'compras_mes': ['compras directas y reabastecimiento de bodega', 'compras directas'],
            'gastos_nomina_base': ['gastos de personal', 'nomina y salarios', 'nomina'],
            'gastos_cargas_patronales': ['cargas sociales patronales', 'inss patronal', 'inatec'],
            'gastos_provisiones_laborales': ['provision de prestaciones laborales', 'prestaciones laborales', 'aguinaldo y vacaciones'],
            'gastos_servicios_basicos': ['servicios basicos', 'energia electrica', 'disnorte'],
            'gastos_alquiler': ['alquiler y arrendamiento', 'arriendo mensual', 'alquiler'],
            'gastos_mantenimiento': ['mantenimiento de herramientas', 'mantenimiento local', 'mantenimiento'],
            'gastos_otros': ['otros gastos operacionales', 'otros gastos'],
            'gastos_mercadotecnia': ['mercadotecnia, publicidad', 'mercadotecnia', 'publicidad']
        }

        orig_ingresos_base = round(datos['mano_obra_mes'] + datos['repuestos_taller_mes'] + datos['mostrador_mes'], 2)
        orig_costo_base = round(datos['costo_repuestos_taller'] + datos['costo_mostrador'], 2)

        def _grupo_estado(c_str):
            cn = _norm_cont(c_str)
            if 'otro' in cn:
                if 'gasto' in cn and 'ingreso' not in cn:
                    return 'otros_gastos'
                return 'otros'
            if 'ingreso' in cn:
                return 'ingresos'
            if 'costo' in cn:
                return 'costos'
            if 'gasto' in cn:
                return 'gastos'
            return 'otros'

        try:
            cursor.execute("""
                SELECT AjusteID, TipoReporte, Categoria, NombreCuenta, Monto, ClaveCuenta 
                FROM CuentasContablesAjustes 
                WHERE Mes = ? AND Anio = ?
                ORDER BY AjusteID ASC
            """, (mes, anio))
            for aj in cursor.fetchall():
                aj_id = aj[0]
                tipo_rep = aj[1]
                cat = aj[2]
                nombre = aj[3]
                monto = float(aj[4] or 0.0)
                clave_db = aj[5] if len(aj) > 5 and aj[5] else None
                norm_nom = _norm_cont(nombre)

                item = {
                    'id': aj_id,
                    'tipo_reporte': tipo_rep,
                    'categoria': cat,
                    'nombre': nombre,
                    'monto': monto,
                    'monto_raw': monto,
                    'clave_cuenta': clave_db
                }

                # Mapeo de categoría base oficial en Balance General
                DEFAULT_CAT_BASE_BALANCE = {
                    'efectivo_caja': 'Activo Corriente',
                    'cuentas_por_cobrar': 'Activo Corriente',
                    'inventario_costo': 'Activo Corriente',
                    'credito_fiscal_iva': 'Activo Corriente',
                    'activo_fijo_maquinaria': 'Activo No Corriente',
                    'activo_fijo_herramientas': 'Activo No Corriente',
                    'activo_fijo_mobiliario': 'Activo No Corriente',
                    'depreciacion_acumulada': 'Activo No Corriente',
                    'proveedores_por_pagar': 'Pasivo Corriente',
                    'iva_por_enterar': 'Pasivo Corriente',
                    'retenciones_dgi': 'Pasivo Corriente',
                    'obligaciones_laborales': 'Pasivo Corriente',
                    'pasivo_largo_plazo': 'Pasivo No Corriente',
                    'capital_social': 'Patrimonio',
                    'utilidades_acumuladas': 'Patrimonio'
                }

                # Mapeo de categoría base oficial en Estado de Resultados
                DEFAULT_CAT_BASE_ESTADO = {
                    'mano_obra_mes': 'Ingresos Operativos',
                    'repuestos_taller_mes': 'Ingresos Operativos',
                    'mostrador_mes': 'Ingresos Operativos',
                    'costo_repuestos_taller': 'Costos de Ventas',
                    'costo_mostrador': 'Costos de Ventas',
                    'compras_mes': 'Costos de Ventas',
                    'gastos_nomina_base': 'Gastos Operativos',
                    'gastos_cargas_patronales': 'Gastos Operativos',
                    'gastos_provisiones_laborales': 'Gastos Operativos',
                    'gastos_servicios_basicos': 'Gastos Operativos',
                    'gastos_alquiler': 'Gastos Operativos',
                    'gastos_mantenimiento': 'Gastos Operativos',
                    'gastos_otros': 'Gastos Operativos',
                    'gastos_mercadotecnia': 'Gastos Operativos'
                }

                # Revisar si coincide con una cuenta base existente por clave o alias
                base_match_key = None
                if clave_db:
                    base_match_key = clave_db
                elif tipo_rep == 'Balance':
                    for k, aliases in MAPA_BASE_BALANCE.items():
                        if any(a in norm_nom for a in aliases):
                            base_match_key = k
                            break
                elif tipo_rep == 'EstadoResultados':
                    for k, aliases in MAPA_BASE_ESTADO.items():
                        if any(a in norm_nom for a in aliases):
                            base_match_key = k
                            break

                if base_match_key:
                    if tipo_rep == 'Balance' and base_match_key in DEFAULT_CAT_BASE_BALANCE:
                        def_cat = DEFAULT_CAT_BASE_BALANCE[base_match_key]
                        c1 = _norm_cont(cat)
                        c2 = _norm_cont(def_cat)
                        coincide = False
                        if ('patrimonio' in c1 or 'capital' in c1) and ('patrimonio' in c2 or 'capital' in c2):
                            coincide = True
                        elif 'pasivo' in c1 and 'pasivo' in c2:
                            if ('no corriente' in c1 or 'largo' in c1) == ('no corriente' in c2 or 'largo' in c2):
                                coincide = True
                        elif 'activo' in c1 and 'activo' in c2:
                            if ('no corriente' in c1 or 'fijo' in c1) == ('no corriente' in c2 or 'fijo' in c2):
                                coincide = True

                        if coincide:
                            if base_match_key == 'depreciacion_acumulada':
                                datos[base_match_key] = -abs(monto)
                            else:
                                datos[base_match_key] = monto
                            datos['ajuste_id_' + base_match_key] = aj_id
                            datos['nombre_' + base_match_key] = nombre
                            datos['categoria_' + base_match_key] = cat
                            continue
                        else:
                            # El usuario reubicó la cuenta a otra categoría (ej. Activo o Pasivo)
                            datos['ocultar_' + base_match_key] = True
                            datos['ajuste_id_' + base_match_key] = aj_id
                            datos[base_match_key] = 0.0
                            item['clave_cuenta'] = clave_db or base_match_key
                            # Continúa al flujo de cuentas personalizadas abajo
                    elif tipo_rep == 'EstadoResultados' and base_match_key in DEFAULT_CAT_BASE_ESTADO:
                        def_cat = DEFAULT_CAT_BASE_ESTADO[base_match_key]
                        if _grupo_estado(cat) == _grupo_estado(def_cat):
                            datos[base_match_key] = monto
                            datos['ajuste_id_' + base_match_key] = aj_id
                            datos['nombre_' + base_match_key] = nombre
                            datos['categoria_' + base_match_key] = cat
                            continue
                        else:
                            # El usuario reubicó la cuenta a otra sección del Estado de Resultados
                            datos['ocultar_' + base_match_key] = True
                            datos['ajuste_id_' + base_match_key] = aj_id
                            datos[base_match_key] = 0.0
                            item['clave_cuenta'] = clave_db or base_match_key
                            # Continúa al flujo de cuentas personalizadas abajo
                    else:
                        if base_match_key == 'depreciacion_acumulada':
                            datos[base_match_key] = -abs(monto)
                        else:
                            datos[base_match_key] = monto
                        datos['ajuste_id_' + base_match_key] = aj_id
                        datos['nombre_' + base_match_key] = nombre
                        datos['categoria_' + base_match_key] = cat
                        continue

                # Si es una cuenta personalizada o cuenta base reubicada de categoría
                c_norm = _norm_cont(cat)
                if tipo_rep == 'Balance':
                    if 'pasivo' in c_norm and ('no corriente' in c_norm or 'largo' in c_norm):
                        datos['cuentas_pers_pasivo_no_corriente'].append(item)
                    elif 'pasivo' in c_norm:
                        datos['cuentas_pers_pasivo_corriente'].append(item)
                    elif 'activo' in c_norm and ('no corriente' in c_norm or 'fijo' in c_norm):
                        datos['cuentas_pers_activo_no_corriente'].append(item)
                    elif 'activo' in c_norm:
                        datos['cuentas_pers_activo_corriente'].append(item)
                    elif 'patrimonio' in c_norm or 'capital' in c_norm:
                        datos['cuentas_pers_patrimonio'].append(item)
                    else:
                        datos['cuentas_pers_patrimonio'].append(item)
                elif tipo_rep == 'EstadoResultados':
                    grp = _grupo_estado(cat)
                    if grp == 'ingresos':
                        datos['cuentas_pers_ingresos'].append(item)
                    elif grp == 'costos':
                        datos['cuentas_pers_costos'].append(item)
                    elif grp == 'gastos':
                        datos['cuentas_pers_gastos'].append(item)
                    elif grp == 'otros_gastos':
                        item['monto_raw'] = monto
                        item['monto'] = -abs(monto)
                        item['es_gasto_otro'] = True
                        datos['cuentas_pers_otros'].append(item)
                    else:
                        item['monto_raw'] = monto
                        item['es_gasto_otro'] = False
                        datos['cuentas_pers_otros'].append(item)
        except Exception as e_aj:
            print(f"Aviso leyendo CuentasContablesAjustes: {e_aj}")

        total_ingresos_pers = sum(c['monto'] for c in datos['cuentas_pers_ingresos'])
        total_costos_pers = sum(c['monto'] for c in datos['cuentas_pers_costos'])
        total_gastos_pers = sum(c['monto'] for c in datos['cuentas_pers_gastos'])
        total_otros_pers = sum(c['monto'] for c in datos['cuentas_pers_otros'])

        # Recalcular ventas, costos y utilidad bruta considerando ediciones o reubicaciones de cuentas base
        nuevo_ingresos_base = round(datos['mano_obra_mes'] + datos['repuestos_taller_mes'] + datos['mostrador_mes'], 2)
        delta_ingresos_base = round(nuevo_ingresos_base - orig_ingresos_base, 2)
        nuevo_costo_base = round(datos['costo_repuestos_taller'] + datos['costo_mostrador'], 2)
        delta_costo_base = round(nuevo_costo_base - orig_costo_base, 2)

        datos['repuestos_mes'] = round(datos['repuestos_taller_mes'] + datos['mostrador_mes'], 2)
        datos['ventas_netas'] = round(datos['ventas_netas'] + delta_ingresos_base + total_ingresos_pers, 2)
        datos['costo_ventas'] = round(datos['costo_ventas'] + delta_costo_base + total_costos_pers, 2)
        datos['utilidad_bruta'] = round(datos['ventas_netas'] - datos['costo_ventas'], 2)
        datos['margen_bruto_pct'] = round((datos['utilidad_bruta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0
        datos['margen_bruto_pct'] = round((datos['utilidad_bruta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        datos['gastos_nomina_total'] = round(
            datos['gastos_nomina_base'] + 
            datos['gastos_cargas_patronales'] + 
            datos['gastos_provisiones_laborales'], 2
        )
        datos['gastos_planilla'] = datos['gastos_nomina_total']

        # 5.1 Gastos Operativos y Conciliación Integral de Arqueos de Caja (ControlCaja)
        datos['gastos_operativos_base'] = round(
            datos['gastos_servicios_basicos'] + 
            datos['gastos_alquiler'] + 
            datos['gastos_mantenimiento'] + 
            datos['gastos_otros'] + 
            datos['gastos_nomina_total'] + 
            datos['gastos_mercadotecnia'] + 
            total_gastos_pers, 2
        )

        cursor.execute('''
            SELECT 
                CajaID, MontoInicial, MontoFinal, EfectivoFisico, Estado, Diferencia, FechaApertura, FechaCierre
            FROM ControlCaja 
            WHERE MONTH(FechaApertura) = ? AND YEAR(FechaApertura) = ? 
            ORDER BY CajaID DESC
        ''', (mes, anio))
        cajas_periodo = cursor.fetchall()
        if not cajas_periodo:
            cursor.execute('''
                SELECT TOP 1 
                    CajaID, MontoInicial, MontoFinal, EfectivoFisico, Estado, Diferencia, FechaApertura, FechaCierre
                FROM ControlCaja 
                ORDER BY CajaID DESC
            ''')
            latest_c = cursor.fetchone()
            cajas_periodo = [latest_c] if latest_c else []

        # Arqueo de Caja: calcular Faltantes (gasto por faltante) y Sobrantes (otros ingresos)
        total_faltante_caja = 0.0
        total_sobrante_caja = 0.0
        for c_item in cajas_periodo:
            if c_item[4] == 'Cerrada':
                dif_val = float(c_item[5] or 0.0) if len(c_item) > 5 and c_item[5] is not None else 0.0
                if dif_val < -0.001:
                    total_faltante_caja += abs(dif_val)
                elif dif_val > 0.001:
                    total_sobrante_caja += dif_val

        datos['faltante_caja'] = round(total_faltante_caja, 2)
        datos['sobrante_caja'] = round(total_sobrante_caja, 2)

        # Si hay faltante de arqueo en caja cerrada, se registra contablemente como gasto operativo
        if total_faltante_caja > 0:
            datos['gastos_faltante_caja'] = round(total_faltante_caja, 2)
            datos['gastos_desglose'].append({
                'categoria': 'Arqueo de Caja',
                'descripcion': 'Pérdida por Faltante en Arqueo de Caja',
                'monto': round(total_faltante_caja, 2),
                'fecha': periodo_texto
            })
        else:
            datos['gastos_faltante_caja'] = 0.0

        datos['gastos_operativos'] = round(datos['gastos_operativos_base'] + datos['gastos_faltante_caja'], 2)

        datos['utilidad_operativa'] = round(datos['utilidad_bruta'] - datos['gastos_operativos'], 2)
        datos['margen_operativo_pct'] = round((datos['utilidad_operativa'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        # Impuesto sobre la Renta (Pago mínimo definitivo 1% DGI o provisión si hay utilidad)
        if datos['utilidad_operativa'] > 0:
            datos['impuesto_renta_ir'] = round(max(datos['ventas_netas'] * 0.01, datos['utilidad_operativa'] * 0.10), 2)
        else:
            datos['impuesto_renta_ir'] = 0.0

        # Si hay sobrante de caja, se incorpora en Otros Ingresos Operacionales
        datos['otros_ingresos_gastos'] = round(total_otros_pers + total_sobrante_caja, 2)
        datos['utilidad_neta'] = round(datos['utilidad_operativa'] - datos['impuesto_renta_ir'] + datos['otros_ingresos_gastos'], 2)
        datos['margen_neto_pct'] = round((datos['utilidad_neta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        # 6. BALANCE GENERAL - ACTIVOS CORRIENTES (100% Automático y Conciliado con Arqueo de Caja)
        saldo_caja = 0.0
        if cajas_periodo:
            c_top = cajas_periodo[0]
            cid, m_ini, m_fin, ef_fis, est = c_top[0], c_top[1], c_top[2], c_top[3], c_top[4]
            if est == 'Abierta':
                cursor.execute("SELECT ISNULL(SUM(TotalNeto), 0) FROM Facturas WHERE CajaID = ? AND Estado = 'Pagada'", (cid,))
                v_row = cursor.fetchone()
                total_v = float(v_row[0] or 0.0) if v_row else 0.0
                saldo_caja = float(m_ini or 0.0) + total_v
            else:
                # Si la caja está cerrada, el saldo real en poder del taller es el Efectivo Físico Arqueado
                if ef_fis is not None and (ef_fis > 0 or (m_fin is not None and m_fin == 0)):
                    saldo_caja = float(ef_fis)
                else:
                    saldo_caja = float(m_fin or 0.0)
        if not datos.get('ajuste_id_efectivo_caja') and not datos.get('ocultar_efectivo_caja'):
            datos['efectivo_caja'] = round(saldo_caja, 2)

        # Inventario de Mercaderías y Repuestos al Costo
        cursor.execute("SELECT ISNULL(SUM(StockActual * PrecioCompra), 0), COUNT(*) FROM Productos WHERE Activo = 1")
        inv_row = cursor.fetchone()
        costo_inv_bd = float(inv_row[0] or 0.0) if inv_row else 0.0
        cant_articulos = int(inv_row[1] or 0) if inv_row else 0
        if not datos.get('ajuste_id_inventario_costo') and not datos.get('ocultar_inventario_costo'):
            datos['inventario_costo'] = costo_inv_bd
        datos['articulos_inventario'] = cant_articulos

        # Cuentas por cobrar clientes (servicios y ventas pendientes de cobro)
        cursor.execute("""
            SELECT 
                ISNULL((SELECT SUM(TotalNeto) FROM Facturas WHERE Estado = 'Pendiente' AND MONTH(FechaEmision) = ? AND YEAR(FechaEmision) = ?), 0) +
                ISNULL((SELECT SUM(mo.CostoSugerido) FROM OrdenManoObra mo JOIN OrdenesTrabajo ot ON mo.OrdenID = ot.OrdenID WHERE ot.Estado IN ('Pendiente de Pago', 'Finalizado') AND NOT EXISTS (SELECT 1 FROM Facturas f WHERE f.OrdenID = ot.OrdenID AND f.Estado = 'Pagada')), 0) +
                ISNULL((SELECT SUM(r.Cantidad * p.PrecioVenta) FROM OrdenRepuestos r JOIN Productos p ON r.ProductoID = p.ProductoID JOIN OrdenesTrabajo ot ON r.OrdenID = ot.OrdenID WHERE ot.Estado IN ('Pendiente de Pago', 'Finalizado') AND NOT EXISTS (SELECT 1 FROM Facturas f WHERE f.OrdenID = ot.OrdenID AND f.Estado = 'Pagada')), 0)
        """, (mes, anio))
        cpc_row = cursor.fetchone()
        cpc_val = float(cpc_row[0] or 0.0) if cpc_row else 0.0
        if not datos.get('ajuste_id_cuentas_por_cobrar') and not datos.get('ocultar_cuentas_por_cobrar'):
            datos['cuentas_por_cobrar'] = cpc_val
        
        cursor.execute("SELECT ISNULL(SUM(ISNULL(IVA, TotalCompra * 0.15)), 0) FROM Compras WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?", (mes, anio))
        iva_compras_row = cursor.fetchone()
        iva_credito_val = float(iva_compras_row[0] or 0.0) if iva_compras_row else 0.0
        if not datos.get('ajuste_id_credito_fiscal_iva') and not datos.get('ocultar_credito_fiscal_iva'):
            datos['credito_fiscal_iva'] = round(iva_credito_val, 2)
        total_act_corr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_activo_corriente', []))
        total_act_nocorr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_activo_no_corriente', []))

        datos['activo_circulante'] = round(datos['efectivo_caja'] + datos['inventario_costo'] + datos['cuentas_por_cobrar'] + datos['credito_fiscal_iva'] + total_act_corr_pers, 2)

        # BALANCE GENERAL - ACTIVOS NO CORRIENTES
        datos['activo_fijo_total'] = round(
            datos['activo_fijo_maquinaria'] + 
            datos['activo_fijo_herramientas'] + 
            datos['activo_fijo_mobiliario'] + 
            datos['depreciacion_acumulada'] + 
            total_act_nocorr_pers, 2
        )
        datos['activo_fijo_estimado'] = datos['activo_fijo_total']
        datos['activo_total'] = round(datos['activo_circulante'] + datos['activo_fijo_total'], 2)

        # BALANCE GENERAL - PASIVOS CORRIENTES
        cursor.execute("SELECT ISNULL(SUM(TotalCompra), 0) FROM Compras WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?", (mes, anio))
        prov_compras_row = cursor.fetchone()
        prov_val = float(prov_compras_row[0] or 0.0) if prov_compras_row else 0.0
        if not datos.get('ajuste_id_proveedores_por_pagar') and not datos.get('ocultar_proveedores_por_pagar'):
            datos['proveedores_por_pagar'] = prov_val
        if not datos.get('ajuste_id_iva_por_enterar') and not datos.get('ocultar_iva_por_enterar'):
            datos['iva_por_enterar'] = round(max(0.0, datos['iva_debito_fiscal'] - datos['credito_fiscal_iva']), 2)
        if not datos.get('ajuste_id_retenciones_dgi') and not datos.get('ocultar_retenciones_dgi'):
            ret_ir = float(tot_nom.get('ir', 0.0) or 0.0)
            ret_min = round(datos['ventas_netas'] * 0.01, 2) if datos['ventas_netas'] > 0 else 0.0
            datos['retenciones_dgi'] = round(ret_ir + ret_min, 2)
        if not datos.get('ajuste_id_obligaciones_laborales') and not datos.get('ocultar_obligaciones_laborales'):
            # Cargas patronales (INSS 22.5% + INATEC 2%) + INSS laboral (7%) pendientes de enterar al INSS
            inss_total = float(tot_nom.get('cargas_patronales', 0.0) or 0.0) + float(tot_nom.get('inss_laboral', 0.0) or 0.0)
            salarios_pend = sum(e['salario_neto'] for e in totales_nom.get('todos', []) if not e.get('pagado', False))
            datos['obligaciones_laborales'] = round(inss_total + salarios_pend, 2)
        
        total_pas_corr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_pasivo_corriente', []))
        total_pas_nocorr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_pasivo_no_corriente', []))
        total_patri_pers = sum(c['monto'] for c in datos.get('cuentas_pers_patrimonio', []))

        datos['pasivo_circulante'] = round(
            datos['proveedores_por_pagar'] + 
            datos['iva_por_enterar'] + 
            datos['retenciones_dgi'] + 
            datos['obligaciones_laborales'] + 
            total_pas_corr_pers, 2
        )
        if not datos.get('ajuste_id_pasivo_largo_plazo') and not datos.get('ocultar_pasivo_largo_plazo'):
            datos['pasivo_largo_plazo'] = 0.0
        datos['pasivo_largo_plazo'] = round(datos['pasivo_largo_plazo'] + total_pas_nocorr_pers, 2)
        datos['pasivo_total'] = round(datos['pasivo_circulante'] + datos['pasivo_largo_plazo'], 2)

        # BALANCE GENERAL - PATRIMONIO NETO (NIIF PARA LAS MIPYMES)
        # Regla de oro de la partida doble: Activo = Pasivo + Patrimonio
        datos['utilidad_ejercicio'] = datos['utilidad_neta']
        datos['capital_social'] = 0.0 if datos.get('ocultar_capital_social') else datos.get('capital_social', 150000.0)
        datos['ajustes_patrimonio_total'] = round(total_patri_pers, 2)
        
        # Las utilidades acumuladas reflejan el saldo real de ejercicios anteriores o ajuste manual del usuario (sin inventar cifras)
        if not datos.get('ajuste_id_utilidades_acumuladas') and not datos.get('ocultar_utilidades_acumuladas'):
            datos['utilidades_acumuladas'] = float(datos.get('utilidades_acumuladas', 0.0) or 0.0)

        datos['patrimonio'] = round(datos['capital_social'] + datos['utilidades_acumuladas'] + datos['utilidad_ejercicio'] + datos['ajustes_patrimonio_total'], 2)

        datos['pasivo_mas_patrimonio'] = round(datos['pasivo_total'] + datos['patrimonio'], 2)
        datos['diferencia_cuadre'] = round(datos['activo_total'] - datos['pasivo_mas_patrimonio'], 2)
        datos['cuadra'] = abs(datos['diferencia_cuadre']) < 0.01

        # Ratios / Razones Financieras
        datos['razon_circulante'] = round(datos['activo_circulante'] / datos['pasivo_circulante'], 2) if datos['pasivo_circulante'] > 0 else 0.0
        datos['capital_trabajo'] = round(datos['activo_circulante'] - datos['pasivo_circulante'], 2)
        datos['endeudamiento_pct'] = round((datos['pasivo_total'] / datos['activo_total']) * 100, 2) if datos['activo_total'] > 0 else 0.0
        datos['autonomia_financiera'] = round(datos['patrimonio'] / datos['pasivo_total'], 2) if datos['pasivo_total'] > 0 else 0.0
        datos['rotacion_inventario'] = round(datos['costo_ventas'] / datos['inventario_costo'], 2) if datos['inventario_costo'] > 0 else 0.0
        datos['dias_inventario'] = round(365 / datos['rotacion_inventario'], 0) if datos['rotacion_inventario'] > 0 else 0

        # Cierres diarios recientes
        cursor.execute("""
            SELECT 
                fechas.Fecha,
                (SELECT ISNULL(SUM(TotalNeto), 0) FROM Facturas f JOIN ControlCaja c ON f.CajaID = c.CajaID WHERE CAST(c.FechaApertura AS DATE) = fechas.Fecha AND f.Estado = 'Pagada') as Ventas,
                (SELECT ISNULL(SUM(CostoSugerido), 0) FROM OrdenesTrabajo o JOIN OrdenManoObra m ON o.OrdenID = m.OrdenID WHERE CAST(o.FechaIngreso AS DATE) = fechas.Fecha) as Taller,
                (SELECT TOP 1 Estado FROM ControlCaja WHERE CAST(FechaApertura AS DATE) = fechas.Fecha ORDER BY CajaID DESC) as EstadoCaja
            FROM (
                SELECT CAST(FechaApertura AS DATE) as Fecha FROM ControlCaja WHERE MONTH(FechaApertura) = ? AND YEAR(FechaApertura) = ?
                UNION
                SELECT CAST(FechaIngreso AS DATE) as Fecha FROM OrdenesTrabajo WHERE MONTH(FechaIngreso) = ? AND YEAR(FechaIngreso) = ?
            ) fechas
            ORDER BY fechas.Fecha DESC
        """, (mes, anio, mes, anio))
        dias_cierres = cursor.fetchall()
        for d in dias_cierres:
            v = float(d[1] or 0.0)
            t = float(d[2] or 0.0)
            datos['cierres_diarios'].append({
                'fecha': d[0].strftime('%d/%m/%Y') if hasattr(d[0], 'strftime') else str(d[0]),
                'ventas': v,
                'taller': t,
                'total': v + t,
                'estado': d[3] or 'Cerrada'
            })

    except Exception as e:
        print(f"Error calculando datos financieros del taller para {mes}/{anio}: {e}")
    finally:
        conn.close()

    return datos

@contador_bp.route('/')
@contador_required
def index():
    return redirect(url_for('contador.balance'))

# ==============================================================================
# MÓDULO CONTABILIDAD: BALANCE GENERAL (SITUACIÓN FINANCIERA)
# ==============================================================================
@contador_bp.route('/balance', methods=['GET', 'POST'])
@contador_required
def balance():
    ahora = datetime.now()
    mes = request.args.get('mes', default=ahora.month, type=int)
    anio = request.args.get('anio', default=ahora.year, type=int)
    ver_vivo = request.args.get('ver_vivo', default='0') == '1'

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action', 'guardar_cierre')

        if action == 'recalcular_vivo':
            # Elimina el reporte cerrado para forzar lectura en vivo
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'Balance' AND Mes = ? AND Anio = ?", (mes, anio))
            conn.commit()
            conn.close()
            flash(f"Balance General de {MESES_ES[mes]} {anio} recalculado en vivo con los últimos movimientos del taller.", "success")
            return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))

        elif action == 'guardar_cierre':
            # Guarda snapshot oficial auditado en ReportesContables
            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'Balance' AND Mes = ? AND Anio = ?", (mes, anio))
            cursor.execute("""
                INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                VALUES (?, 'Balance', ?, ?, ?, GETDATE())
            """, (session['usuario_id'], mes, anio, json.dumps(fin)))
            conn.commit()
            conn.close()
            flash(f"Cierre Contable Oficial de Balance General para {MESES_ES[mes]} {anio} sellado exitosamente.", "success")
            return redirect(url_for('contador.balance', mes=mes, anio=anio))

        elif action == 'desellar_cierre':
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'Balance' AND Mes = ? AND Anio = ?", (mes, anio))
            conn.commit()
            conn.close()
            flash(f"Balance General de {MESES_ES[mes]} {anio} desellado. Las razones financieras volverán a permanecer en 0 hasta sellar nuevamente.", "success")
            return redirect(url_for('contador.balance', mes=mes, anio=anio))

        elif action == 'ajuste_manual':
            # Guarda un ajuste manual en ReportesContables
            activo_nombres = request.form.getlist('activo_nombres[]')
            activo_montos = request.form.getlist('activo_montos[]')
            pasivo_nombres = request.form.getlist('pasivo_nombres[]')
            pasivo_montos = request.form.getlist('pasivo_montos[]')
            patri_nombres = request.form.getlist('patrimonio_nombres[]')
            patri_montos = request.form.getlist('patrimonio_montos[]')

            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
            fin['activos_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(activo_nombres, activo_montos) if n.strip()]
            fin['pasivos_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(pasivo_nombres, pasivo_montos) if n.strip()]
            fin['patrimonio_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(patri_nombres, patri_montos) if n.strip()]

            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'Balance' AND Mes = ? AND Anio = ?", (mes, anio))
            cursor.execute("""
                INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                VALUES (?, 'Balance', ?, ?, ?, GETDATE())
            """, (session['usuario_id'], mes, anio, json.dumps(fin)))
            conn.commit()
            conn.close()
            flash(f"Ajuste contable guardado para {MESES_ES[mes]} {anio}.", "success")
            return redirect(url_for('contador.balance', mes=mes, anio=anio))

    # GET: Verificar si existe un cierre oficial sellado
    cursor.execute("""
        SELECT rc.DatosJSON, rc.FechaCreacion, u.NombreCompleto 
        FROM ReportesContables rc
        LEFT JOIN Usuarios u ON rc.UsuarioID = u.UsuarioID
        WHERE rc.TipoReporte = 'Balance' AND rc.Mes = ? AND rc.Anio = ?
    """, (mes, anio))
    cierre_row = cursor.fetchone()
    conn.close()

    es_oficial_cerrado = False
    fecha_cierre_str = None
    autor_cierre = None

    if cierre_row and not ver_vivo:
        try:
            fin = json.loads(cierre_row[0])
            es_oficial_cerrado = True
            fecha_cierre_str = cierre_row[1].strftime('%d/%m/%Y %I:%M %p') if cierre_row[1] else None
            autor_cierre = cierre_row[2] or "Contador General"
            fin['periodos_disponibles'] = obtener_periodos_disponibles()
        except Exception:
            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
    else:
        fin = obtener_datos_financieros_taller(mes=mes, anio=anio)

    return render_template(
        'contador/balance.html',
        fin=fin,
        mes_seleccionado=mes,
        anio_seleccionado=anio,
        es_oficial_cerrado=es_oficial_cerrado,
        fecha_cierre_str=fecha_cierre_str,
        autor_cierre=autor_cierre,
        
    )

# ==============================================================================
# MÓDULO CONTABILIDAD: ESTADO DE RESULTADOS (PÉRDIDAS Y GANANCIAS)
# ==============================================================================
@contador_bp.route('/estado_resultados', methods=['GET', 'POST'])
@contador_required
def estado_resultados():
    ahora = datetime.now()
    mes = request.args.get('mes', default=ahora.month, type=int)
    anio = request.args.get('anio', default=ahora.year, type=int)
    ver_vivo = request.args.get('ver_vivo', default='0') == '1'

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action', 'guardar_cierre')

        if action == 'recalcular_vivo':
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'EstadoResultados' AND Mes = ? AND Anio = ?", (mes, anio))
            conn.commit()
            conn.close()
            flash(f"Estado de Resultados de {MESES_ES[mes]} {anio} recalculado en vivo.", "success")
            return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))

        elif action == 'guardar_cierre':
            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'EstadoResultados' AND Mes = ? AND Anio = ?", (mes, anio))
            cursor.execute("""
                INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                VALUES (?, 'EstadoResultados', ?, ?, ?, GETDATE())
            """, (session['usuario_id'], mes, anio, json.dumps(fin)))
            conn.commit()
            conn.close()
            flash(f"Estado de Resultados Oficial de {MESES_ES[mes]} {anio} sellado exitosamente.", "success")
            return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio))

        elif action == 'desellar_cierre':
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'EstadoResultados' AND Mes = ? AND Anio = ?", (mes, anio))
            conn.commit()
            conn.close()
            flash(f"Estado de Resultados de {MESES_ES[mes]} {anio} desellado. Las razones financieras permanecerán en 0 hasta sellar nuevamente.", "success")
            return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio))

        elif action == 'ajuste_manual':
            ing_nombres = request.form.getlist('ingresos_nombres[]')
            ing_montos = request.form.getlist('ingresos_montos[]')
            cost_nombres = request.form.getlist('costos_nombres[]')
            cost_montos = request.form.getlist('costos_montos[]')
            gas_nombres = request.form.getlist('gastos_nombres[]')
            gas_montos = request.form.getlist('gastos_montos[]')

            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
            fin['ingresos_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(ing_nombres, ing_montos) if n.strip()]
            fin['costos_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(cost_nombres, cost_montos) if n.strip()]
            fin['gastos_ajuste'] = [{'nombre': n, 'monto': float(m or 0)} for n, m in zip(gas_nombres, gas_montos) if n.strip()]

            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = 'EstadoResultados' AND Mes = ? AND Anio = ?", (mes, anio))
            cursor.execute("""
                INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                VALUES (?, 'EstadoResultados', ?, ?, ?, GETDATE())
            """, (session['usuario_id'], mes, anio, json.dumps(fin)))
            conn.commit()
            conn.close()
            flash(f"Ajuste guardado para Estado de Resultados {MESES_ES[mes]} {anio}.", "success")
            return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio))

    cursor.execute("""
        SELECT rc.DatosJSON, rc.FechaCreacion, u.NombreCompleto 
        FROM ReportesContables rc
        LEFT JOIN Usuarios u ON rc.UsuarioID = u.UsuarioID
        WHERE rc.TipoReporte = 'EstadoResultados' AND rc.Mes = ? AND rc.Anio = ?
    """, (mes, anio))
    cierre_row = cursor.fetchone()
    conn.close()

    es_oficial_cerrado = False
    fecha_cierre_str = None
    autor_cierre = None
    es_mes_actual = (mes == ahora.month and anio == ahora.year)

    if cierre_row and not ver_vivo:
        try:
            fin = json.loads(cierre_row[0])
            es_oficial_cerrado = True
            fecha_cierre_str = cierre_row[1].strftime('%d/%m/%Y %I:%M %p') if cierre_row[1] else None
            autor_cierre = cierre_row[2] or "Contador General"
            fin['periodos_disponibles'] = obtener_periodos_disponibles()
        except Exception:
            fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
    else:
        fin = obtener_datos_financieros_taller(mes=mes, anio=anio)

    return render_template(
        'contador/estado_resultados.html',
        fin=fin,
        mes_seleccionado=mes,
        anio_seleccionado=anio,
        es_oficial_cerrado=es_oficial_cerrado,
        fecha_cierre_str=fecha_cierre_str,
        autor_cierre=autor_cierre,
        
    )

# ==============================================================================
# MÓDULO CONTABILIDAD: RESUMEN CONTABLE CONSOLIDADO
# ==============================================================================
@contador_bp.route('/resumen_contable')
@contador_required
def resumen_contable():
    return redirect(url_for('contador.balance'))

# ==============================================================================
# MÓDULO CONTABILIDAD: HISTORIAL MENSUAL COMPARATIVO (ESTADO Y BALANCE)
# ==============================================================================
@contador_bp.route('/historial')
@contador_required
def historial():
    ahora = datetime.now()
    anio = request.args.get('anio', default=ahora.year, type=int)
    vista = request.args.get('vista', default='ambos')  # 'ambos', 'estado', 'balance'
    solo_movimientos = request.args.get('solo_movimientos', default='0') == '1'

    conn = get_db_connection()
    anios_disponibles = set([ahora.year])
    meses_con_datos = set()
    cierres_guardados = set()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT YEAR(FechaEmision) FROM Facturas WHERE FechaEmision IS NOT NULL
                UNION
                SELECT DISTINCT YEAR(FechaGasto) FROM GastosOperativos WHERE FechaGasto IS NOT NULL
                UNION
                SELECT DISTINCT YEAR(FechaCompra) FROM Compras WHERE FechaCompra IS NOT NULL
                UNION
                SELECT DISTINCT Anio FROM ReportesContables WHERE Anio IS NOT NULL
            """)
            for r in cursor.fetchall():
                if r[0]:
                    anios_disponibles.add(int(r[0]))

            cursor.execute("SELECT DISTINCT MONTH(FechaEmision) FROM Facturas WHERE YEAR(FechaEmision) = ? AND FechaEmision IS NOT NULL", (anio,))
            for r in cursor.fetchall():
                if r[0]: meses_con_datos.add(int(r[0]))

            cursor.execute("SELECT DISTINCT MONTH(FechaGasto) FROM GastosOperativos WHERE YEAR(FechaGasto) = ? AND FechaGasto IS NOT NULL", (anio,))
            for r in cursor.fetchall():
                if r[0]: meses_con_datos.add(int(r[0]))

            cursor.execute("SELECT DISTINCT MONTH(FechaCompra) FROM Compras WHERE YEAR(FechaCompra) = ? AND FechaCompra IS NOT NULL", (anio,))
            for r in cursor.fetchall():
                if r[0]: meses_con_datos.add(int(r[0]))

            cursor.execute("SELECT DISTINCT Mes FROM ReportesContables WHERE Anio = ? AND Mes IS NOT NULL", (anio,))
            for r in cursor.fetchall():
                if r[0]: meses_con_datos.add(int(r[0]))

            cursor.execute("SELECT TipoReporte, Mes FROM ReportesContables WHERE Anio = ?", (anio,))
            for r in cursor.fetchall():
                if r[0] and r[1]:
                    cierres_guardados.add((r[0], int(r[1])))
        except Exception as e:
            print(f"Error consultando historial contable: {e}")
        finally:
            conn.close()

    if anio == ahora.year:
        meses_con_datos.add(ahora.month)

    lista_anios = sorted(list(anios_disponibles), reverse=True)
    historial_meses = []

    totales = {
        'ventas_netas': 0.0,
        'costo_ventas': 0.0,
        'utilidad_bruta': 0.0,
        'gastos_operativos': 0.0,
        'utilidad_operativa': 0.0,
        'utilidad_neta': 0.0,
        'impuesto_renta_ir': 0.0,
        'facturas_total': 0,
        'meses_con_actividad': 0,
        'mejor_mes_ventas': 'N/D',
        'mejor_ventas_monto': -1.0,
        'mejor_mes_utilidad': 'N/D',
        'mejor_utilidad_monto': -99999999.0
    }

    suma_activos = 0.0
    suma_pasivos = 0.0
    suma_patrimonio = 0.0

    for m in range(1, 13):
        es_mes_actual = (m == ahora.month and anio == ahora.year)
        tiene_mov = (m in meses_con_datos)

        if solo_movimientos and not tiene_mov:
            continue

        cierre_balance = ('Balance', m) in cierres_guardados
        cierre_estado = ('EstadoResultados', m) in cierres_guardados

        if tiene_mov:
            fin = obtener_datos_financieros_taller(mes=m, anio=anio)
            v_netas = fin.get('ventas_netas', 0.0)
            c_ventas = fin.get('costo_ventas', 0.0)
            u_bruta = fin.get('utilidad_bruta', 0.0)
            m_bruto = fin.get('margen_bruto_pct', 0.0)
            g_oper = fin.get('gastos_operativos', 0.0)
            u_oper = fin.get('utilidad_operativa', 0.0)
            ir = fin.get('impuesto_renta_ir', 0.0)
            u_neta = fin.get('utilidad_neta', 0.0)
            m_neto = fin.get('margen_neto_pct', 0.0)
            fac_cant = fin.get('facturas_cantidad', 0)

            act_circ = fin.get('activo_circulante', 0.0)
            act_fijo = fin.get('activo_fijo_neto', 0.0)
            act_tot = fin.get('activo_total', 0.0)
            pas_circ = fin.get('pasivo_circulante', 0.0)
            pas_largo = fin.get('pasivo_largo_plazo', 0.0)
            pas_tot = fin.get('pasivo_total', 0.0)
            pat_tot = fin.get('patrimonio_total', 0.0)
            cap_trabajo = round(act_circ - pas_circ, 2)
            balance_ok = abs(act_tot - (pas_tot + pat_tot)) < 0.1

            totales['ventas_netas'] += v_netas
            totales['costo_ventas'] += c_ventas
            totales['utilidad_bruta'] += u_bruta
            totales['gastos_operativos'] += g_oper
            totales['utilidad_operativa'] += u_oper
            totales['impuesto_renta_ir'] += ir
            totales['utilidad_neta'] += u_neta
            totales['facturas_total'] += fac_cant
            totales['meses_con_actividad'] += 1

            suma_activos += act_tot
            suma_pasivos += pas_tot
            suma_patrimonio += pat_tot

            if v_netas > totales['mejor_ventas_monto']:
                totales['mejor_ventas_monto'] = v_netas
                totales['mejor_mes_ventas'] = MESES_ES[m]

            if u_neta > totales['mejor_utilidad_monto']:
                totales['mejor_utilidad_monto'] = u_neta
                totales['mejor_mes_utilidad'] = MESES_ES[m]
        else:
            v_netas = 0.0
            c_ventas = 0.0
            u_bruta = 0.0
            m_bruto = 0.0
            g_oper = 0.0
            u_oper = 0.0
            ir = 0.0
            u_neta = 0.0
            m_neto = 0.0
            fac_cant = 0

            act_circ = 0.0
            act_fijo = 187000.0
            act_tot = 187000.0
            pas_circ = 0.0
            pas_largo = 0.0
            pas_tot = 0.0
            pat_tot = 187000.0
            cap_trabajo = 0.0
            balance_ok = True

        historial_meses.append({
            'mes': m,
            'nombre_mes': MESES_ES[m],
            'periodo_texto': f"{MESES_ES[m]} {anio}",
            'es_actual': es_mes_actual,
            'tiene_movimiento': tiene_mov,
            'cierre_balance': cierre_balance,
            'cierre_estado': cierre_estado,
            # Estado de Resultados
            'ventas_netas': v_netas,
            'costo_ventas': c_ventas,
            'utilidad_bruta': u_bruta,
            'margen_bruto_pct': m_bruto,
            'gastos_operativos': g_oper,
            'utilidad_operativa': u_oper,
            'impuesto_renta_ir': ir,
            'utilidad_neta': u_neta,
            'margen_neto_pct': m_neto,
            'facturas_cantidad': fac_cant,
            # Balance General
            'activo_circulante': act_circ,
            'activo_fijo_neto': act_fijo,
            'activo_total': act_tot,
            'pasivo_circulante': pas_circ,
            'pasivo_largo_plazo': pas_largo,
            'pasivo_total': pas_tot,
            'patrimonio_total': pat_tot,
            'capital_trabajo': cap_trabajo,
            'balance_ok': balance_ok
        })

    act_count = max(totales['meses_con_actividad'], 1)
    totales['margen_bruto_anual_pct'] = round((totales['utilidad_bruta'] / totales['ventas_netas'] * 100), 1) if totales['ventas_netas'] > 0 else 0.0
    totales['margen_neto_anual_pct'] = round((totales['utilidad_neta'] / totales['ventas_netas'] * 100), 1) if totales['ventas_netas'] > 0 else 0.0
    totales['promedio_ventas_mensual'] = round(totales['ventas_netas'] / act_count, 2)
    totales['promedio_utilidad_mensual'] = round(totales['utilidad_neta'] / act_count, 2)
    totales['promedio_activo_total'] = round(suma_activos / act_count, 2) if act_count > 0 else 0.0

    return render_template(
        'contador/historial.html',
        historial_meses=historial_meses,
        totales=totales,
        anio_seleccionado=anio,
        mes_actual=ahora.month,
        lista_anios=lista_anios,
        vista=vista,
        solo_movimientos=solo_movimientos
    )

# ==============================================================================
# MOTOR ANALÍTICO DE RAZONES FINANCIERAS (5 CATEGORÍAS)
# ==============================================================================
def safe_div(num, den, default=0.0):
    """División segura que evita ZeroDivisionError retornando default si el denominador es 0."""
    try:
        num = float(num or 0)
        den = float(den or 0)
        if den == 0.0 or abs(den) < 1e-9:
            return default
        return round(num / den, 2)
    except (ZeroDivisionError, ValueError, TypeError):
        return default

def verificar_cierre_estados(mes, anio, conn=None):
    """
    Verifica en ReportesContables si el Balance General y el Estado de Resultados
    fueron sellados y cerrados oficialmente para el mes y año dados.
    Para una MiPyME, las razones financieras solo se calculan sobre estados cerrados;
    mientras tanto, permanecen en 0.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    info = {
        'ambos_cerrados': False,
        'balance_cerrado': False,
        'estado_cerrado': False,
        'fecha_balance': None,
        'autor_balance': None,
        'fecha_estado': None,
        'autor_estado': None,
        'fecha_cierre_str': None,
        'autor_cierre': None,
        'datos_cerrados': None
    }

    if not conn:
        return info

    try:
        cursor = conn.cursor()
        # 1. Verificar Cierre de Balance General
        cursor.execute("""
            SELECT rc.DatosJSON, rc.FechaCreacion, u.NombreCompleto 
            FROM ReportesContables rc
            LEFT JOIN Usuarios u ON rc.UsuarioID = u.UsuarioID
            WHERE rc.TipoReporte = 'Balance' AND rc.Mes = ? AND rc.Anio = ?
        """, (mes, anio))
        row_b = cursor.fetchone()
        if row_b:
            info['balance_cerrado'] = True
            info['fecha_balance'] = row_b[1].strftime('%d/%m/%Y %I:%M %p') if row_b[1] else None
            info['autor_balance'] = row_b[2] or "Contador General"

        # 2. Verificar Cierre de Estado de Resultados
        cursor.execute("""
            SELECT rc.DatosJSON, rc.FechaCreacion, u.NombreCompleto 
            FROM ReportesContables rc
            LEFT JOIN Usuarios u ON rc.UsuarioID = u.UsuarioID
            WHERE rc.TipoReporte = 'EstadoResultados' AND rc.Mes = ? AND rc.Anio = ?
        """, (mes, anio))
        row_e = cursor.fetchone()
        if row_e:
            info['estado_cerrado'] = True
            info['fecha_estado'] = row_e[1].strftime('%d/%m/%Y %I:%M %p') if row_e[1] else None
            info['autor_estado'] = row_e[2] or "Contador General"

        # Si ambos están cerrados y sellados
        if info['balance_cerrado'] and info['estado_cerrado']:
            info['ambos_cerrados'] = True
            info['fecha_cierre_str'] = info['fecha_estado'] or info['fecha_balance']
            info['autor_cierre'] = info['autor_estado'] or info['autor_balance']
            try:
                datos_b = json.loads(row_b[0]) if (row_b and row_b[0]) else {}
                datos_e = json.loads(row_e[0]) if (row_e and row_e[0]) else {}
                datos_unificados = dict(datos_b)
                datos_unificados.update(datos_e)
                info['datos_cerrados'] = datos_unificados
            except Exception as ex_json:
                print(f"Aviso al parsear datosJSON oficiales: {ex_json}")
    except Exception as e:
        print(f"Error verificando cierre de estados contables: {e}")
    finally:
        if should_close and conn:
            conn.close()

    return info

def calcular_motor_razones_financieras(fin, periodo_cerrado=True):
    """
    Motor analítico que calcula las 20 razones financieras del taller agrupadas en las 5 categorías estándar:
    1. Liquidez
    2. Actividad o Rotación
    3. Endeudamiento
    4. Rentabilidad
    5. Cobertura

    Si periodo_cerrado=False, las razones financieras no se calculan formalmente
    y se reflejan en 0 (0.00x, 0.0%, 0 días, C$ 0.00) con estado Pendiente,
    cumpliendo la regla contable de MiPyME.
    """
    ventas = float(fin.get('ventas_netas', 0.0))
    costo_ventas = float(fin.get('costo_ventas', 0.0))
    utilidad_bruta = float(fin.get('utilidad_bruta', 0.0))
    utilidad_operativa = float(fin.get('utilidad_operativa', 0.0))
    utilidad_neta = float(fin.get('utilidad_neta', 0.0))
    
    activo_corriente = float(fin.get('activo_circulante', 0.0))
    inventario = float(fin.get('inventario_costo', 0.0))
    cuentas_cobrar = float(fin.get('cuentas_por_cobrar', 0.0))
    activo_fijo_neto = float(fin.get('activo_fijo_total', 200000.0))
    activo_total = float(fin.get('activo_total', 0.0))
    
    pasivo_corriente = float(fin.get('pasivo_circulante', 0.0))
    pasivo_largo_plazo = float(fin.get('pasivo_largo_plazo', 20000.0))
    pasivo_total = float(fin.get('pasivo_total', 0.0))
    proveedores = float(fin.get('proveedores_por_pagar', 0.0))
    compras_periodo = float(fin.get('compras_mes', 0.0))
    patrimonio = float(fin.get('patrimonio', 0.0))

    # Estimaciones financieras operativas para crédito y servicio de deuda
    ventas_credito = round(ventas * 0.40, 2) if ventas > 0 else 0.0
    compras_credito = round(compras_periodo * 0.70, 2) if compras_periodo > 0 else (costo_ventas * 0.30 if costo_ventas > 0 else 1.0)
    
    # Intereses bancarios sobre pasivo a largo plazo (12% anual -> 1% mensual)
    gastos_intereses = round(pasivo_largo_plazo * (0.12 / 12), 2) if pasivo_largo_plazo > 0 else 0.0
    abono_capital = round(pasivo_largo_plazo / 24, 2) if pasivo_largo_plazo > 0 else 0.0
    depreciacion_mensual = 1250.0
    ebitda = round(utilidad_operativa + depreciacion_mensual, 2)
    tasa_ir = 0.30

    razones = {
        'liquidez': [],
        'actividad': [],
        'endeudamiento': [],
        'rentabilidad': [],
        'cobertura': []
    }

    # --------------------------------------------------------------------------
    # 1. RAZONES DE LIQUIDEZ
    # --------------------------------------------------------------------------
    # 1.1 Razón Corriente
    rc = safe_div(activo_corriente, pasivo_corriente)
    if rc >= 1.5:
        rc_estado, rc_class = 'Saludable', 'success'
        rc_desc = f'Excelente liquidez: el taller dispone de C$ {rc:.2f} en activos líquidos por cada C$ 1.00 de deuda a corto plazo.'
    elif rc >= 1.0:
        rc_estado, rc_class = 'Precaución', 'warning'
        rc_desc = f'Liquidez ajustada: C$ {rc:.2f} por cada C$ 1.00 de deuda. Conviene acelerar cobros o negociar plazos.'
    else:
        rc_estado, rc_class = 'Crítico', 'danger'
        rc_desc = f'Riesgo de iliquidez: los activos corrientes (C$ {rc:.2f}) son insuficientes para cubrir deudas inmediatas.'
    razones['liquidez'].append({
        'id': 'razon_corriente',
        'nombre': 'Razón Corriente (Liquidez General)',
        'categoria': 'Liquidez',
        'formula': 'Activo Corriente / Pasivo Corriente',
        'formula_valores': f'C$ {activo_corriente:,.2f} / C$ {pasivo_corriente:,.2f}',
        'valor_raw': rc,
        'valor': f'{rc:.2f}x',
        'meta': '1.5x a 2.0x',
        'interpretacion': rc_desc,
        'estado': rc_estado,
        'badge_class': rc_class,
        'icono': 'fa-solid fa-droplet'
    })

    # 1.2 Prueba Ácida
    pa = safe_div(activo_corriente - inventario, pasivo_corriente)
    if pa >= 1.0:
        pa_estado, pa_class = 'Saludable', 'success'
        pa_desc = f'Capacidad de pago inmediata óptima (C$ {pa:.2f}) sin necesidad de liquidar el inventario de repuestos.'
    elif pa >= 0.7:
        pa_estado, pa_class = 'Precaución', 'warning'
        pa_desc = f'Cobertura moderada (C$ {pa:.2f}). Se depende en parte de vender el stock de aceites y repuestos.'
    else:
        pa_estado, pa_class = 'Crítico', 'danger'
        pa_desc = f'Cobertura inmediata deficiente (C$ {pa:.2f}). Si los repuestos no se venden, no se cubren pasivos corrientes.'
    razones['liquidez'].append({
        'id': 'prueba_acida',
        'nombre': 'Prueba Ácida (Liquidez Inmediata)',
        'categoria': 'Liquidez',
        'formula': '(Activo Corriente - Inventarios) / Pasivo Corriente',
        'formula_valores': f'(C$ {activo_corriente:,.2f} - C$ {inventario:,.2f}) / C$ {pasivo_corriente:,.2f}',
        'valor_raw': pa,
        'valor': f'{pa:.2f}x',
        'meta': '>= 1.0x',
        'interpretacion': pa_desc,
        'estado': pa_estado,
        'badge_class': pa_class,
        'icono': 'fa-solid fa-flask-vial'
    })

    # 1.3 Capital de Trabajo Neto
    ctn = round(activo_corriente - pasivo_corriente, 2)
    if ctn > 0:
        ctn_estado, ctn_class = 'Saludable', 'success'
        ctn_desc = f'Fondo de maniobra positivo: C$ {ctn:,.2f} libres para operar el día a día tras cubrir compromisos a corto plazo.'
    elif ctn == 0:
        ctn_estado, ctn_class = 'Precaución', 'warning'
        ctn_desc = 'Capital de trabajo en equilibrio exacto. No existe margen de seguridad para imprevistos operativos.'
    else:
        ctn_estado, ctn_class = 'Crítico', 'danger'
        ctn_desc = f'Déficit operativo (-C$ {abs(ctn):,.2f}). El taller opera con pasivos vencidos que superan sus activos líquidos.'
    razones['liquidez'].append({
        'id': 'capital_trabajo',
        'nombre': 'Capital de Trabajo Neto (CTN)',
        'categoria': 'Liquidez',
        'formula': 'Activo Corriente - Pasivo Corriente',
        'formula_valores': f'C$ {activo_corriente:,.2f} - C$ {pasivo_corriente:,.2f}',
        'valor_raw': ctn,
        'valor': f'C$ {ctn:,.2f}',
        'meta': '> C$ 0.00',
        'interpretacion': ctn_desc,
        'estado': ctn_estado,
        'badge_class': ctn_class,
        'icono': 'fa-solid fa-wallet'
    })

    # --------------------------------------------------------------------------
    # 2. RAZONES DE ACTIVIDAD O ROTACIÓN
    # --------------------------------------------------------------------------
    # 2.1 Rotación de Inventarios
    rot_inv = safe_div(costo_ventas, inventario)
    dias_inv = safe_div(360, rot_inv) if rot_inv > 0 else 0
    if rot_inv >= 1.5:
        ri_estado, ri_class = 'Saludable', 'success'
        ri_desc = f'Excelente dinámica comercial: el stock de repuestos y aceites se renueva {rot_inv:.2f} veces en el período.'
    elif rot_inv >= 0.5:
        ri_estado, ri_class = 'Precaución', 'warning'
        ri_desc = f'Rotación moderada ({rot_inv:.2f} veces). Los repuestos tardan {dias_inv:.0f} días en salir de bodega.'
    else:
        ri_estado, ri_class = 'Crítico', 'danger'
        ri_desc = f'Baja rotación ({rot_inv:.2f} veces). Exceso de stock inmovilizado en estanterías.'
    razones['actividad'].append({
        'id': 'rotacion_inventarios',
        'nombre': 'Rotación de Inventarios',
        'categoria': 'Actividad',
        'formula': 'Costo de Ventas / Inventario Promedio',
        'formula_valores': f'C$ {costo_ventas:,.2f} / C$ {inventario:,.2f}',
        'valor_raw': rot_inv,
        'valor': f'{rot_inv:.2f} veces',
        'meta': '>= 1.5x',
        'interpretacion': ri_desc,
        'estado': ri_estado,
        'badge_class': ri_class,
        'icono': 'fa-solid fa-boxes-packing'
    })

    # 2.2 Días de Inventario (Permanencia)
    razones['actividad'].append({
        'id': 'dias_inventario',
        'nombre': 'Días de Inventario (Permanencia)',
        'categoria': 'Actividad',
        'formula': '360 / Rotación de Inventarios',
        'formula_valores': f'360 / {rot_inv:.2f}',
        'valor_raw': dias_inv,
        'valor': f'{dias_inv:.0f} días' if dias_inv > 0 else 'N/A',
        'meta': '<= 90 días',
        'interpretacion': f'Un repuesto o lubricante pasa en promedio {dias_inv:.0f} días almacenado antes de venderse o instalarse.' if dias_inv > 0 else 'Sin rotación de inventario cuantificable en el período.',
        'estado': 'Saludable' if (0 < dias_inv <= 90) else ('Precaución' if dias_inv <= 180 else 'Crítico'),
        'badge_class': 'success' if (0 < dias_inv <= 90) else ('warning' if dias_inv <= 180 else 'danger'),
        'icono': 'fa-solid fa-clock-rotate-left'
    })

    # 2.3 Rotación de Cartera
    rot_cart = safe_div(ventas_credito, cuentas_cobrar)
    dias_cobro = safe_div(360, rot_cart) if rot_cart > 0 else 0
    razones['actividad'].append({
        'id': 'rotacion_cartera',
        'nombre': 'Rotación de Cartera (Cuentas por Cobrar)',
        'categoria': 'Actividad',
        'formula': 'Ventas a Crédito / Cuentas por Cobrar Promedio',
        'formula_valores': f'C$ {ventas_credito:,.2f} / C$ {cuentas_cobrar:,.2f}',
        'valor_raw': rot_cart,
        'valor': f'{rot_cart:.2f} veces' if rot_cart > 0 else 'N/A',
        'meta': '>= 3.0x',
        'interpretacion': f'Las cuentas por cobrar a clientes y empresas rotan {rot_cart:.2f} veces en el período.' if rot_cart > 0 else 'Ventas operadas mayoritariamente de contado.',
        'estado': 'Saludable' if rot_cart >= 3.0 else ('Precaución' if rot_cart >= 1.0 else 'Crítico'),
        'badge_class': 'success' if rot_cart >= 3.0 else ('warning' if rot_cart >= 1.0 else 'danger'),
        'icono': 'fa-solid fa-hand-holding-dollar'
    })

    # 2.4 Periodo Promedio de Cobro (Días de Cartera)
    razones['actividad'].append({
        'id': 'periodo_cobro',
        'nombre': 'Periodo Promedio de Cobro (Días de Cartera)',
        'categoria': 'Actividad',
        'formula': '360 / Rotación de Cartera',
        'formula_valores': f'360 / {rot_cart:.2f}',
        'valor_raw': dias_cobro,
        'valor': f'{dias_cobro:.0f} días' if dias_cobro > 0 else 'Inmediato (Contado)',
        'meta': '<= 30 a 45 días',
        'interpretacion': f'Los clientes que reciben crédito tardan en promedio {dias_cobro:.0f} días en pagar sus facturas.' if dias_cobro > 0 else 'Cobro de contado en caja al entregar la motocicleta reparada.',
        'estado': 'Saludable' if dias_cobro <= 35 else ('Precaución' if dias_cobro <= 60 else 'Crítico'),
        'badge_class': 'success' if dias_cobro <= 35 else ('warning' if dias_cobro <= 60 else 'danger'),
        'icono': 'fa-solid fa-calendar-check'
    })

    # 2.5 Rotación de Cuentas por Pagar (Días de Pago)
    dias_pago = safe_div(proveedores * 360, compras_credito)
    razones['actividad'].append({
        'id': 'dias_pago',
        'nombre': 'Rotación de Cuentas por Pagar (Días de Pago)',
        'categoria': 'Actividad',
        'formula': '(Cuentas por Pagar Promedio * 360) / Compras a Crédito',
        'formula_valores': f'(C$ {proveedores:,.2f} * 360) / C$ {compras_credito:,.2f}',
        'valor_raw': dias_pago,
        'valor': f'{dias_pago:.0f} días' if dias_pago > 0 else 'Al Contado',
        'meta': '30 a 60 días',
        'interpretacion': f'El taller salda sus obligaciones con distribuidores de repuestos cada {dias_pago:.0f} días en promedio.' if dias_pago > 0 else 'Adquisición de repuestos e insumos al contado.',
        'estado': 'Saludable' if (0 <= dias_pago <= 60) else ('Precaución' if dias_pago <= 90 else 'Crítico'),
        'badge_class': 'success' if (0 <= dias_pago <= 60) else ('warning' if dias_pago <= 90 else 'danger'),
        'icono': 'fa-solid fa-truck-ramp-box'
    })

    # 2.6 Rotación de Activos Fijos
    rot_af = safe_div(ventas, activo_fijo_neto)
    razones['actividad'].append({
        'id': 'rotacion_activos_fijos',
        'nombre': 'Rotación de Activos Fijos',
        'categoria': 'Actividad',
        'formula': 'Ventas Totales / Activo Fijo Neto',
        'formula_valores': f'C$ {ventas:,.2f} / C$ {activo_fijo_neto:,.2f}',
        'valor_raw': rot_af,
        'valor': f'{rot_af:.2f} veces',
        'meta': '>= 0.15x mes / >= 1.5x año',
        'interpretacion': f'Por cada córdoba invertido en maquinaria, elevadores y herramientas, se generan C$ {rot_af:.2f} en facturación.',
        'estado': 'Saludable' if rot_af >= 0.10 else ('Precaución' if rot_af >= 0.05 else 'Crítico'),
        'badge_class': 'success' if rot_af >= 0.10 else ('warning' if rot_af >= 0.05 else 'danger'),
        'icono': 'fa-solid fa-toolbox'
    })

    # 2.7 Rotación de Activos Totales
    rot_at = safe_div(ventas, activo_total)
    razones['actividad'].append({
        'id': 'rotacion_activos_totales',
        'nombre': 'Rotación de Activos Totales',
        'categoria': 'Actividad',
        'formula': 'Ventas Totales / Activo Total',
        'formula_valores': f'C$ {ventas:,.2f} / C$ {activo_total:,.2f}',
        'valor_raw': rot_at,
        'valor': f'{rot_at:.2f} veces',
        'meta': '>= 0.10x mes / >= 1.0x año',
        'interpretacion': f'Eficiencia operativa global: el taller genera C$ {rot_at:.2f} en ventas por cada C$ 1.00 de activos consolidados.',
        'estado': 'Saludable' if rot_at >= 0.08 else ('Precaución' if rot_at >= 0.04 else 'Crítico'),
        'badge_class': 'success' if rot_at >= 0.08 else ('warning' if rot_at >= 0.04 else 'danger'),
        'icono': 'fa-solid fa-arrows-spin'
    })

    # --------------------------------------------------------------------------
    # 3. RAZONES DE ENDEUDAMIENTO
    # --------------------------------------------------------------------------
    # 3.1 Nivel de Endeudamiento Total (%)
    end_tot = safe_div(pasivo_total * 100, activo_total)
    if end_tot <= 50.0:
        et_estado, et_class = 'Saludable', 'success'
        et_desc = f'Estructura financiera conservadora y sólida: solo el {end_tot:.1f}% de los activos del taller está financiado por acreedores.'
    elif end_tot <= 70.0:
        et_estado, et_class = 'Precaución', 'warning'
        et_desc = f'Endeudamiento moderado ({end_tot:.1f}%). Existe control pero se debe vigilar la carga financiera.'
    else:
        et_estado, et_class = 'Crítico', 'danger'
        et_desc = f'Alto apalancamiento ({end_tot:.1f}%). Más del 70% del taller está comprometido con terceros.'
    razones['endeudamiento'].append({
        'id': 'endeudamiento_total',
        'nombre': 'Nivel de Endeudamiento Total (%)',
        'categoria': 'Endeudamiento',
        'formula': '(Pasivo Total / Activo Total) * 100',
        'formula_valores': f'(C$ {pasivo_total:,.2f} / C$ {activo_total:,.2f}) * 100',
        'valor_raw': end_tot,
        'valor': f'{end_tot:.1f}%',
        'meta': '40% a 60%',
        'interpretacion': et_desc,
        'estado': et_estado,
        'badge_class': et_class,
        'icono': 'fa-solid fa-scale-unbalanced'
    })

    # 3.2 Endeudamiento a Corto Plazo (%)
    end_cp = safe_div(pasivo_corriente * 100, pasivo_total)
    razones['endeudamiento'].append({
        'id': 'endeudamiento_corto_plazo',
        'nombre': 'Endeudamiento a Corto Plazo (%)',
        'categoria': 'Endeudamiento',
        'formula': '(Pasivo Corriente / Pasivo Total) * 100',
        'formula_valores': f'(C$ {pasivo_corriente:,.2f} / C$ {pasivo_total:,.2f}) * 100',
        'valor_raw': end_cp,
        'valor': f'{end_cp:.1f}%',
        'meta': '<= 60%',
        'interpretacion': f'El {end_cp:.1f}% de la deuda total vence en menos de 1 año (exige liquidez inmediata para cancelarse).',
        'estado': 'Saludable' if end_cp <= 60 else ('Precaución' if end_cp <= 80 else 'Crítico'),
        'badge_class': 'success' if end_cp <= 60 else ('warning' if end_cp <= 80 else 'danger'),
        'icono': 'fa-solid fa-hourglass-half'
    })

    # 3.3 Apalancamiento Financiero (Deuda a Patrimonio)
    apal = safe_div(pasivo_total, patrimonio)
    razones['endeudamiento'].append({
        'id': 'apalancamiento_financiero',
        'nombre': 'Apalancamiento Financiero (Deuda a Patrimonio)',
        'categoria': 'Endeudamiento',
        'formula': 'Pasivo Total / Patrimonio',
        'formula_valores': f'C$ {pasivo_total:,.2f} / C$ {patrimonio:,.2f}',
        'valor_raw': apal,
        'valor': f'{apal:.2f}x',
        'meta': '<= 1.0x',
        'interpretacion': f'Por cada C$ 1.00 de capital propio invertido por los socios, hay C$ {apal:.2f} financiados por acreedores.',
        'estado': 'Saludable' if (0 < apal <= 1.0) else ('Precaución' if apal <= 1.5 else 'Crítico'),
        'badge_class': 'success' if (0 < apal <= 1.0) else ('warning' if apal <= 1.5 else 'danger'),
        'icono': 'fa-solid fa-building-shield'
    })

    # --------------------------------------------------------------------------
    # 4. RAZONES DE RENTABILIDAD
    # --------------------------------------------------------------------------
    # 4.1 Margen Bruto de Utilidad (%)
    mb = safe_div(utilidad_bruta * 100, ventas)
    razones['rentabilidad'].append({
        'id': 'margen_bruto',
        'nombre': 'Margen Bruto de Utilidad (%)',
        'categoria': 'Rentabilidad',
        'formula': '((Ventas Totales - Costo de Ventas) / Ventas Totales) * 100',
        'formula_valores': f'((C$ {ventas:,.2f} - C$ {costo_ventas:,.2f}) / C$ {ventas:,.2f}) * 100',
        'valor_raw': mb,
        'valor': f'{mb:.1f}%',
        'meta': '>= 40.0%',
        'interpretacion': f'El taller retiene C$ {mb:.1f} por cada C$ 100 facturados tras cubrir el costo de repuestos y mano de obra.',
        'estado': 'Saludable' if mb >= 40.0 else ('Precaución' if mb >= 20.0 else 'Crítico'),
        'badge_class': 'success' if mb >= 40.0 else ('warning' if mb >= 20.0 else 'danger'),
        'icono': 'fa-solid fa-coins'
    })

    # 4.2 Margen Operacional - EBIT (%)
    m_op = safe_div(utilidad_operativa * 100, ventas)
    razones['rentabilidad'].append({
        'id': 'margen_operacional',
        'nombre': 'Margen Operacional - EBIT (%)',
        'categoria': 'Rentabilidad',
        'formula': '(Utilidad Operativa / Ventas Totales) * 100',
        'formula_valores': f'(C$ {utilidad_operativa:,.2f} / C$ {ventas:,.2f}) * 100',
        'valor_raw': m_op,
        'valor': f'{m_op:.1f}%',
        'meta': '>= 15.0%',
        'interpretacion': f'Rentabilidad operativa pura: {m_op:.1f}% tras absorber gastos de nómina, servicios y alquiler, antes de impuestos.',
        'estado': 'Saludable' if m_op >= 15.0 else ('Precaución' if m_op >= 5.0 else 'Crítico'),
        'badge_class': 'success' if m_op >= 15.0 else ('warning' if m_op >= 5.0 else 'danger'),
        'icono': 'fa-solid fa-chart-line'
    })

    # 4.3 Margen Neto de Utilidad (%)
    mn = safe_div(utilidad_neta * 100, ventas)
    razones['rentabilidad'].append({
        'id': 'margen_neto',
        'nombre': 'Margen Neto de Utilidad (%)',
        'categoria': 'Rentabilidad',
        'formula': '(Utilidad Neta / Ventas Totales) * 100',
        'formula_valores': f'(C$ {utilidad_neta:,.2f} / C$ {ventas:,.2f}) * 100',
        'valor_raw': mn,
        'valor': f'{mn:.1f}%',
        'meta': '>= 10.0%',
        'interpretacion': f'Ganancia neta final disponible para los socios: C$ {mn:.1f} por cada C$ 100 de ingresos totales.',
        'estado': 'Saludable' if mn >= 10.0 else ('Precaución' if mn >= 3.0 else 'Crítico'),
        'badge_class': 'success' if mn >= 10.0 else ('warning' if mn >= 3.0 else 'danger'),
        'icono': 'fa-solid fa-trophy'
    })

    # 4.4 ROA - Rendimiento sobre el Activo (%)
    roa = safe_div(utilidad_neta * 100, activo_total)
    razones['rentabilidad'].append({
        'id': 'roa',
        'nombre': 'ROA - Rendimiento sobre el Activo (%)',
        'categoria': 'Rentabilidad',
        'formula': '(Utilidad Neta / Activo Total) * 100',
        'formula_valores': f'(C$ {utilidad_neta:,.2f} / C$ {activo_total:,.2f}) * 100',
        'valor_raw': roa,
        'valor': f'{roa:.1f}%',
        'meta': '>= 5.0%',
        'interpretacion': f'Rendimiento sobre la inversión total: C$ {roa:.1f} de utilidad neta generada por cada C$ 100 en bienes del taller.',
        'estado': 'Saludable' if roa >= 5.0 else ('Precaución' if roa >= 1.0 else 'Crítico'),
        'badge_class': 'success' if roa >= 5.0 else ('warning' if roa >= 1.0 else 'danger'),
        'icono': 'fa-solid fa-gem'
    })

    # 4.5 ROE - Rendimiento sobre el Patrimonio (%)
    roe = safe_div(utilidad_neta * 100, patrimonio)
    razones['rentabilidad'].append({
        'id': 'roe',
        'nombre': 'ROE - Rendimiento sobre el Patrimonio (%)',
        'categoria': 'Rentabilidad',
        'formula': '(Utilidad Neta / Patrimonio) * 100',
        'formula_valores': f'(C$ {utilidad_neta:,.2f} / C$ {patrimonio:,.2f}) * 100',
        'valor_raw': roe,
        'valor': f'{roe:.1f}%',
        'meta': '>= 10.0%',
        'interpretacion': f'Retorno financiero para los dueños: C$ {roe:.1f} de ganancia por cada C$ 100 de capital propio invertido.',
        'estado': 'Saludable' if roe >= 10.0 else ('Precaución' if roe >= 3.0 else 'Crítico'),
        'badge_class': 'success' if roe >= 10.0 else ('warning' if roe >= 3.0 else 'danger'),
        'icono': 'fa-solid fa-award'
    })

    # --------------------------------------------------------------------------
    # 5. RAZONES DE COBERTURA
    # --------------------------------------------------------------------------
    # 5.1 Cobertura de Intereses
    cob_int = safe_div(utilidad_operativa, gastos_intereses) if gastos_intereses > 0 else (99.0 if utilidad_operativa > 0 else 0.0)
    if gastos_intereses == 0:
        cob_int_val = 'Libre de Deuda'
        cob_int_desc = 'El taller no devenga gastos por intereses bancarios en este período.'
        cob_int_est, cob_int_cls = 'Saludable', 'success'
    else:
        cob_int_val = f'{cob_int:.2f} veces'
        if cob_int >= 3.0:
            cob_int_est, cob_int_cls = 'Saludable', 'success'
            cob_int_desc = f'Excelente holgura: la utilidad operativa cubre {cob_int:.2f} veces el pago mensual de intereses.'
        elif cob_int >= 1.5:
            cob_int_est, cob_int_cls = 'Precaución', 'warning'
            cob_int_desc = f'Cobertura moderada ({cob_int:.2f}x). Cuidar el flujo operativo ante alzas de financiamiento.'
        else:
            cob_int_est, cob_int_cls = 'Crítico', 'danger'
            cob_int_desc = f'Alerta de insolvencia: la utilidad ({cob_int:.2f}x) apenas cubre o no alcanza para pagar intereses.'
    razones['cobertura'].append({
        'id': 'cobertura_intereses',
        'nombre': 'Cobertura de Intereses',
        'categoria': 'Cobertura',
        'formula': 'Utilidad Operativa / Gastos de Intereses',
        'formula_valores': f'C$ {utilidad_operativa:,.2f} / C$ {gastos_intereses:,.2f}',
        'valor_raw': cob_int,
        'valor': cob_int_val,
        'meta': '>= 3.0 veces',
        'interpretacion': cob_int_desc,
        'estado': cob_int_est,
        'badge_class': cob_int_cls,
        'icono': 'fa-solid fa-shield-virus'
    })

    # 5.2 Cobertura Total del Servicio de la Deuda
    denom_servicio = gastos_intereses + safe_div(abono_capital, (1.0 - tasa_ir))
    cob_deuda = safe_div(ebitda, denom_servicio) if denom_servicio > 0 else (99.0 if ebitda > 0 else 0.0)
    if denom_servicio == 0:
        cd_val = 'Sin Cargas de Deuda'
        cd_desc = 'Flujo de caja 100% disponible para reinversión operativa y capital de trabajo.'
        cd_est, cd_cls = 'Saludable', 'success'
    else:
        cd_val = f'{cob_deuda:.2f} veces'
        if cob_deuda >= 1.2:
            cd_est, cd_cls = 'Saludable', 'success'
            cd_desc = f'Flujo de caja sólido: el EBITDA cubre {cob_deuda:.2f} veces el servicio integral de la deuda (capital + interés).'
        elif cob_deuda >= 1.0:
            cd_est, cd_cls = 'Precaución', 'warning'
            cd_desc = f'Cobertura justa ({cob_deuda:.2f}x). El flujo operativo alcanza justo para pagar las cuotas bancarias.'
        else:
            cd_est, cd_cls = 'Crítico', 'danger'
            cd_desc = f'Flujo de caja deficitario ({cob_deuda:.2f}x). El taller requiere renegociar plazos o cuotas.'
    razones['cobertura'].append({
        'id': 'cobertura_deuda_total',
        'nombre': 'Cobertura Total del Servicio de la Deuda',
        'categoria': 'Cobertura',
        'formula': 'EBITDA / (Gastos de Intereses + [Abono Capital / (1 - IR)])',
        'formula_valores': f'C$ {ebitda:,.2f} / (C$ {gastos_intereses:,.2f} + [C$ {abono_capital:,.2f} / (1 - {tasa_ir})])',
        'valor_raw': cob_deuda,
        'valor': cd_val,
        'meta': '>= 1.2 veces',
        'interpretacion': cd_desc,
        'estado': cd_est,
        'badge_class': cd_cls,
        'icono': 'fa-solid fa-shield-halved'
    })

    # --------------------------------------------------------------------------
    # REGLA CONTABLE MIPYME: SI EL PERÍODO NO ESTÁ CERRADO, LAS RAZONES APARECEN EN 0
    # --------------------------------------------------------------------------
    if not periodo_cerrado:
        todos_cero = []
        for cat in razones.values():
            for r in cat:
                # Asignar formato de cero según su unidad
                val_meta = r.get('meta', '')
                if 'x' in val_meta:
                    val_cero = '0.00x'
                elif '%' in val_meta:
                    val_cero = '0.0%'
                elif 'días' in val_meta.lower():
                    val_cero = '0 días'
                elif 'C$' in val_meta:
                    val_cero = 'C$ 0.00'
                else:
                    val_cero = '0.00'

                r['valor_raw'] = 0.0
                r['valor'] = val_cero
                r['formula_valores'] = 'C$ 0.00 / C$ 0.00 (Pendiente de cierre contable)'
                r['estado'] = 'Pendiente'
                r['badge_class'] = 'pending'
                r['interpretacion'] = f"Este indicador para {r['nombre']} se calculará automáticamente al final del mes una vez sellados el Balance General y el Estado de Resultados."
                todos_cero.append(r)

        total_r = len(todos_cero)
        resumen_semaforo = {
            'total': total_r,
            'saludable': 0,
            'precaucion': 0,
            'critico': 0,
            'pendientes': total_r,
            'score': 0.0,
            'diagnostico': 'Período en Curso: Razones en Cero (Requiere Cierre de Fin de Mes)'
        }
        return razones, resumen_semaforo

    # Resumen Semáforo Global para períodos cerrados
    todos = []
    for cat in razones.values():
        todos.extend(cat)
    saludables = sum(1 for r in todos if r['estado'] == 'Saludable')
    precauciones = sum(1 for r in todos if r['estado'] == 'Precaución')
    criticos = sum(1 for r in todos if r['estado'] == 'Crítico')
    total_r = len(todos)
    score = round((saludables * 1.0 + precauciones * 0.5) / total_r * 100, 1) if total_r > 0 else 0.0

    resumen_semaforo = {
        'total': total_r,
        'saludable': saludables,
        'precaucion': precauciones,
        'critico': criticos,
        'pendientes': 0,
        'score': score,
        'diagnostico': 'Diagnóstico Financiero Favorable' if score >= 75 else ('Situación Financiera Estable con Puntos de Alerta' if score >= 50 else 'Condición Financiera Comprometida - Requiere Acción')
    }

    return razones, resumen_semaforo

# ==============================================================================
# CRUD CUENTAS CONTABLES PERSONALIZADAS Y AJUSTES (MiPyME)
# ==============================================================================
@contador_bp.route('/agregar_cuenta', methods=['POST'])
@contador_required
def agregar_cuenta():
    tipo_reporte = request.form.get('tipo_reporte', 'Balance')
    mes = request.form.get('mes', type=int, default=datetime.now().month)
    anio = request.form.get('anio', type=int, default=datetime.now().year)
    categoria = request.form.get('categoria', '').strip()
    nombre_cuenta = request.form.get('nombre_cuenta', '').strip()
    try:
        monto = float(request.form.get('monto', 0.0))
    except (ValueError, TypeError):
        monto = 0.0

    if not nombre_cuenta or not categoria:
        flash("Debe ingresar el nombre y la categoría de la cuenta contable.", "error")
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO CuentasContablesAjustes (UsuarioID, TipoReporte, Mes, Anio, Categoria, NombreCuenta, Monto, FechaCreacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (session.get('usuario_id', 1), tipo_reporte, mes, anio, categoria, nombre_cuenta, monto))
            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = ? AND Mes = ? AND Anio = ?", (tipo_reporte, mes, anio))
            conn.commit()
            conn.close()
            flash(f"Cuenta contable '{nombre_cuenta}' añadida exitosamente (C$ {monto:,.2f}).", "success")

    if tipo_reporte == 'EstadoResultados':
        return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))
    return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))

@contador_bp.route('/editar_cuenta', methods=['POST'])
@contador_required
def editar_cuenta():
    ajuste_id = request.form.get('ajuste_id', type=int)
    tipo_reporte = request.form.get('tipo_reporte', 'Balance')
    mes = request.form.get('mes', type=int, default=datetime.now().month)
    anio = request.form.get('anio', type=int, default=datetime.now().year)
    categoria = request.form.get('categoria', '').strip()
    nombre_cuenta = request.form.get('nombre_cuenta', '').strip()
    clave_cuenta = request.form.get('clave_cuenta', '').strip() or None
    try:
        monto = float(request.form.get('monto', 0.0))
    except (ValueError, TypeError):
        monto = 0.0

    if not nombre_cuenta:
        flash("Debe ingresar el nombre de la cuenta contable.", "error")
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if ajuste_id and ajuste_id > 0:
                cursor.execute("""
                    UPDATE CuentasContablesAjustes 
                    SET NombreCuenta = ?, Monto = ?, Categoria = ?, ClaveCuenta = COALESCE(?, ClaveCuenta)
                    WHERE AjusteID = ?
                """, (nombre_cuenta, monto, categoria, clave_cuenta, ajuste_id))
            else:
                if clave_cuenta:
                    cursor.execute("""
                        SELECT AjusteID FROM CuentasContablesAjustes 
                        WHERE TipoReporte = ? AND Mes = ? AND Anio = ? AND (ClaveCuenta = ? OR LOWER(LTRIM(RTRIM(NombreCuenta))) = LOWER(?))
                    """, (tipo_reporte, mes, anio, clave_cuenta, nombre_cuenta))
                else:
                    cursor.execute("""
                        SELECT AjusteID FROM CuentasContablesAjustes 
                        WHERE TipoReporte = ? AND Mes = ? AND Anio = ? AND LOWER(LTRIM(RTRIM(NombreCuenta))) = LOWER(?)
                    """, (tipo_reporte, mes, anio, nombre_cuenta))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        UPDATE CuentasContablesAjustes 
                        SET Monto = ?, Categoria = ?, NombreCuenta = ?, ClaveCuenta = COALESCE(?, ClaveCuenta)
                        WHERE AjusteID = ?
                    """, (monto, categoria, nombre_cuenta, clave_cuenta, row[0]))
                else:
                    cursor.execute("""
                        INSERT INTO CuentasContablesAjustes (UsuarioID, TipoReporte, Mes, Anio, Categoria, NombreCuenta, Monto, FechaCreacion, ClaveCuenta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
                    """, (session.get('usuario_id', 1), tipo_reporte, mes, anio, categoria, nombre_cuenta, monto, clave_cuenta))

            cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = ? AND Mes = ? AND Anio = ?", (tipo_reporte, mes, anio))
            conn.commit()
            conn.close()
            flash(f"Cuenta contable '{nombre_cuenta}' actualizada correctamente a C$ {monto:,.2f}.", "success")

    if tipo_reporte == 'EstadoResultados':
        return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))
    return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))

@contador_bp.route('/eliminar_cuenta/<int:id>', methods=['POST'])
@contador_required
def eliminar_cuenta(id):
    tipo_reporte = request.form.get('tipo_reporte') or request.args.get('tipo_reporte') or 'Balance'
    mes = request.form.get('mes', type=int) or request.args.get('mes', type=int) or datetime.now().month
    anio = request.form.get('anio', type=int) or request.args.get('anio', type=int) or datetime.now().year

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CuentasContablesAjustes WHERE AjusteID = ?", (id,))
        cursor.execute("DELETE FROM ReportesContables WHERE TipoReporte = ? AND Mes = ? AND Anio = ?", (tipo_reporte, mes, anio))
        conn.commit()
        conn.close()
        flash("Cuenta contable eliminada o restablecida a su valor base.", "success")

    if tipo_reporte == 'EstadoResultados':
        return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))
    return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))

@contador_bp.route('/resumen_finanzas')
@contador_required
def resumen_finanzas():
    ahora = datetime.now()
    anio = request.args.get('anio', default=max(2026, ahora.year), type=int)
    if anio < 2026:
        anio = 2026
    return redirect(url_for('contador.historial_finanzas', anio=anio))

@contador_bp.route('/historial_finanzas')
@contador_required
def historial_finanzas():
    ahora = datetime.now()
    anio = request.args.get('anio', default=max(2026, ahora.year), type=int)
    if anio < 2026:
        anio = 2026
    mes_sel = request.args.get('mes', default=ahora.month, type=int)
    if not (1 <= mes_sel <= 12):
        mes_sel = ahora.month

    conn = get_db_connection()
    anios_disponibles = set([2026, 2027, 2028, 2029, 2030])
    if ahora.year >= 2026:
        anios_disponibles.add(ahora.year)

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT YEAR(FechaEmision) FROM Facturas WHERE FechaEmision IS NOT NULL AND YEAR(FechaEmision) >= 2026
                UNION
                SELECT DISTINCT YEAR(FechaGasto) FROM GastosOperativos WHERE FechaGasto IS NOT NULL AND YEAR(FechaGasto) >= 2026
                UNION
                SELECT DISTINCT YEAR(FechaCompra) FROM Compras WHERE FechaCompra IS NOT NULL AND YEAR(FechaCompra) >= 2026
                UNION
                SELECT DISTINCT Anio FROM ReportesContables WHERE Anio IS NOT NULL AND Anio >= 2026
            """)
            for r in cursor.fetchall():
                if r[0] and int(r[0]) >= 2026:
                    anios_disponibles.add(int(r[0]))
        except Exception as e:
            print(f"Error consultando anios disponibles: {e}")

    lista_anios = sorted(list(anios_disponibles))
    if not lista_anios:
        lista_anios = [2026, 2027, 2028, 2029, 2030]

    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # Barra superior de los 12 meses con estados de cierre en base de datos
    meses_bar = []
    totales_anuales = {
        'ventas_netas': 0.0,
        'costo_ventas': 0.0,
        'utilidad_bruta': 0.0,
        'gastos_operativos': 0.0,
        'utilidad_neta': 0.0,
        'meses_con_actividad': 0
    }

    for m in range(1, 13):
        cierre_m = verificar_cierre_estados(m, anio, conn)
        if cierre_m['ambos_cerrados'] and cierre_m['datos_cerrados']:
            dat_m = cierre_m['datos_cerrados']
        else:
            dat_m = obtener_datos_financieros_taller(mes=m, anio=anio)

        v_m = float(dat_m.get('ventas_netas', 0.0))
        u_m = float(dat_m.get('utilidad_neta', 0.0))
        g_m = float(dat_m.get('gastos_operativos', 0.0))
        c_m = float(dat_m.get('costo_ventas', 0.0))

        if v_m > 0 or g_m > 0 or c_m > 0:
            totales_anuales['meses_con_actividad'] += 1
            totales_anuales['ventas_netas'] += v_m
            totales_anuales['costo_ventas'] += c_m
            totales_anuales['utilidad_bruta'] += float(dat_m.get('utilidad_bruta', 0.0))
            totales_anuales['gastos_operativos'] += g_m
            totales_anuales['utilidad_neta'] += u_m

        meses_bar.append({
            'mes': m,
            'nombre': meses_nombres[m],
            'anio': anio,
            'es_seleccionado': (m == mes_sel),
            'es_mes_actual': (m == ahora.month and anio == ahora.year),
            'balance_cerrado': cierre_m['balance_cerrado'],
            'estado_cerrado': cierre_m['estado_cerrado'],
            'ambos_cerrados': cierre_m['ambos_cerrados'],
            'ventas_netas': v_m,
            'utilidad_neta': u_m,
            'tiene_actividad': (v_m > 0 or g_m > 0)
        })

    # Datos específicos del mes seleccionado (100% oficial sin simulaciones)
    cierre_sel = verificar_cierre_estados(mes_sel, anio, conn)
    ambos_cerrados = cierre_sel['ambos_cerrados']

    if ambos_cerrados and cierre_sel['datos_cerrados']:
        fin = cierre_sel['datos_cerrados']
        fin['periodos_disponibles'] = obtener_periodos_disponibles(conn)
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=True)
    else:
        fin = obtener_datos_financieros_taller(mes=mes_sel, anio=anio)
        # Regla contable MiPyME: las razones permanecen formalmente fijadas en 0 hasta sellar el cierre
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=False)

    if conn:
        conn.close()

    return render_template(
        'contador/historial_finanzas.html',
        mes_seleccionado=mes_sel,
        nombre_mes=meses_nombres[mes_sel],
        anio_seleccionado=anio,
        lista_anios=lista_anios,
        meses_bar=meses_bar,
        cierre_info=cierre_sel,
        ambos_cerrados=ambos_cerrados,
        fin=fin,
        razones=razones,
        resumen_semaforo=resumen_semaforo,
        totales=totales_anuales
    )


@contador_bp.route('/guardar_cierre_finanzas', methods=['POST'])
@contador_required
def guardar_cierre_finanzas():
    mes = request.form.get('mes', type=int)
    anio = request.form.get('anio', type=int)
    if not mes or not anio:
        flash("Mes y año son requeridos.", "error")
        return redirect(url_for('contador.historial_finanzas'))

    usuario_id = session.get('usuario_id', 1)
    fin_datos = obtener_datos_financieros_taller(mes=mes, anio=anio)
    json_str = json.dumps(fin_datos, default=str)

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ReporteID FROM ReportesContables WHERE TipoReporte = 'Finanzas' AND Mes = ? AND Anio = ?", (mes, anio))
            existente = cursor.fetchone()
            if existente:
                cursor.execute("""
                    UPDATE ReportesContables 
                    SET UsuarioID = ?, DatosJSON = ?, FechaCreacion = GETDATE()
                    WHERE ReporteID = ?
                """, (usuario_id, json_str, existente[0]))
            else:
                cursor.execute("""
                    INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                    VALUES (?, 'Finanzas', ?, ?, ?, GETDATE())
                """, (usuario_id, mes, anio, json_str))
            conn.commit()
            flash(f"Cierre financiero de {mes}/{anio} guardado y certificado exitosamente en la base de datos.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al guardar cierre financiero: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('contador.historial_finanzas', anio=anio))

@contador_bp.route('/razones')
@contador_required
def razones():
    ahora = datetime.now()
    mes = request.args.get('mes', default=ahora.month, type=int)
    anio = request.args.get('anio', default=max(2026, ahora.year), type=int)
    if anio < 2026:
        anio = 2026

    # Verificar si el mes y año tienen cerrados el Estado de Resultados y el Balance General
    info_cierre = verificar_cierre_estados(mes, anio)
    ambos_cerrados = info_cierre['ambos_cerrados']

    if ambos_cerrados and info_cierre['datos_cerrados']:
        fin = info_cierre['datos_cerrados']
        fin['periodos_disponibles'] = obtener_periodos_disponibles()
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=True)
    else:
        # Regla contable MIPYME: sin cierre sellado, todas las razones permanecen en 0
        fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=False)

    return render_template('contador/razones.html', 
                          fin=fin,
                          razones=razones,
                          resumen_semaforo=resumen_semaforo,
                          mes_seleccionado=mes,
                          anio_seleccionado=anio,
                          info_cierre=info_cierre,
                          ambos_cerrados=ambos_cerrados)


# ==============================================================================
# API: DETALLE ANALÍTICO DE TRANSACCIONES (MODAL DRILL-DOWN)
# ==============================================================================
@contador_bp.route('/api/detalle_transacciones')
@contador_required
def api_detalle_transacciones():
    tipo = request.args.get('tipo', 'facturas')
    mes = request.args.get('mes', default=datetime.now().month, type=int)
    anio = request.args.get('anio', default=datetime.now().year, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No DB connection'}), 500

    cursor = conn.cursor()
    items = []
    resumen = {}
    empty_title = "Sin movimientos registrados"
    empty_msg = "No se encontraron registros contables para este concepto en el período seleccionado."

    try:
        if tipo == 'caja':
            empty_title = "Sin movimientos de caja"
            empty_msg = "No se registraron aperturas, cobros en efectivo ni cierres de caja en este mes."
            
            # 1. Sesiones de caja
            cursor.execute("""
                SELECT CajaID, FechaApertura, MontoInicial, Estado, FechaCierre, MontoFinal, EfectivoFisico, Diferencia
                FROM ControlCaja
                WHERE MONTH(FechaApertura) = ? AND YEAR(FechaApertura) = ?
                ORDER BY CajaID ASC
            """, (mes, anio))
            cajas_rows = cursor.fetchall()

            # 2. Facturas cobradas en efectivo
            cursor.execute("""
                SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, f.TotalNeto, f.SubTotal, f.TotalIVA,
                       f.MetodoPago, ISNULL(c.NombreCompleto, f.NombreClienteDePaso) as Cliente, f.CajaID, f.OrdenID
                FROM Facturas f
                LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
                WHERE f.Estado = 'Pagada' AND f.MetodoPago = 'Efectivo' 
                      AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
                ORDER BY f.FechaEmision ASC
            """, (mes, anio))
            fact_efectivo = cursor.fetchall()

            total_ingresos_efectivo = sum(float(r[3] or 0) for r in fact_efectivo)
            monto_ini_primera = float(cajas_rows[0][2] or 0.0) if cajas_rows else 0.0
            saldo_acumulado = monto_ini_primera

            for c_row in cajas_rows:
                items.append({
                    'id': f"caja-open-{c_row[0]}",
                    'fecha': c_row[1].strftime('%d/%m/%Y %I:%M %p') if c_row[1] else '',
                    'tipo_mov': 'Apertura de Caja',
                    'concepto': f"Apertura de Turno Caja #{c_row[0]}",
                    'referencia': f"Caja #{c_row[0]}",
                    'cliente': 'Cajero en Turno',
                    'ingreso': float(c_row[2] or 0.0),
                    'egreso': 0.0,
                    'saldo': float(c_row[2] or 0.0),
                    'estado': c_row[3]
                })

            for f_row in fact_efectivo:
                monto_f = float(f_row[3] or 0.0)
                saldo_acumulado += monto_f
                items.append({
                    'id': f"fact-{f_row[0]}",
                    'fecha': f_row[2].strftime('%d/%m/%Y %I:%M %p') if f_row[2] else '',
                    'tipo_mov': 'Cobro en Efectivo',
                    'concepto': f"Factura {f_row[1]} ({'Orden Taller #' + str(f_row[9]) if f_row[9] else 'Venta Mostrador'})",
                    'referencia': f_row[1],
                    'cliente': f_row[7] or 'Cliente General',
                    'ingreso': monto_f,
                    'egreso': 0.0,
                    'saldo': saldo_acumulado,
                    'estado': 'Cobrada'
                })

            total_dif_cajas = 0.0
            saldo_final_conciliado = saldo_acumulado

            for c_row in cajas_rows:
                if c_row[3] == 'Cerrada' and c_row[4]:
                    ef_fis_val = float(c_row[6] if (c_row[6] is not None and (c_row[6] > 0 or (c_row[5] is not None and c_row[5] == 0))) else (c_row[5] or 0.0))
                    dif_val = float(c_row[7] or 0.0) if len(c_row) > 7 and c_row[7] is not None else 0.0
                    total_dif_cajas += dif_val
                    
                    dif_texto = ""
                    if dif_val > 0.001:
                        dif_texto = f" (Sobrante: +C$ {dif_val:,.2f})"
                    elif dif_val < -0.001:
                        dif_texto = f" (Faltante: C$ {dif_val:,.2f})"
                    else:
                        dif_texto = " (Arqueo Cuadrado C$ 0.00)"

                    items.append({
                        'id': f"caja-close-{c_row[0]}",
                        'fecha': c_row[4].strftime('%d/%m/%Y %I:%M %p'),
                        'tipo_mov': 'Cierre de Caja',
                        'concepto': f"Arqueo y Cierre Oficial Caja #{c_row[0]}{dif_texto}",
                        'referencia': f"Cierre #{c_row[0]}",
                        'cliente': 'Cierre Diario',
                        'ingreso': 0.0,
                        'egreso': 0.0,
                        'saldo': ef_fis_val,
                        'estado': 'Cerrada'
                    })
                    saldo_final_conciliado = ef_fis_val

            resumen = {
                'total_caja': round(saldo_final_conciliado, 2),
                'total_ingresos_efectivo': round(total_ingresos_efectivo, 2),
                'monto_inicial': round(monto_ini_primera, 2),
                'diferencia_arqueo': round(total_dif_cajas, 2),
                'cajas_activas': len(cajas_rows),
                'facturas_efectivo_count': len(fact_efectivo)
            }

        elif tipo == 'cobrar':
            empty_title = "¡Cartera de Clientes al Día!"
            empty_msg = "No hay cuentas por cobrar pendientes ni órdenes a crédito en este período. Todos los servicios y ventas directas han sido pagados al contado."

            # Facturas pendientes
            cursor.execute("""
                SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, f.TotalNeto, ISNULL(c.NombreCompleto, f.NombreClienteDePaso) as Cliente, f.MetodoPago
                FROM Facturas f
                LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
                WHERE f.Estado = 'Pendiente' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
                ORDER BY f.FechaEmision DESC
            """, (mes, anio))
            for r in cursor.fetchall():
                items.append({
                    'id': f"cpc-fact-{r[0]}",
                    'numero': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'cliente': r[4] or 'Cliente General',
                    'concepto': 'Factura Pendiente de Cobro',
                    'monto': float(r[3] or 0.0),
                    'estado': 'Pendiente'
                })

            # Órdenes pendientes de pago
            cursor.execute("""
                SELECT o.OrdenID, c.NombreCompleto, m.Modelo, o.TipoServicio, o.FechaIngreso,
                       ISNULL((SELECT SUM(CostoSugerido) FROM OrdenManoObra WHERE OrdenID = o.OrdenID), 0) +
                       ISNULL((SELECT SUM(r.Cantidad * p.PrecioVenta) FROM OrdenRepuestos r JOIN Productos p ON r.ProductoID = p.ProductoID WHERE r.OrdenID = o.OrdenID), 0) as TotalSugerido
                FROM OrdenesTrabajo o
                JOIN Motocicletas m ON o.MotoID = m.MotoID
                JOIN Clientes c ON m.ClienteID = c.ClienteID
                WHERE o.Estado IN ('Pendiente de Pago', 'Finalizado') 
                  AND NOT EXISTS (SELECT 1 FROM Facturas f WHERE f.OrdenID = o.OrdenID AND f.Estado = 'Pagada')
                  AND MONTH(o.FechaIngreso) = ? AND YEAR(o.FechaIngreso) = ?
                ORDER BY o.FechaIngreso DESC
            """, (mes, anio))
            for r in cursor.fetchall():
                items.append({
                    'id': f"cpc-ord-{r[0]}",
                    'numero': f"OT #{r[0]}",
                    'fecha': r[4].strftime('%d/%m/%Y %I:%M %p') if r[4] else '',
                    'cliente': r[1],
                    'concepto': f"{r[3]} ({r[2]})",
                    'monto': float(r[5] or 0.0),
                    'estado': 'Pendiente de Pago'
                })

        elif tipo == 'inventario':
            empty_title = "Inventario Vacío"
            empty_msg = "No se encontraron repuestos ni lubricantes activos en el catálogo de bodega."
            cursor.execute("""
                SELECT ProductoID, CodigoSKU, Nombre, Categoria, StockActual, PrecioCompra, 
                       (StockActual * PrecioCompra) as ValorTotal, PrecioVenta
                FROM Productos
                WHERE Activo = 1
                ORDER BY ValorTotal DESC, StockActual DESC
            """)
            total_val = 0.0
            total_uds = 0
            for r in cursor.fetchall():
                vt = float(r[6] or 0.0)
                st = int(r[4] or 0)
                total_val += vt
                total_uds += st
                items.append({
                    'id': r[0],
                    'sku': r[1] or 'S/SKU',
                    'nombre': r[2],
                    'categoria': r[3] or 'General',
                    'stock': st,
                    'costo_unit': float(r[5] or 0.0),
                    'costo_total': vt,
                    'precio_venta': float(r[7] or 0.0)
                })
            resumen = {
                'total_valorizado': round(total_val, 2),
                'total_articulos': total_uds,
                'total_skus': len(items)
            }

        elif tipo == 'compras' or tipo == 'credito_iva':
            empty_title = "Sin Compras de Bodega"
            empty_msg = "No se registraron compras de repuestos o lubricantes a proveedores durante este período."
            cursor.execute("""
                SELECT c.CompraID, pr.NombreEmpresa, c.FechaCompra, c.TotalCompra, c.Subtotal, c.IVA
                FROM Compras c
                LEFT JOIN Proveedores pr ON c.ProveedorID = pr.ProveedorID
                WHERE MONTH(c.FechaCompra) = ? AND YEAR(c.FechaCompra) = ?
                ORDER BY c.FechaCompra DESC
            """, (mes, anio))
            total_compras = 0.0
            total_iva_cred = 0.0
            for r in cursor.fetchall():
                tc = float(r[3] or 0.0)
                iv = float(r[5] or 0.0) if r[5] else round(tc * 0.15, 2)
                sb = float(r[4] or 0.0) if r[4] else round(tc - iv, 2)
                total_compras += tc
                total_iva_cred += iv
                items.append({
                    'id': r[0],
                    'proveedor': r[1] or 'Proveedor Mayorista Local',
                    'fecha': r[2].strftime('%d/%m/%Y') if hasattr(r[2], 'strftime') else str(r[2] or ''),
                    'subtotal': sb,
                    'iva': iv,
                    'total': tc
                })
            resumen = {
                'total_compras': round(total_compras, 2),
                'credito_fiscal_iva': round(total_iva_cred, 2)
            }

        elif tipo == 'debito_iva':
            empty_title = "Sin Facturas con IVA"
            empty_msg = "No se emitieron facturas de venta durante este período."
            cursor.execute("""
                SELECT FacturaID, NumeroFactura, FechaEmision, SubTotal, TotalIVA, TotalNeto, MetodoPago, OrdenID
                FROM Facturas 
                WHERE Estado = 'Pagada' AND MONTH(FechaEmision) = ? AND YEAR(FechaEmision) = ?
                ORDER BY FechaEmision DESC
            """, (mes, anio))
            tot_sub = 0.0
            tot_iva = 0.0
            tot_neto = 0.0
            for r in cursor.fetchall():
                sb = float(r[3] or 0.0)
                iv = float(r[4] or 0.0)
                tn = float(r[5] or 0.0)
                tot_sub += sb
                tot_iva += iv
                tot_neto += tn
                items.append({
                    'id': r[0],
                    'numero': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'subtotal': sb,
                    'iva': iv,
                    'total': tn,
                    'pago': r[6],
                    'tipo': 'Orden de Taller #' + str(r[7]) if r[7] else 'Venta Mostrador'
                })
            resumen = {
                'subtotal_gravado': round(tot_sub, 2),
                'debito_fiscal_iva': round(tot_iva, 2),
                'total_facturado': round(tot_neto, 2)
            }

        elif tipo == 'retenciones_dgi':
            empty_title = "Sin Retenciones DGI"
            empty_msg = "No se registraron retenciones de nómina ni anticipos IR en este período."
            from routes.planilla import obtener_totales_nomina_mes
            nom = obtener_totales_nomina_mes(mes, anio)
            ret_ir_nom = float(nom['totales'].get('ir', 0.0) or 0.0)
            
            cursor.execute("""
                SELECT ISNULL(SUM(SubTotal), 0) FROM Facturas 
                WHERE Estado = 'Pagada' AND MONTH(FechaEmision) = ? AND YEAR(FechaEmision) = ?
            """, (mes, anio))
            v_grav = float(cursor.fetchone()[0] or 0.0)
            anticipo_1pct = round(v_grav * 0.01, 2)

            if ret_ir_nom > 0:
                items.append({
                    'concepto': 'Retención de IR Laboral en la Fuente sobre Salarios (Nómina DGI)',
                    'base': float(nom['totales'].get('salario_bruto', 0.0) or 0.0),
                    'tasa': 'Tabla Progresiva DGI (Ley 822)',
                    'monto': ret_ir_nom,
                    'referencia': 'Nómina de Pago'
                })
            if anticipo_1pct > 0:
                items.append({
                    'concepto': 'Anticipo Mensual Pago Mínimo Definitivo del IR (1% Ventas Gravadas)',
                    'base': v_grav,
                    'tasa': '1.0% DGI',
                    'monto': anticipo_1pct,
                    'referencia': 'Declaración DGI V-01'
                })
            resumen = {
                'total_retenciones': round(ret_ir_nom + anticipo_1pct, 2),
                'ret_ir_nomina': round(ret_ir_nom, 2),
                'anticipo_ir_ventas': round(anticipo_1pct, 2)
            }

        elif tipo in ('obligaciones_laborales', 'nomina'):
            empty_title = "Sin Obligaciones Laborales"
            empty_msg = "No se registraron colaboradores en la planilla de este mes."
            from routes.planilla import obtener_totales_nomina_mes
            nom = obtener_totales_nomina_mes(mes, anio)
            for emp in nom.get('todos', []):
                is_pag = bool(emp.get('pagado', False))
                sb = float(emp.get('salario_bruto') if is_pag else (emp.get('calc_salario_bruto') or emp.get('salario_base', 0.0)))
                inss_l = float(emp.get('inss_laboral') if is_pag else (emp.get('calc_inss_laboral') or 0.0))
                ir_v = float(emp.get('ir') if is_pag else (emp.get('calc_ir') or 0.0))
                sn = float(emp.get('salario_neto') if is_pag else (emp.get('calc_salario_neto') or 0.0))
                inss_p = float(emp.get('inss_patronal') if is_pag else (emp.get('calc_inss_patronal') or 0.0))
                ina = float(emp.get('inatec') if is_pag else (emp.get('calc_inatec') or 0.0))
                prov = float(emp.get('total_provisiones_mensuales') if is_pag else (emp.get('calc_total_provisiones_mensuales') or 0.0))
                costo = float(emp.get('costo_total_empleador') if is_pag else (emp.get('calc_costo_total_empleador') or 0.0))
                items.append({
                    'id': emp.get('id', 0),
                    'nombre': emp.get('nombre', ''),
                    'cargo': emp.get('cargo', ''),
                    'salario_base': float(emp.get('salario_base', 0.0)),
                    'salario_bruto': round(sb, 2),
                    'inss_laboral': round(inss_l, 2),
                    'ir': round(ir_v, 2),
                    'salario_neto': round(sn, 2),
                    'inss_patronal': round(inss_p, 2),
                    'inatec': round(ina, 2),
                    'provisiones': round(prov, 2),
                    'costo_empresa': round(costo, 2),
                    'pagado': is_pag
                })
            t = nom.get('totales', {})
            t_sb = sum(i['salario_bruto'] for i in items)
            t_inss_l = sum(i['inss_laboral'] for i in items)
            t_ir = sum(i['ir'] for i in items)
            t_inss_p = sum(i['inss_patronal'] for i in items)
            t_inatec = sum(i['inatec'] for i in items)
            t_prov = sum(i['provisiones'] for i in items)
            t_costo = sum(i['costo_empresa'] for i in items)
            resumen = {
                'salario_bruto': round(t.get('salario_bruto') or t_sb, 2),
                'inss_laboral': round(t.get('inss_laboral') or t_inss_l, 2),
                'ir': round(t.get('ir') or t_ir, 2),
                'inss_patronal': round(t.get('inss_patronal') or t_inss_p, 2),
                'inatec': round(t.get('inatec') or t_inatec, 2),
                'cargas_patronales': round((t.get('inss_patronal') or t_inss_p) + (t.get('inatec') or t_inatec), 2),
                'provisiones': round(t.get('provisiones_mensuales') or t_prov, 2),
                'costo_empresa_total': round(t.get('costo_total_empleador') or t_costo, 2),
                'empleados_pagados': t.get('cantidad_pagados', 0),
                'total_empleados': len(items)
            }

        elif tipo == 'mano_obra':
            empty_title = "Sin Mano de Obra en Taller"
            empty_msg = "No se liquidaron mantenimientos mecánicos en órdenes de trabajo durante este período."
            cursor.execute("""
                SELECT ot.OrdenID, c.NombreCompleto, m.Modelo, mo.Servicio, mo.CostoSugerido, f.NumeroFactura, f.FechaEmision
                FROM OrdenManoObra mo
                JOIN OrdenesTrabajo ot ON mo.OrdenID = ot.OrdenID
                JOIN Facturas f ON ot.OrdenID = f.OrdenID
                JOIN Motocicletas m ON ot.MotoID = m.MotoID
                JOIN Clientes c ON m.ClienteID = c.ClienteID
                WHERE f.Estado = 'Pagada' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
                ORDER BY f.FechaEmision DESC
            """, (mes, anio))
            total_mo = 0.0
            for r in cursor.fetchall():
                c_mo = float(r[4] or 0.0)
                total_mo += c_mo
                items.append({
                    'orden_id': r[0],
                    'cliente': r[1],
                    'moto': r[2],
                    'servicio': r[3],
                    'monto': c_mo,
                    'factura': r[5],
                    'fecha': r[6].strftime('%d/%m/%Y %I:%M %p') if r[6] else ''
                })
            resumen = {'total_mano_obra': round(total_mo, 2)}

        elif tipo == 'repuestos_taller':
            empty_title = "Sin Repuestos en Taller"
            empty_msg = "No se aplicaron repuestos de bodega en órdenes de trabajo durante este período."
            cursor.execute("""
                SELECT ot.OrdenID, p.Nombre, or_rep.Cantidad, p.PrecioVenta, p.PrecioCompra, 
                       (or_rep.Cantidad * p.PrecioVenta) as TotalVenta, 
                       (or_rep.Cantidad * p.PrecioCompra) as TotalCosto,
                       f.NumeroFactura, f.FechaEmision
                FROM OrdenRepuestos or_rep
                JOIN Productos p ON or_rep.ProductoID = p.ProductoID
                JOIN OrdenesTrabajo ot ON or_rep.OrdenID = ot.OrdenID
                JOIN Facturas f ON ot.OrdenID = f.OrdenID
                WHERE f.Estado = 'Pagada' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
                ORDER BY f.FechaEmision DESC
            """, (mes, anio))
            tot_v = 0.0
            tot_c = 0.0
            for r in cursor.fetchall():
                v = float(r[5] or 0.0)
                c = float(r[6] or 0.0)
                tot_v += v
                tot_c += c
                items.append({
                    'orden_id': r[0],
                    'producto': r[1],
                    'cantidad': int(r[2] or 0),
                    'precio_venta': float(r[3] or 0.0),
                    'costo_compra': float(r[4] or 0.0),
                    'total_venta': v,
                    'total_costo': c,
                    'margen': round(v - c, 2),
                    'factura': r[7],
                    'fecha': r[8].strftime('%d/%m/%Y %I:%M %p') if r[8] else ''
                })
            resumen = {'total_venta': round(tot_v, 2), 'total_costo': round(tot_c, 2)}

        elif tipo == 'mostrador':
            empty_title = "Sin Ventas de Mostrador"
            empty_msg = "No se registraron ventas directas al público en mostrador durante este mes."
            cursor.execute("""
                SELECT df.DetalleID, f.NumeroFactura, f.FechaEmision, df.Descripcion, df.Cantidad, 
                       df.PrecioVentaAplicado, (df.Cantidad * df.PrecioVentaAplicado) as SubtotalVenta,
                       ISNULL(p.PrecioCompra, 0) as CostoUnitario,
                       (df.Cantidad * ISNULL(p.PrecioCompra, 0)) as CostoTotal
                FROM DetalleFactura df
                JOIN Facturas f ON df.FacturaID = f.FacturaID
                LEFT JOIN Productos p ON df.ProductoID = p.ProductoID
                WHERE f.Estado = 'Pagada' AND f.OrdenID IS NULL 
                      AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
                ORDER BY f.FechaEmision DESC
            """, (mes, anio))
            tot_v = 0.0
            tot_c = 0.0
            for r in cursor.fetchall():
                v = float(r[6] or 0.0)
                c = float(r[8] or 0.0)
                tot_v += v
                tot_c += c
                items.append({
                    'id': r[0],
                    'factura': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'producto': r[3],
                    'cantidad': int(r[4] or 0),
                    'precio_venta': float(r[5] or 0.0),
                    'total_venta': v,
                    'costo_unit': float(r[7] or 0.0),
                    'costo_total': c,
                    'margen': round(v - c, 2)
                })
            resumen = {'total_venta': round(tot_v, 2), 'total_costo': round(tot_c, 2)}

        elif tipo == 'cogs' or tipo == 'costo_ventas':
            empty_title = "Sin Costo de Ventas"
            empty_msg = "No se despacharon repuestos en taller ni mercaderías de mostrador en este período."
            # Repuestos de taller
            cursor.execute("""
                SELECT 'Taller' as Origen, f.NumeroFactura, f.FechaEmision, p.Nombre, or_rep.Cantidad, 
                       p.PrecioCompra as CostoUnitario, (or_rep.Cantidad * p.PrecioCompra) as CostoTotal
                FROM OrdenRepuestos or_rep
                JOIN Productos p ON or_rep.ProductoID = p.ProductoID
                JOIN OrdenesTrabajo ot ON or_rep.OrdenID = ot.OrdenID
                JOIN Facturas f ON ot.OrdenID = f.OrdenID
                WHERE f.Estado = 'Pagada' AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
            """, (mes, anio))
            for r in cursor.fetchall():
                items.append({
                    'origen': r[0],
                    'factura': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'producto': r[3],
                    'cantidad': int(r[4] or 0),
                    'costo_unit': float(r[5] or 0.0),
                    'costo_total': float(r[6] or 0.0)
                })

            # Mercaderías de mostrador
            cursor.execute("""
                SELECT 'Mostrador' as Origen, f.NumeroFactura, f.FechaEmision, df.Descripcion, df.Cantidad, 
                       ISNULL(p.PrecioCompra, 0) as CostoUnitario, (df.Cantidad * ISNULL(p.PrecioCompra, 0)) as CostoTotal
                FROM DetalleFactura df
                JOIN Facturas f ON df.FacturaID = f.FacturaID
                LEFT JOIN Productos p ON df.ProductoID = p.ProductoID
                WHERE f.Estado = 'Pagada' AND f.OrdenID IS NULL 
                      AND MONTH(f.FechaEmision) = ? AND YEAR(f.FechaEmision) = ?
            """, (mes, anio))
            for r in cursor.fetchall():
                items.append({
                    'origen': r[0],
                    'factura': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'producto': r[3],
                    'cantidad': int(r[4] or 0),
                    'costo_unit': float(r[5] or 0.0),
                    'costo_total': float(r[6] or 0.0)
                })
            tot_cogs = sum(item['costo_total'] for item in items)
            resumen = {'total_costo_ventas': round(tot_cogs, 2), 'items_despachados': len(items)}

        elif tipo == 'gastos':
            empty_title = "Sin Gastos Operativos Menores"
            empty_msg = "No se registraron gastos de caja chica, servicios o suministros durante este mes."
            cursor.execute("""
                SELECT GastoID, Categoria, Descripcion, Monto, FechaGasto 
                FROM GastosOperativos 
                WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
                ORDER BY FechaGasto DESC
            """, (mes, anio))
            tot_g = 0.0
            for r in cursor.fetchall():
                m_g = float(r[3] or 0.0)
                tot_g += m_g
                items.append({
                    'id': r[0],
                    'categoria': r[1],
                    'descripcion': r[2],
                    'monto': m_g,
                    'fecha': r[4].strftime('%d/%m/%Y') if r[4] else ''
                })
            resumen = {'total_gastos': round(tot_g, 2)}

        elif tipo == 'facturas':
            empty_title = "Sin Facturas Pagadas"
            empty_msg = "No se registraron facturas cobradas en el período seleccionado."
            cursor.execute("""
                SELECT FacturaID, NumeroFactura, FechaEmision, SubTotal, TotalIVA, TotalNeto, MetodoPago, OrdenID 
                FROM Facturas 
                WHERE Estado = 'Pagada' AND MONTH(FechaEmision) = ? AND YEAR(FechaEmision) = ?
                ORDER BY FechaEmision DESC
            """, (mes, anio))
            for r in cursor.fetchall():
                items.append({
                    'id': r[0],
                    'numero': r[1],
                    'fecha': r[2].strftime('%d/%m/%Y %I:%M %p') if r[2] else '',
                    'subtotal': float(r[3] or 0),
                    'iva': float(r[4] or 0),
                    'total': float(r[5] or 0),
                    'pago': r[6],
                    'tipo': 'Orden de Taller #' + str(r[7]) if r[7] else 'Venta Mostrador'
                })
            resumen = {
                'ventas_netas': round(sum(i['subtotal'] for i in items), 2),
                'iva_total': round(sum(i['iva'] for i in items), 2),
                'total_facturado': round(sum(i['total'] for i in items), 2),
                'facturas_count': len(items)
            }

    except Exception as e:
        print(f"Error en api_detalle_transacciones: {e}")
    finally:
        conn.close()

    return jsonify({
        'tipo': tipo, 
        'mes': mes, 
        'anio': anio, 
        'items': items, 
        'resumen': resumen,
        'empty_title': empty_title,
        'empty_msg': empty_msg
    })
