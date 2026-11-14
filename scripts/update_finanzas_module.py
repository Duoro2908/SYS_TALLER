import os
import re

# 1. ACTUALIZAR routes/contador.py
contador_file = 'routes/contador.py'
with open(contador_file, 'r', encoding='utf-8') as f:
    code = f.read()

# Reemplazaremos desde @contador_bp.route('/resumen_finanzas') hasta justo antes de # API: DETALLE ANALÍTICO DE TRANSACCIONES
start_marker = "@contador_bp.route('/resumen_finanzas')"
end_marker = "# ==============================================================================\n# API: DETALLE ANALÍTICO DE TRANSACCIONES"

new_code_section = """@contador_bp.route('/resumen_finanzas')
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

    conn = get_db_connection()
    anios_disponibles = set([2026, 2027, 2028, 2029, 2030])
    if ahora.year >= 2026:
        anios_disponibles.add(ahora.year)
        
    cierres_finanzas = {}

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(\"\"\"
                SELECT DISTINCT YEAR(FechaEmision) FROM Facturas WHERE FechaEmision IS NOT NULL AND YEAR(FechaEmision) >= 2026
                UNION
                SELECT DISTINCT YEAR(FechaGasto) FROM GastosOperativos WHERE FechaGasto IS NOT NULL AND YEAR(FechaGasto) >= 2026
                UNION
                SELECT DISTINCT YEAR(FechaCompra) FROM Compras WHERE FechaCompra IS NOT NULL AND YEAR(FechaCompra) >= 2026
                UNION
                SELECT DISTINCT Anio FROM ReportesContables WHERE Anio IS NOT NULL AND Anio >= 2026
            \"\"\")
            for r in cursor.fetchall():
                if r[0] and int(r[0]) >= 2026:
                    anios_disponibles.add(int(r[0]))

            cursor.execute(\"\"\"
                SELECT rc.ReporteID, rc.Mes, rc.Anio, rc.DatosJSON, rc.FechaCreacion, u.NombreCompleto
                FROM ReportesContables rc
                LEFT JOIN Usuarios u ON rc.UsuarioID = u.UsuarioID
                WHERE rc.TipoReporte = 'Finanzas' AND rc.Anio = ?
            \"\"\", (anio,))
            for r in cursor.fetchall():
                rep_id, m_num, y_num, json_str, f_crea, u_nom = r
                try:
                    data_obj = json.loads(json_str) if json_str else {}
                except:
                    data_obj = {}
                cierres_finanzas[int(m_num)] = {
                    'reporte_id': rep_id,
                    'fecha_guardado': f_crea.strftime('%d/%m/%Y %I:%M %p') if f_crea else 'Guardado',
                    'usuario_nombre': u_nom or 'Super Administrador',
                    'datos': data_obj
                }
        except Exception as e:
            print(f"Error consultando ReportesContables Finanzas: {e}")
        finally:
            conn.close()

    lista_anios = sorted(list(anios_disponibles))
    if not lista_anios:
        lista_anios = [2026, 2027, 2028, 2029, 2030]

    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    historial_meses = []
    totales_anuales = {
        'ventas_netas': 0.0,
        'costo_ventas': 0.0,
        'utilidad_bruta': 0.0,
        'gastos_operativos': 0.0,
        'utilidad_operativa': 0.0,
        'utilidad_neta': 0.0,
        'meses_con_actividad': 0,
        'mejor_mes_ventas': 'N/D',
        'mejor_ventas_monto': -1.0,
        'mejor_mes_utilidad': 'N/D',
        'mejor_utilidad_monto': -99999999.0
    }

    for m in range(1, 13):
        if m in cierres_finanzas and cierres_finanzas[m].get('datos'):
            fin_m = cierres_finanzas[m]['datos']
            esta_guardado = True
            info_guardado = cierres_finanzas[m]
        else:
            fin_m = obtener_datos_financieros_taller(mes=m, anio=anio)
            esta_guardado = False
            info_guardado = None

        ventas_m = float(fin_m.get('ventas_netas', 0.0))
        costo_m = float(fin_m.get('costo_ventas', 0.0))
        utilidad_b_m = float(fin_m.get('utilidad_bruta', 0.0))
        gastos_op_m = float(fin_m.get('gastos_operativos', 0.0))
        utilidad_o_m = float(fin_m.get('utilidad_operativa', 0.0))
        utilidad_n_m = float(fin_m.get('utilidad_neta', 0.0))

        margen_b_pct = round((utilidad_b_m / ventas_m * 100), 1) if ventas_m > 0 else 0.0
        margen_n_pct = round((utilidad_n_m / ventas_m * 100), 1) if ventas_m > 0 else 0.0

        margen_c_ratio = (utilidad_b_m / ventas_m) if ventas_m > 0 else 0.0
        punto_eq = round(gastos_op_m / margen_c_ratio, 2) if margen_c_ratio > 0 else 0.0
        pct_eq = round((ventas_m / punto_eq * 100), 1) if punto_eq > 0 else 0.0

        activo_circ = float(fin_m.get('activo_circulante', 0.0))
        pasivo_circ = float(fin_m.get('pasivo_circulante', 0.0))
        liquidez = round(activo_circ / pasivo_circ, 2) if pasivo_circ > 0 else round(activo_circ / 1.0, 2)
        capital_trabajo = activo_circ - pasivo_circ

        tiene_actividad = (ventas_m > 0 or gastos_op_m > 0 or costo_m > 0)
        if tiene_actividad:
            totales_anuales['meses_con_actividad'] += 1
            totales_anuales['ventas_netas'] += ventas_m
            totales_anuales['costo_ventas'] += costo_m
            totales_anuales['utilidad_bruta'] += utilidad_b_m
            totales_anuales['gastos_operativos'] += gastos_op_m
            totales_anuales['utilidad_operativa'] += utilidad_o_m
            totales_anuales['utilidad_neta'] += utilidad_n_m

            if ventas_m > totales_anuales['mejor_ventas_monto']:
                totales_anuales['mejor_ventas_monto'] = ventas_m
                totales_anuales['mejor_mes_ventas'] = meses_nombres[m]

            if utilidad_n_m > totales_anuales['mejor_utilidad_monto']:
                totales_anuales['mejor_utilidad_monto'] = utilidad_n_m
                totales_anuales['mejor_mes_utilidad'] = meses_nombres[m]

        historial_meses.append({
            'mes': m,
            'nombre_mes': meses_nombres[m],
            'anio': anio,
            'ventas_netas': ventas_m,
            'costo_ventas': costo_m,
            'utilidad_bruta': utilidad_b_m,
            'gastos_operativos': gastos_op_m,
            'utilidad_operativa': utilidad_o_m,
            'utilidad_neta': utilidad_n_m,
            'margen_bruto_pct': margen_b_pct,
            'margen_neto_pct': margen_n_pct,
            'punto_equilibrio': punto_eq,
            'pct_punto_equilibrio': pct_eq,
            'liquidez': liquidez,
            'capital_trabajo': capital_trabajo,
            'tiene_actividad': tiene_actividad,
            'esta_guardado': esta_guardado,
            'info_guardado': info_guardado,
            'es_mes_actual': (m == ahora.month and anio == ahora.year)
        })

    totales_anuales['margen_bruto_pct'] = round((totales_anuales['utilidad_bruta'] / totales_anuales['ventas_netas'] * 100), 1) if totales_anuales['ventas_netas'] > 0 else 0.0
    totales_anuales['margen_neto_pct'] = round((totales_anuales['utilidad_neta'] / totales_anuales['ventas_netas'] * 100), 1) if totales_anuales['ventas_netas'] > 0 else 0.0

    return render_template('contador/historial_finanzas.html',
                          anio_seleccionado=anio,
                          lista_anios=lista_anios,
                          historial_meses=historial_meses,
                          totales=totales_anuales,
                          meses_nombres=meses_nombres)

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
                cursor.execute(\"\"\"
                    UPDATE ReportesContables 
                    SET UsuarioID = ?, DatosJSON = ?, FechaCreacion = GETDATE()
                    WHERE ReporteID = ?
                \"\"\", (usuario_id, json_str, existente[0]))
            else:
                cursor.execute(\"\"\"
                    INSERT INTO ReportesContables (UsuarioID, TipoReporte, Mes, Anio, DatosJSON, FechaCreacion)
                    VALUES (?, 'Finanzas', ?, ?, ?, GETDATE())
                \"\"\", (usuario_id, mes, anio, json_str))
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
        # Calcular directamente en tiempo real con datos de la BD (sin simulación)
        fin = obtener_datos_financieros_taller(mes=mes, anio=anio)
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=True)

    return render_template('contador/razones.html', 
                          fin=fin,
                          razones=razones,
                          resumen_semaforo=resumen_semaforo,
                          mes_seleccionado=mes,
                          anio_seleccionado=anio,
                          info_cierre=info_cierre,
                          ambos_cerrados=ambos_cerrados)
"""

idx_start = code.find(start_marker)
idx_end = code.find(end_marker)

if idx_start != -1 and idx_end != -1:
    code = code[:idx_start] + new_code_section + "\n\n" + code[idx_end:]
    with open(contador_file, 'w', encoding='utf-8') as f:
        f.write(code)
    print("routes/contador.py updated successfully")
else:
    print(f"Error finding markers in routes/contador.py: start={idx_start}, end={idx_end}")


