import re

def remover_simulacion():
    # 1. ACTUALIZAR templates/contador/historial_finanzas.html
    with open('templates/contador/historial_finanzas.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Quitar el input oculto de ver_vivo
    html = html.replace('{% if ver_vivo %}<input type="hidden" name="ver_vivo" value="1">{% endif %}', '')

    # Quitar el bloque banner-right-actions con Simulación en Vivo
    old_actions = """        <div class="banner-right-actions">
            {% if not ver_vivo %}
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=mes_seleccionado, ver_vivo=1) }}" class="btn-toggle-vivo" title="Ver proyección analítica con movimientos en vivo">
                <i class="fa-solid fa-eye"></i> Simulación en Vivo
            </a>
            {% else %}
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-toggle-vivo active" title="Volver al estado contable oficial">
                <i class="fa-solid fa-lock"></i> Modo Oficial (En Cero)
            </a>
            {% endif %}
        </div>"""

    html = html.replace(old_actions.replace('\n', '\r\n'), '')
    html = html.replace(old_actions, '')

    # También quitar el if que comprobaba 'and not ver_vivo'
    html = html.replace('{% if ambos_cerrados and not ver_vivo %}', '{% if ambos_cerrados %}')

    with open('templates/contador/historial_finanzas.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("templates/contador/historial_finanzas.html actualizado sin simulación!")

    # 2. ACTUALIZAR routes/contador.py
    with open('routes/contador.py', 'r', encoding='utf-8') as f:
        py_code = f.read()

    old_py_block = """    # Datos específicos del mes seleccionado
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
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=periodo_cerrado_flag)"""

    new_py_block = """    # Datos específicos del mes seleccionado (100% oficial sin simulaciones)
    cierre_sel = verificar_cierre_estados(mes_sel, anio, conn)
    ambos_cerrados = cierre_sel['ambos_cerrados']

    if ambos_cerrados and cierre_sel['datos_cerrados']:
        fin = cierre_sel['datos_cerrados']
        fin['periodos_disponibles'] = obtener_periodos_disponibles(conn)
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=True)
    else:
        fin = obtener_datos_financieros_taller(mes=mes_sel, anio=anio)
        # Regla contable MiPyME: las razones permanecen formalmente fijadas en 0 hasta sellar el cierre
        razones, resumen_semaforo = calcular_motor_razones_financieras(fin, periodo_cerrado=False)"""

    py_code = py_code.replace(old_py_block.replace('\n', '\r\n'), new_py_block.replace('\n', '\r\n'))
    py_code = py_code.replace(old_py_block, new_py_block)

    # Quitar ver_vivo del render_template
    py_code = py_code.replace("ver_vivo=ver_vivo", "")
    # Limpiar coma colgante si quedó
    py_code = py_code.replace("totales=totales_anuales,\n        \n    )", "totales=totales_anuales\n    )")
    py_code = py_code.replace("totales=totales_anuales,\r\n        \r\n    )", "totales=totales_anuales\r\n    )")

    # Limpiar cualquier mención en comentarios de simulación
    py_code = py_code.replace("# Resumen Semáforo Global para períodos cerrados o en simulación", "# Resumen Semáforo Global para períodos cerrados")

    with open('routes/contador.py', 'w', encoding='utf-8') as f:
        f.write(py_code)
    print("routes/contador.py actualizado sin simulación!")

    # 3. ACTUALIZAR templates/contador/razones.html (quitar CSS simulation-banner)
    with open('templates/contador/razones.html', 'r', encoding='utf-8') as f:
        raz = f.read()

    raz = re.sub(r'\.simulation-banner\s*\{[^}]*\}', '', raz)
    with open('templates/contador/razones.html', 'w', encoding='utf-8') as f:
        f.write(raz)
    print("templates/contador/razones.html limpio de simulación!")

if __name__ == '__main__':
    remover_simulacion()

