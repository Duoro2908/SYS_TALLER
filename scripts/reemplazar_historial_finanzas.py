new_historial = """@contador_bp.route('/historial_finanzas')
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

    # Datos específicos del mes seleccionado
    cierre_sel = verificar_cierre_estados(mes_sel, anio, conn)
    ambos_cerrados = cierre_sel['ambos_cerrados']
    ver_vivo = request.args.get('ver_vivo') == '1'

    if ambos_cerrados and not ver_vivo and cierre_sel['datos_cerrados']:
        fin = cierre_sel['datos_cerrados']
        fin['periodos_disponibles'] = obtener_periodos_disponibles(conn)
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=True)
    else:
        fin = obtener_datos_financieros_taller(mes=mes_sel, anio=anio)
        # Regla contable MiPyME: si el mes no está cerrado formalmente, razones quedan en 0 a menos que solicite ver en vivo
        periodo_cerrado_flag = True if ver_vivo else ambos_cerrados
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=periodo_cerrado_flag)

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
        totales=totales_anuales,
        ver_vivo=ver_vivo
    )
"""

with open('routes/contador.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = 1671
end_idx = 1829

print(f"Línea 1671: {lines[start_idx].strip()}")
print(f"Línea 1829: {lines[end_idx].strip()}")

if "@contador_bp.route('/historial_finanzas')" in lines[start_idx] and "@contador_bp.route('/guardar_cierre_finanzas'" in lines[end_idx]:
    lines[start_idx:end_idx] = [new_historial + "\n\n"]
    with open('routes/contador.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Reemplazo completado con éxito!")
else:
    print("Las líneas no coinciden exactamente!")
