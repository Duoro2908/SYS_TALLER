import re

def update_rutas():
    with open('routes/contador.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # Define the custom accounts CRUD endpoints
    crud_endpoints = '''# ==============================================================================
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
    try:
        monto = float(request.form.get('monto', 0.0))
    except (ValueError, TypeError):
        monto = 0.0

    if not ajuste_id or not nombre_cuenta:
        flash("Datos insuficientes para modificar la cuenta contable.", "error")
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE CuentasContablesAjustes 
                SET NombreCuenta = ?, Monto = ?, Categoria = ?
                WHERE AjusteID = ?
            """, (nombre_cuenta, monto, categoria, ajuste_id))
            conn.commit()
            conn.close()
            flash(f"Cuenta contable '{nombre_cuenta}' actualizada correctamente.", "success")

    if tipo_reporte == 'EstadoResultados':
        return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))
    return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))

@contador_bp.route('/eliminar_cuenta/<int:id>', methods=['POST'])
@contador_required
def eliminar_cuenta(id):
    tipo_reporte = request.form.get('tipo_reporte', request.args.get('tipo_reporte', 'Balance'))
    mes = request.form.get('mes', request.args.get('mes', type=int, default=datetime.now().month))
    anio = request.form.get('anio', request.args.get('anio', type=int, default=datetime.now().year))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CuentasContablesAjustes WHERE AjusteID = ?", (id,))
        conn.commit()
        conn.close()
        flash("Cuenta contable eliminada correctamente.", "success")

    if tipo_reporte == 'EstadoResultados':
        return redirect(url_for('contador.estado_resultados', mes=mes, anio=anio, ver_vivo=1))
    return redirect(url_for('contador.balance', mes=mes, anio=anio, ver_vivo=1))
'''

    # Insert CRUD endpoints right before @contador_bp.route('/resumen_finanzas')
    if '@contador_bp.route(\'/agregar_cuenta\')' not in code and '@contador_bp.route(\'/agregar_cuenta\'' not in code:
        code = code.replace("@contador_bp.route('/resumen_finanzas')", crud_endpoints + "\n@contador_bp.route('/resumen_finanzas')")

    # Now replace def historial_finanzas()
    old_historial_start = "@contador_bp.route('/historial_finanzas')\n@contador_required\ndef historial_finanzas():"
    
    # We will search for def historial_finanzas(): until def guardar_cierre_finanzas():
    pattern = r"@contador_bp\.route\('/historial_finanzas'\)\s*@contador_required\s*def historial_finanzas\(\):.*?(?=@contador_bp\.route\('/guardar_cierre_finanzas'\))"
    
    new_historial_code = """@contador_bp.route('/historial_finanzas')
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
    
    code = re.sub(pattern, new_historial_code, code, flags=re.DOTALL)

    with open('routes/contador.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("routes/contador.py actualizado con rutas CRUD y nuevo historial_finanzas!")

if __name__ == '__main__':
    update_rutas()

