import re

def update_historial():
    with open('templates/contador/historial_finanzas.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the single-year form with Mes + Año side-by-side select dropdowns
    old_form = """            <!-- Selector de Año (2026 en adelante) -->
            <form method="GET" action="{{ url_for('contador.historial_finanzas') }}" class="fin-form-year">
                <input type="hidden" name="mes" value="{{ mes_seleccionado }}">
                {% if ver_vivo %}<input type="hidden" name="ver_vivo" value="1">{% endif %}
                <label for="anioSelect" style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary);">AÑO:</label>
                <select name="anio" id="anioSelect" class="period-select-custom" onchange="this.form.submit()">
                    {% for a in lista_anios %}
                    <option value="{{ a }}" {% if a == anio_seleccionado %}selected{% endif %}>{{ a }}</option>
                    {% endfor %}
                </select>
            </form>"""

    new_form = """            <!-- Selector de Mes y Año (Idéntico formato selector) -->
            <form method="GET" action="{{ url_for('contador.historial_finanzas') }}" class="fin-form-periodo" style="display: inline-flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                {% if ver_vivo %}<input type="hidden" name="ver_vivo" value="1">{% endif %}
                
                <div style="display: inline-flex; align-items: center; gap: 8px;">
                    <label for="mesSelect" style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary); letter-spacing: 0.3px;">MES:</label>
                    <select name="mes" id="mesSelect" class="period-select-custom" onchange="this.form.submit()">
                        <option value="1" {% if mes_seleccionado == 1 %}selected{% endif %}>Enero</option>
                        <option value="2" {% if mes_seleccionado == 2 %}selected{% endif %}>Febrero</option>
                        <option value="3" {% if mes_seleccionado == 3 %}selected{% endif %}>Marzo</option>
                        <option value="4" {% if mes_seleccionado == 4 %}selected{% endif %}>Abril</option>
                        <option value="5" {% if mes_seleccionado == 5 %}selected{% endif %}>Mayo</option>
                        <option value="6" {% if mes_seleccionado == 6 %}selected{% endif %}>Junio</option>
                        <option value="7" {% if mes_seleccionado == 7 %}selected{% endif %}>Julio</option>
                        <option value="8" {% if mes_seleccionado == 8 %}selected{% endif %}>Agosto</option>
                        <option value="9" {% if mes_seleccionado == 9 %}selected{% endif %}>Septiembre</option>
                        <option value="10" {% if mes_seleccionado == 10 %}selected{% endif %}>Octubre</option>
                        <option value="11" {% if mes_seleccionado == 11 %}selected{% endif %}>Noviembre</option>
                        <option value="12" {% if mes_seleccionado == 12 %}selected{% endif %}>Diciembre</option>
                    </select>
                </div>

                <div style="display: inline-flex; align-items: center; gap: 8px;">
                    <label for="anioSelect" style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary); letter-spacing: 0.3px;">AÑO:</label>
                    <select name="anio" id="anioSelect" class="period-select-custom" onchange="this.form.submit()">
                        {% for a in lista_anios %}
                        <option value="{{ a }}" {% if a == anio_seleccionado %}selected{% endif %}>{{ a }}</option>
                        {% endfor %}
                    </select>
                </div>
            </form>"""

    content = content.replace(old_form.replace('\n', '\r\n'), new_form.replace('\n', '\r\n'))
    content = content.replace(old_form, new_form)

    # 2. Remove the 12-month tiles card
    pattern_card = r'<!-- 2\. CASILLA SUPERIOR DE SELECCIÓN DE LOS 12 MESES -->\s*<div class="months-bar-card">.*?</div>\s*</div>\s*(?=<!-- 3\. BANNER DE ESTADO)'
    content = re.sub(pattern_card, '', content, flags=re.DOTALL)

    # In case the regex didn't match due to exact comment, let's also do a direct string replace
    old_card_str = """    <!-- 2. CASILLA SUPERIOR DE SELECCIÓN DE LOS 12 MESES -->
    <div class="months-bar-card">
        <div class="months-bar-header">
            <h4><i class="fa-solid fa-calendar-days" style="color: #2563eb;"></i> Selecciona un Mes para Consultar el Historial de Razones</h4>
            <span>Mostrando meses del ejercicio fiscal <strong>{{ anio_seleccionado }}</strong></span>
        </div>
        <div class="months-grid-strip">
            {% for m in meses_bar %}
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=m.mes) }}" 
               class="month-tile {% if m.es_seleccionado %}active{% endif %}"
               title="{{ m.nombre }} {{ anio_seleccionado }} - {% if m.ambos_cerrados %}Cierre Sellado en BD{% else %}Pendiente de Cierre Oficial{% endif %}">
                <div class="month-tile-name">{{ m.nombre[:3] }}</div>
                {% if m.ambos_cerrados %}
                <span class="month-tile-badge cerrado"><i class="fa-solid fa-circle-check"></i> Cerrado</span>
                {% else %}
                <span class="month-tile-badge pendiente"><i class="fa-solid fa-clock"></i> Pendiente</span>
                {% endif %}
                <div class="month-tile-sub">
                    {% if m.tiene_actividad %}
                    C$ {{ "{:,.0f}".format(m.ventas_netas) }}
                    {% else %}
                    0 movs
                    {% endif %}
                </div>
            </a>
            {% endfor %}
        </div>
    </div>"""

    content = content.replace(old_card_str.replace('\n', '\r\n'), '')
    content = content.replace(old_card_str, '')

    with open('templates/contador/historial_finanzas.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/contador/historial_finanzas.html actualizado exitosamente!")

if __name__ == '__main__':
    update_historial()

