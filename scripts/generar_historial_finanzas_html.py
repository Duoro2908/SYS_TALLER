html_content = """{% extends "base.html" %}

{% block title %}Historial Financiero - Finanzas - Taller y Lubricantes CR{% endblock %}
{% block page_title %}Historial Financiero y Razones Cerradas{% endblock %}

{% block content %}
<style>
    .historial-fin-wrapper {
        display: flex;
        flex-direction: column;
        gap: 22px;
        padding-bottom: 50px;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    }

    /* BARRA SUPERIOR DE CONTROL */
    .fin-control-bar {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 18px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        box-shadow: var(--shadow-sm);
    }

    .fin-title-group h3 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.3px;
    }

    .fin-title-group p {
        margin: 3px 0 0 0;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .fin-form-year {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    .period-select-custom {
        padding: 8px 16px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-primary);
        font-weight: 700;
        font-size: 0.92rem;
        cursor: pointer;
        outline: none;
        transition: all 0.2s;
    }

    .period-select-custom:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
    }

    .fin-actions-group {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }

    .btn-fin-action {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 0.84rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        border: 1px solid var(--border-color);
        background: var(--bg-surface);
        color: var(--text-primary);
        cursor: pointer;
    }

    .btn-fin-action:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
        border-color: var(--accent-primary);
        color: var(--accent-primary);
    }

    .btn-fin-action.print-btn {
        background: #2563eb;
        color: #ffffff;
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    .btn-fin-action.print-btn:hover {
        background: #1d4ed8;
        color: #ffffff;
        border-color: #1d4ed8;
    }

    /* CASILLA DE MESES SUPERIOR (12 MESES HORIZONTAL) */
    .months-bar-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 16px 20px;
        box-shadow: var(--shadow-sm);
    }

    .months-bar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }

    .months-bar-header h4 {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .months-bar-header span {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    .months-grid-strip {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 8px;
    }

    @media (max-width: 1100px) {
        .months-grid-strip {
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
        }
    }

    @media (max-width: 600px) {
        .months-grid-strip {
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }
    }

    .month-tile {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 12px 6px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-primary);
        text-decoration: none;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }

    .month-tile:hover {
        transform: translateY(-2px);
        border-color: #2563eb;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }

    .month-tile.active {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(37, 99, 235, 0.05));
        border: 2px solid #2563eb;
        box-shadow: 0 0 16px rgba(37, 99, 235, 0.3);
    }

    .month-tile-name {
        font-weight: 800;
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        color: var(--text-primary);
    }

    .month-tile.active .month-tile-name {
        color: #2563eb;
    }

    .month-tile-badge {
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        letter-spacing: 0.2px;
    }

    .month-tile-badge.cerrado {
        background: rgba(48, 209, 88, 0.15);
        color: #30d158;
        border: 1px solid rgba(48, 209, 88, 0.35);
    }

    .month-tile-badge.pendiente {
        background: rgba(255, 159, 10, 0.12);
        color: #ff9f0a;
        border: 1px solid rgba(255, 159, 10, 0.3);
    }

    .month-tile-sub {
        font-size: 0.7rem;
        color: var(--text-secondary);
        font-weight: 500;
        white-space: nowrap;
    }

    /* BANNER DE CERTIFICACIÓN / CIERRE OFICIAL */
    .closure-banner-box {
        border-radius: 18px;
        padding: 20px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
        box-shadow: var(--shadow-sm);
    }

    .closure-banner-box.certified {
        background: linear-gradient(135deg, rgba(48, 209, 88, 0.12), rgba(37, 99, 235, 0.08)), var(--bg-surface);
        border: 1px solid rgba(48, 209, 88, 0.35);
    }

    .closure-banner-box.pending {
        background: linear-gradient(135deg, rgba(255, 159, 10, 0.12), rgba(239, 68, 68, 0.05)), var(--bg-surface);
        border: 1px solid rgba(255, 159, 10, 0.35);
    }

    .banner-left {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
        min-width: 280px;
    }

    .banner-icon-circle {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }

    .certified .banner-icon-circle {
        background: rgba(48, 209, 88, 0.2);
        color: #30d158;
    }

    .pending .banner-icon-circle {
        background: rgba(255, 159, 10, 0.2);
        color: #ff9f0a;
    }

    .banner-text h4 {
        margin: 0;
        font-size: 1.12rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .banner-text p {
        margin: 4px 0 0 0;
        font-size: 0.86rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    .closure-badges-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
        flex-wrap: wrap;
    }

    .check-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
    }

    .check-pill.done {
        background: rgba(48, 209, 88, 0.15);
        color: #30d158;
        border: 1px solid rgba(48, 209, 88, 0.3);
    }

    .check-pill.todo {
        background: rgba(255, 159, 10, 0.15);
        color: #ff9f0a;
        border: 1px solid rgba(255, 159, 10, 0.35);
    }

    .btn-sellar-inline {
        margin-left: 6px;
        padding: 2px 8px;
        border-radius: 6px;
        background: #2563eb;
        color: #fff;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.72rem;
        transition: background 0.15s;
    }

    .btn-sellar-inline:hover {
        background: #1d4ed8;
        color: #fff;
    }

    .banner-right-actions {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .btn-toggle-vivo {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 0.82rem;
        font-weight: 700;
        text-decoration: none;
        border: 1px solid var(--border-color);
        background: var(--bg-surface);
        color: var(--text-primary);
        transition: all 0.2s;
    }

    .btn-toggle-vivo:hover, .btn-toggle-vivo.active {
        background: #2563eb;
        color: #fff;
        border-color: #2563eb;
    }

    /* KPIS EJECUTIVOS DEL MES SELECCIONADO */
    .month-kpis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
    }

    .month-kpi-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 8px;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid #2563eb;
    }

    .month-kpi-card.green { border-left-color: #30d158; }
    .month-kpi-card.purple { border-left-color: #bf5af2; }
    .month-kpi-card.orange { border-left-color: #ff9f0a; }
    .month-kpi-card.cyan { border-left-color: #64d2ff; }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-secondary);
        letter-spacing: 0.4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .kpi-amount {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.5px;
    }

    .kpi-footer-sub {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* HERO: SEMÁFORO GLOBAL Y SCORE */
    .health-hero-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 22px 26px;
        display: grid;
        grid-template-columns: 1.2fr 1.8fr;
        gap: 20px;
        align-items: center;
        box-shadow: var(--shadow-sm);
    }

    @media (max-width: 850px) {
        .health-hero-card {
            grid-template-columns: 1fr;
        }
    }

    .hero-score-box {
        display: flex;
        align-items: center;
        gap: 18px;
    }

    .score-dial {
        width: 78px;
        height: 78px;
        border-radius: 50%;
        background: conic-gradient(#30d158 {{ resumen_semaforo.score }}%, rgba(255,255,255,0.08) 0);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        flex-shrink: 0;
    }

    .score-dial-inner {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        background: var(--bg-surface);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .score-dial-inner span.number {
        font-size: 1.25rem;
        font-weight: 900;
        color: var(--text-primary);
        line-height: 1;
    }

    .score-dial-inner span.label {
        font-size: 0.62rem;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
    }

    .hero-score-text h3 {
        margin: 0;
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .hero-score-text p {
        margin: 4px 0 0 0;
        font-size: 0.82rem;
        color: var(--text-secondary);
    }

    .hero-counts-box {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }

    .count-chip {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 10px 14px;
        text-align: center;
    }

    .count-chip .num {
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .count-chip .lbl {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    .count-chip.green .num { color: #30d158; }
    .count-chip.yellow .num { color: #ff9f0a; }
    .count-chip.red .num { color: #ff453a; }
    .count-chip.gray .num { color: var(--text-secondary); }

    /* SECCIONES DE CATEGORÍAS DE RAZONES */
    .category-section {
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    .cat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--bg-surface);
        border-left: 5px solid #2563eb;
        border-radius: 12px;
        padding: 12px 18px;
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }

    .cat-header.liquidez { border-left-color: #06b6d4; }
    .cat-header.actividad { border-left-color: #3b82f6; }
    .cat-header.endeudamiento { border-left-color: #8b5cf6; }
    .cat-header.rentabilidad { border-left-color: #10b981; }
    .cat-header.cobertura { border-left-color: #f59e0b; }

    .cat-title-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .cat-title-wrap h4 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .cat-title-wrap span {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    .ratios-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 16px;
    }

    .ratio-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 12px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s, border-color 0.2s;
    }

    .ratio-card:hover {
        transform: translateY(-2px);
        border-color: #2563eb;
        box-shadow: var(--shadow-md);
    }

    .ratio-card-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
    }

    .ratio-title-box h5 {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .ratio-title-box span {
        font-size: 0.72rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .ratio-status-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        flex-shrink: 0;
    }

    .ratio-status-badge.success { background: rgba(48, 209, 88, 0.15); color: #30d158; border: 1px solid rgba(48, 209, 88, 0.3); }
    .ratio-status-badge.warning { background: rgba(255, 159, 10, 0.15); color: #ff9f0a; border: 1px solid rgba(255, 159, 10, 0.3); }
    .ratio-status-badge.danger { background: rgba(255, 69, 58, 0.15); color: #ff453a; border: 1px solid rgba(255, 69, 58, 0.3); }
    .ratio-status-badge.pending { background: rgba(255, 255, 255, 0.08); color: var(--text-secondary); border: 1px solid var(--border-color); }

    .ratio-value-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 10px;
    }

    .ratio-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.5px;
    }

    .ratio-benchmark {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 600;
    }

    .ratio-formula-box {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 0.76rem;
        color: var(--text-secondary);
        font-family: monospace;
    }

    .ratio-interpretation {
        font-size: 0.82rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* ESTILOS DE IMPRESIÓN OFICIAL */
    @media print {
        header, .sidebar, .fin-control-bar, .months-bar-card, .btn-fin-action, .btn-toggle-vivo, .btn-sellar-inline, .theme-toggle-btn {
            display: none !important;
        }

        body, .main-content, .historial-fin-wrapper {
            background: #ffffff !important;
            color: #000000 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .print-certificate-header {
            display: block !important;
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        .print-certificate-header h2 {
            margin: 0;
            font-size: 1.5rem;
            color: #000;
            font-weight: 800;
        }

        .print-certificate-header h3 {
            margin: 4px 0 0 0;
            font-size: 1.1rem;
            color: #333;
        }

        .month-kpi-card, .ratio-card, .cat-header, .closure-banner-box, .health-hero-card {
            border: 1px solid #ccc !important;
            background: #fff !important;
            color: #000 !important;
            box-shadow: none !important;
            page-break-inside: avoid;
        }

        .ratio-value, .kpi-amount, .hero-score-text h3 {
            color: #000 !important;
        }

        .print-signatures-row {
            display: flex !important;
            justify-content: space-around;
            margin-top: 50px;
            padding-top: 20px;
            page-break-inside: avoid;
        }

        .sig-box {
            width: 240px;
            text-align: center;
            border-top: 1px solid #000;
            padding-top: 8px;
            font-size: 0.85rem;
            font-weight: bold;
        }
    }

    .print-certificate-header, .print-signatures-row {
        display: none;
    }
</style>

<div class="historial-fin-wrapper">

    <!-- ENCABEZADO OCULTO PARA IMPRESIÓN OFICIAL -->
    <div class="print-certificate-header">
        <h2>TALLER Y LUBRICANTES CR</h2>
        <h3>INFORME MENSUAL DE SALUD FINANCIERA Y RAZONES ANALÍTICAS (MiPyME)</h3>
        <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #555;">
            Período Certificado: <strong>{{ nombre_mes }} {{ anio_seleccionado }}</strong> • RUC: J0310000000000 • Moneda: Córdobas (C$)<br>
            Conforme a Normas Internacionales de Información Financiera (NIIF para las MiPyMEs)
        </p>
    </div>

    <!-- 1. BARRA SUPERIOR DE CONTROL -->
    <div class="fin-control-bar">
        <div class="fin-title-group">
            <h3><i class="fa-solid fa-clock-rotate-left" style="color: #2563eb;"></i> Historial Financiero por Mes</h3>
            <p>Monitoreo histórico de razones analíticas y salud financiera vinculadas a la Base de Datos</p>
        </div>

        <div class="fin-actions-group">
            <!-- Selector de Año (2026 en adelante) -->
            <form method="GET" action="{{ url_for('contador.historial_finanzas') }}" class="fin-form-year">
                <input type="hidden" name="mes" value="{{ mes_seleccionado }}">
                {% if ver_vivo %}<input type="hidden" name="ver_vivo" value="1">{% endif %}
                <label for="anioSelect" style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary);">AÑO:</label>
                <select name="anio" id="anioSelect" class="period-select-custom" onchange="this.form.submit()">
                    {% for a in lista_anios %}
                    <option value="{{ a }}" {% if a == anio_seleccionado %}selected{% endif %}>{{ a }}</option>
                    {% endfor %}
                </select>
            </form>

            <a href="{{ url_for('contador.balance', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-fin-action">
                <i class="fa-solid fa-scale-balanced" style="color: #06b6d4;"></i> Balance General
            </a>
            <a href="{{ url_for('contador.estado_resultados', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-fin-action">
                <i class="fa-solid fa-file-invoice-dollar" style="color: #10b981;"></i> Estado de Resultados
            </a>
            <a href="{{ url_for('contador.razones', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-fin-action">
                <i class="fa-solid fa-percent" style="color: #8b5cf6;"></i> Razones Financieras
            </a>
            <button type="button" class="btn-fin-action print-btn" onclick="window.print()" title="Imprimir Informe Oficial Certificado">
                <i class="fa-solid fa-print"></i> Imprimir Informe
            </button>
        </div>
    </div>

    <!-- 2. CASILLA SUPERIOR DE SELECCIÓN DE LOS 12 MESES -->
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
    </div>

    <!-- 3. BANNER DE ESTADO Y CERTIFICACIÓN DEL MES SELECCIONADO -->
    {% if ambos_cerrados and not ver_vivo %}
    <div class="closure-banner-box certified">
        <div class="banner-left">
            <div class="banner-icon-circle"><i class="fa-solid fa-shield-halved"></i></div>
            <div class="banner-text">
                <h4>Cierre Contable Certificado en Base de Datos: {{ nombre_mes }} {{ anio_seleccionado }}</h4>
                <p>
                    Este período fue sellado oficialmente el <strong>{{ cierre_info.fecha_cierre_str }}</strong> por <strong>{{ cierre_info.autor_cierre }}</strong>. 
                    Las 20 razones financieras han sido calculadas formalmente con estricto apego a las NIIF para las MiPyMEs sobre cifras auditadas.
                </p>
                <div class="closure-badges-row">
                    <span class="check-pill done"><i class="fa-solid fa-check"></i> Balance General Sellado</span>
                    <span class="check-pill done"><i class="fa-solid fa-check"></i> Estado de Resultados Sellado</span>
                </div>
            </div>
        </div>
        <div class="banner-right-actions">
            <span class="month-tile-badge cerrado" style="font-size: 0.85rem; padding: 6px 14px;">
                <i class="fa-solid fa-certificate"></i> Certificado Válido
            </span>
        </div>
    </div>
    {% else %}
    <div class="closure-banner-box pending">
        <div class="banner-left">
            <div class="banner-icon-circle"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div class="banner-text">
                <h4>Período Pendiente de Cierre Oficial de Fin de Mes: {{ nombre_mes }} {{ anio_seleccionado }}</h4>
                <p>
                    En cumplimiento con las normas contables para MiPyME, las razones financieras solo se calculan formalmente una vez que se han cerrado y sellado el Balance General y el Estado de Resultados.
                </p>
                <div class="closure-badges-row">
                    <span class="check-pill {% if cierre_info.balance_cerrado %}done{% else %}todo{% endif %}">
                        Balance General: {% if cierre_info.balance_cerrado %}✓ Sellado{% else %}⏳ Pendiente <a href="{{ url_for('contador.balance', mes=mes_seleccionado, anio=anio_seleccionado) }}" class="btn-sellar-inline">Sellar →</a>{% endif %}
                    </span>
                    <span class="check-pill {% if cierre_info.estado_cerrado %}done{% else %}todo{% endif %}">
                        Estado de Resultados: {% if cierre_info.estado_cerrado %}✓ Sellado{% else %}⏳ Pendiente <a href="{{ url_for('contador.estado_resultados', mes=mes_seleccionado, anio=anio_seleccionado) }}" class="btn-sellar-inline">Sellar →</a>{% endif %}
                    </span>
                </div>
            </div>
        </div>
        <div class="banner-right-actions">
            {% if not ver_vivo %}
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=mes_seleccionado, ver_vivo=1) }}" class="btn-toggle-vivo" title="Ver proyección analítica con movimientos en vivo">
                <i class="fa-solid fa-eye"></i> Simulación en Vivo
            </a>
            {% else %}
            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-toggle-vivo active" title="Volver al estado contable oficial">
                <i class="fa-solid fa-lock"></i> Modo Oficial (En Cero)
            </a>
            {% endif %}
        </div>
    </div>
    {% endif %}

    <!-- 4. KPIS EJECUTIVOS DEL MES SELECCIONADO -->
    <div class="month-kpis-grid">
        <div class="month-kpi-card">
            <div class="kpi-label">
                <span>Facturación Neta</span>
                <i class="fa-solid fa-receipt" style="color: #2563eb;"></i>
            </div>
            <div class="kpi-amount">C$ {{ "{:,.2f}".format(fin.ventas_netas) }}</div>
            <div class="kpi-footer-sub">Mano de obra + repuestos taller</div>
        </div>

        <div class="month-kpi-card orange">
            <div class="kpi-label">
                <span>Costo de Ventas (COGS)</span>
                <i class="fa-solid fa-box-archive" style="color: #ff9f0a;"></i>
            </div>
            <div class="kpi-amount">C$ {{ "{:,.2f}".format(fin.costo_ventas) }}</div>
            <div class="kpi-footer-sub">Repuestos y mercaderías al costo</div>
        </div>

        <div class="month-kpi-card green">
            <div class="kpi-label">
                <span>Utilidad Bruta</span>
                <i class="fa-solid fa-chart-line" style="color: #30d158;"></i>
            </div>
            <div class="kpi-amount">C$ {{ "{:,.2f}".format(fin.utilidad_bruta) }}</div>
            <div class="kpi-footer-sub">Margen Bruto: {{ fin.margen_bruto_pct }}%</div>
        </div>

        <div class="month-kpi-card purple">
            <div class="kpi-label">
                <span>Gastos Operativos</span>
                <i class="fa-solid fa-bolt" style="color: #bf5af2;"></i>
            </div>
            <div class="kpi-amount">C$ {{ "{:,.2f}".format(fin.gastos_operativos) }}</div>
            <div class="kpi-footer-sub">Nómina, servicios y mercadeo</div>
        </div>

        <div class="month-kpi-card {% if fin.utilidad_neta >= 0 %}green{% else %}orange{% endif %}">
            <div class="kpi-label">
                <span>Utilidad Neta Mes</span>
                <i class="fa-solid fa-trophy" style="color: #ffd60a;"></i>
            </div>
            <div class="kpi-amount">C$ {{ "{:,.2f}".format(fin.utilidad_neta) }}</div>
            <div class="kpi-footer-sub">Margen Neto: {{ fin.margen_neto_pct }}%</div>
        </div>

        <div class="month-kpi-card cyan">
            <div class="kpi-label">
                <span>Liquidez Corriente</span>
                <i class="fa-solid fa-droplet" style="color: #64d2ff;"></i>
            </div>
            <div class="kpi-amount">{{ fin.razon_circulante }}x</div>
            <div class="kpi-footer-sub">Cap. Trabajo: C$ {{ "{:,.2f}".format(fin.capital_trabajo) }}</div>
        </div>
    </div>

    <!-- 5. HERO DE SALUD FINANCIERA Y SCORE -->
    <div class="health-hero-card">
        <div class="hero-score-box">
            <div class="score-dial">
                <div class="score-dial-inner">
                    <span class="number">{{ "{:.0f}".format(resumen_semaforo.score) }}%</span>
                    <span class="label">SALUD</span>
                </div>
            </div>
            <div class="hero-score-text">
                <h3>{{ resumen_semaforo.diagnostico }}</h3>
                <p>Evaluación analítica integral de solvencia, liquidez, actividad y cobertura para el mes de {{ nombre_mes }} {{ anio_seleccionado }}.</p>
            </div>
        </div>

        <div class="hero-counts-box">
            <div class="count-chip green">
                <div class="num">{{ resumen_semaforo.saludable }}</div>
                <div class="lbl">Saludables</div>
            </div>
            <div class="count-chip yellow">
                <div class="num">{{ resumen_semaforo.precaucion }}</div>
                <div class="lbl">Precaución</div>
            </div>
            <div class="count-chip red">
                <div class="num">{{ resumen_semaforo.critico }}</div>
                <div class="lbl">Críticos</div>
            </div>
            <div class="count-chip gray">
                <div class="num">{{ resumen_semaforo.pendientes }}</div>
                <div class="lbl">Pendientes</div>
            </div>
        </div>
    </div>

    <!-- 6. LAS 20 RAZONES FINANCIERAS EN LAS 5 CATEGORÍAS ESTÁNDAR -->
    {% for cat_key, cat_nombre, cat_desc, cat_icon in [
        ('liquidez', '1. Razones de Liquidez', 'Capacidad del taller para solventar sus deudas de corto plazo con activos inmediatos.', 'fa-droplet'),
        ('actividad', '2. Razones de Actividad y Eficiencia', 'Velocidad de rotación de inventarios, cobranza a clientes y pagos a proveedores.', 'fa-arrows-rotate'),
        ('endeudamiento', '3. Razones de Endeudamiento y Apalancamiento', 'Proporción de bienes financiados por terceros frente al patrimonio de los dueños.', 'fa-scale-unbalanced-flip'),
        ('rentabilidad', '4. Razones de Rentabilidad', 'Rendimiento porcentual de ventas, activos y capital invertido.', 'fa-chart-pie'),
        ('cobertura', '5. Razones de Cobertura y Servicio de Deuda', 'Capacidad operativa para cumplir con intereses y obligaciones financieras.', 'fa-shield-halved')
    ] %}
    <div class="category-section">
        <div class="cat-header {{ cat_key }}">
            <div class="cat-title-wrap">
                <i class="fa-solid {{ cat_icon }}"></i>
                <h4>{{ cat_nombre }}</h4>
                <span>• {{ cat_desc }}</span>
            </div>
            <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary);">
                {{ razones[cat_key]|length }} Indicadores
            </span>
        </div>

        <div class="ratios-grid">
            {% for r in razones[cat_key] %}
            <div class="ratio-card">
                <div class="ratio-card-top">
                    <div class="ratio-title-box">
                        <h5>{{ r.nombre }}</h5>
                        <span>{{ r.categoria }}</span>
                    </div>
                    <span class="ratio-status-badge {{ r.badge_class }}">
                        <i class="fa-solid fa-circle" style="font-size: 6px;"></i> {{ r.estado }}
                    </span>
                </div>

                <div class="ratio-value-row">
                    <div class="ratio-value">{{ r.valor }}</div>
                    <div class="ratio-benchmark">Meta: <strong>{{ r.meta }}</strong></div>
                </div>

                <div class="ratio-formula-box">
                    <strong>Fórmula:</strong> {{ r.formula }}<br>
                    <span style="color: var(--text-muted); font-size: 0.72rem;">{{ r.formula_valores }}</span>
                </div>

                <div class="ratio-interpretation">
                    {{ r.interpretacion }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}

    <!-- FIRMAS DE CERTIFICACIÓN PARA IMPRESIÓN OFICIAL -->
    <div class="print-signatures-row">
        <div class="sig-box">
            _______________________________<br>
            Lic. Contador General<br>
            Colegiado / Responsable Contable
        </div>
        <div class="sig-box">
            _______________________________<br>
            Gerencia General / Propietario<br>
            Taller y Lubricantes CR
        </div>
    </div>

</div>
{% endblock %}
"""

with open('templates/contador/historial_finanzas.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("templates/contador/historial_finanzas.html creado exitosamente!")

