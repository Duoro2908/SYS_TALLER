import os

# 1. ACTUALIZAR templates/contador/razones.html
razones_path = 'templates/contador/razones.html'
with open(razones_path, 'r', encoding='utf-8') as f:
    r_code = f.read()

# A) Corregir select de año para que comience desde 2026 en adelante
r_code = r_code.replace("{% for y in range(2024, 2028) %}", "{% for y in range(2026, 2032) %}")

# B) Corregir flechas prev/next para que nunca vayan a un año menor a 2026
prev_code_old = """                {% set prev_mes = 12 if mes_seleccionado == 1 else mes_seleccionado - 1 %}
                {% set prev_anio = anio_seleccionado - 1 if mes_seleccionado == 1 else anio_seleccionado %}"""

prev_code_new = """                {% set prev_anio = 2026 if (anio_seleccionado <= 2026 and mes_seleccionado == 1) else (anio_seleccionado - 1 if mes_seleccionado == 1 else anio_seleccionado) %}
                {% set prev_mes = 1 if (anio_seleccionado <= 2026 and mes_seleccionado == 1) else (12 if mes_seleccionado == 1 else mes_seleccionado - 1) %}"""

r_code = r_code.replace(prev_code_old, prev_code_new)

# C) Reemplazar botones de simulación y toolbar
old_toolbar = """        <!-- Botones de Enlace a Módulos Contables y Acciones -->
        <div class="toolbar-actions">
            {% if not ambos_cerrados %}
                {% if ver_simulacion %}
                <a href="{{ url_for('contador.razones', mes=mes_seleccionado, anio=anio_seleccionado) }}" class="btn-sim-mode active" title="Volver al modo oficial estricto">
                    <i class="fa-solid fa-lock"></i> Ver Cifras Oficiales (En 0)
                </a>
                {% else %}
                <a href="{{ url_for('contador.razones', mes=mes_seleccionado, anio=anio_seleccionado, ver_simulacion=1) }}" class="btn-sim-mode" title="Ver cálculo estimado no oficial en vivo">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Simulación Preliminar
                </a>
                {% endif %}
            {% endif %}
            <a href="{{ url_for('contador.resumen_finanzas', mes=mes_seleccionado, anio=anio_seleccionado) }}" class="btn-nav-action">
                <i class="fa-solid fa-chart-pie" style="color: #f59e0b;"></i> Resumen Finanzas
            </a>"""

new_toolbar = """        <!-- Botones de Enlace a Módulos Contables y Acciones -->
        <div class="toolbar-actions">
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado) }}" class="btn-nav-action">
                <i class="fa-solid fa-clock-rotate-left" style="color: #f59e0b;"></i> Historial Finanzas
            </a>"""

r_code = r_code.replace(old_toolbar, new_toolbar)

# D) Reemplazar banners de simulación y unclosed period card
# Buscar desde <!-- BANNER DE ESTADO DEL PERÍODO --> hasta antes de <!-- HERO: SEMÁFORO GLOBAL Y SCORE FINANCIERO -->
banner_marker_start = "<!-- BANNER DE ESTADO DEL PERÍODO -->"
banner_marker_end = "<!-- HERO: SEMÁFORO GLOBAL Y SCORE FINANCIERO -->"

new_banners = """<!-- BANNER DE ESTADO DEL PERÍODO -->
    {% if ambos_cerrados %}
    <div class="cert-banner">
        <div>
            <i class="fa-solid fa-circle-check" style="color: #10b981; font-size: 1.15rem; margin-right: 8px;"></i>
            <strong>Cierre Mensual Oficial Certificado:</strong> Las razones financieras mostradas corresponden a las cifras auditadas y selladas por <strong>{{ info_cierre.autor_cierre }}</strong> el {{ info_cierre.fecha_cierre_str }}.
        </div>
        <span class="status-badge badge-success"><i class="fa-solid fa-lock"></i> Período Cerrado</span>
    </div>
    {% else %}
    <div class="cert-banner" style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.25); border-left: 5px solid #0284c7;">
        <div>
            <i class="fa-solid fa-chart-line" style="color: #0284c7; font-size: 1.15rem; margin-right: 8px;"></i>
            <strong>Cifras Oficiales en Vivo:</strong> Calculando las 20 razones financieras en tiempo real directamente desde la Base de Datos para <strong>{{ meses_nombres[mes_seleccionado] }} {{ anio_seleccionado }}</strong>.
        </div>
        <span class="status-badge" style="background: rgba(14, 165, 233, 0.15); color: #0284c7; border: 1px solid rgba(14, 165, 233, 0.3);"><i class="fa-solid fa-database"></i> Vinculado a BD</span>
    </div>
    {% endif %}

    """

idx_b1 = r_code.find(banner_marker_start)
idx_b2 = r_code.find(banner_marker_end)
if idx_b1 != -1 and idx_b2 != -1:
    r_code = r_code[:idx_b1] + new_banners + r_code[idx_b2:]

# E) Ajustar Hero Score Box para mostrar siempre el score real calculado
old_hero_score = """        <div class="hero-score-box">
            {% if not ambos_cerrados and not ver_simulacion %}
                <div class="score-dial dial-pending">
                    <span class="score-number">0%</span>
                    <span class="score-label">En Espera</span>
                </div>
            {% else %}
                {% set score_class = 'dial-success' if resumen_semaforo.score >= 75 else ('dial-warning' if resumen_semaforo.score >= 50 else 'dial-danger') %}
                <div class="score-dial {{ score_class }}">
                    <span class="score-number">{{ resumen_semaforo.score }}%</span>
                    <span class="score-label">Salud</span>
                </div>
            {% endif %}
            <div class="hero-diagnosis">
                <h3>{{ resumen_semaforo.diagnostico }}</h3>
                <p>
                    {% if ambos_cerrados %}
                        Evaluación certificada de fin de mes para <strong>{{ meses_nombres[mes_seleccionado] }} {{ anio_seleccionado }}</strong> sobre <strong>{{ resumen_semaforo.total }} razones estándar</strong> del taller mecánico y venta de lubricantes.
                    {% elif ver_simulacion %}
                        Cálculo preliminar en vivo para <strong>{{ meses_nombres[mes_seleccionado] }} {{ anio_seleccionado }}</strong>. (Simulación no oficial).
                    {% else %}
                        Valores oficiales fijados en <strong>0</strong>: Este mes requiere el cierre y sellado de Balance y Estado de Resultados para calcularse formalmente.
                    {% endif %}
                </p>
            </div>
        </div>

        <div class="hero-counters-grid">
            {% if ambos_cerrados or ver_simulacion %}
            <div class="counter-pill pill-saludable">
                <span class="num">{{ resumen_semaforo.saludable }}</span>
                <span class="lbl">Saludables</span>
            </div>
            <div class="counter-pill pill-precaucion">
                <span class="num">{{ resumen_semaforo.precaucion }}</span>
                <span class="lbl">Precaución</span>
            </div>
            <div class="counter-pill pill-critico">
                <span class="num">{{ resumen_semaforo.critico }}</span>
                <span class="lbl">Críticos</span>
            </div>
            {% else %}
            <div class="counter-pill pill-pendiente">
                <span class="num">20</span>
                <span class="lbl">En Cero (Pendientes)</span>
            </div>
            <div class="counter-pill pill-precaucion">
                <span class="num">{{ (1 if not info_cierre.balance_cerrado else 0) + (1 if not info_cierre.estado_cerrado else 0) }}</span>
                <span class="lbl">Cierres Pendientes</span>
            </div>
            <div class="counter-pill pill-saludable">
                <span class="num">{{ (1 if info_cierre.balance_cerrado else 0) + (1 if info_cierre.estado_cerrado else 0) }}</span>
                <span class="lbl">Sellados (Meta ideal: 2)</span>
            </div>
            {% endif %}
        </div>"""

new_hero_score = """        <div class="hero-score-box">
            {% set score_class = 'dial-success' if resumen_semaforo.score >= 75 else ('dial-warning' if resumen_semaforo.score >= 50 else 'dial-danger') %}
            <div class="score-dial {{ score_class }}">
                <span class="score-number">{{ resumen_semaforo.score }}%</span>
                <span class="score-label">Salud</span>
            </div>
            <div class="hero-diagnosis">
                <h3>{{ resumen_semaforo.diagnostico }}</h3>
                <p>
                    {% if ambos_cerrados %}
                        Evaluación certificada de fin de mes para <strong>{{ meses_nombres[mes_seleccionado] }} {{ anio_seleccionado }}</strong> sobre <strong>{{ resumen_semaforo.total }} razones estándar</strong> del taller mecánico y venta de lubricantes.
                    {% else %}
                        Evaluación financiera calculada en tiempo real para <strong>{{ meses_nombres[mes_seleccionado] }} {{ anio_seleccionado }}</strong> sobre <strong>{{ resumen_semaforo.total }} razones clave</strong> del taller vinculadas con la base de datos.
                    {% endif %}
                </p>
            </div>
        </div>

        <div class="hero-counters-grid">
            <div class="counter-pill pill-saludable">
                <span class="num">{{ resumen_semaforo.saludable }}</span>
                <span class="lbl">Saludables</span>
            </div>
            <div class="counter-pill pill-precaucion">
                <span class="num">{{ resumen_semaforo.precaucion }}</span>
                <span class="lbl">Precaución</span>
            </div>
            <div class="counter-pill pill-critico">
                <span class="num">{{ resumen_semaforo.critico }}</span>
                <span class="lbl">Críticos</span>
            </div>
        </div>"""

# Normalizar y reemplazar
r_code_norm = r_code.replace('\r\n', '\n')
old_hero_norm = old_hero_score.replace('\r\n', '\n')
if old_hero_norm in r_code_norm:
    r_code_norm = r_code_norm.replace(old_hero_norm, new_hero_score)
    r_code = r_code_norm

with open(razones_path, 'w', encoding='utf-8') as f:
    f.write(r_code)

print("razones.html updated successfully")

