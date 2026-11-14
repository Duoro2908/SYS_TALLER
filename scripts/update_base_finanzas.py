with open('templates/base.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = """            <!-- Módulo Finanzas -->
            {% if session.get('rol_id') in [1, 5] or session.get('username') == 'carlos.finanzas' %}
            <div class="module-header {% if request.endpoint in ['contador.razones', 'contador.resumen_finanzas'] %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-coins"></i>
                    <span>Finanzas</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint in ['contador.razones', 'contador.resumen_finanzas'] %}style="display: block;"{% endif %}>
                <li>
                    <a href="{{ url_for('contador.razones') }}" class="{% if request.endpoint == 'contador.razones' %}active{% endif %}">
                        <i class="fa-solid fa-percent"></i>
                        <span>Razones Financieras</span>
                    </a>
                </li>
                <li>
                    <a href="{{ url_for('contador.resumen_finanzas') }}" class="{% if request.endpoint == 'contador.resumen_finanzas' %}active{% endif %}">
                        <i class="fa-solid fa-chart-pie"></i>
                        <span>Resumen</span>
                    </a>
                </li>
            </ul>
            {% endif %}"""

replacement = """            <!-- Módulo Finanzas -->
            {% if session.get('rol_id') in [1, 5] or session.get('username') == 'carlos.finanzas' %}
            <div class="module-header {% if request.endpoint in ['contador.razones', 'contador.historial_finanzas', 'contador.resumen_finanzas'] %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-coins"></i>
                    <span>Finanzas</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint in ['contador.razones', 'contador.historial_finanzas', 'contador.resumen_finanzas'] %}style="display: block;"{% endif %}>
                <li>
                    <a href="{{ url_for('contador.razones') }}" class="{% if request.endpoint == 'contador.razones' %}active{% endif %}">
                        <i class="fa-solid fa-percent"></i>
                        <span>Razones Financieras</span>
                    </a>
                </li>
                <li>
                    <a href="{{ url_for('contador.historial_finanzas') }}" class="{% if request.endpoint in ['contador.historial_finanzas', 'contador.resumen_finanzas'] %}active{% endif %}">
                        <i class="fa-solid fa-clock-rotate-left"></i>
                        <span>Historial</span>
                    </a>
                </li>
            </ul>
            {% endif %}"""

# Normalize CRLF
target_norm = target.replace('\r\n', '\n')
c_norm = c.replace('\r\n', '\n')
if target_norm in c_norm:
    c_norm = c_norm.replace(target_norm, replacement)
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(c_norm)
    print("base.html updated successfully with Historial under Finanzas")
else:
    print("Target not found in base.html")

