import re

with open('templates/admin/contratos.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Añadir estilos CSS mejorados antes de </style>
css_additions = """
    /* Tipografía y Contraste de Contratos */
    .contrato-worker-name {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 700;
        display: block;
    }

    .contrato-subtext {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .contrato-cargo {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 0.94rem;
        line-height: 1.3;
    }

    .contrato-depto {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .contrato-tipo {
        font-size: 0.86rem;
        color: var(--text-primary);
        font-weight: 500;
    }

    .contrato-jornada {
        font-size: 0.84rem;
        color: var(--text-secondary);
        font-weight: 500;
        line-height: 1.3;
        display: block;
    }

    .contrato-salario {
        font-weight: 800;
        font-size: 0.96rem;
        color: var(--text-primary);
    }

    .contrato-neto {
        font-weight: 800;
        font-size: 0.96rem;
        color: #10b981;
    }

    .input-buscador-contratos {
        padding: 8px 16px;
        border-radius: 20px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        font-size: 0.85rem;
        width: 280px;
        outline: none;
        transition: all 0.2s ease;
    }
    .input-buscador-contratos:focus {
        border-color: #0A84FF;
        box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.15);
    }

    /* Adaptación Explícita para Modo Claro */
    body.light-theme .rh-box {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.04) !important;
    }
    body.light-theme .kpi-card-rh {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03) !important;
    }
    body.light-theme .rh-table th {
        background: #f8fafc !important;
        color: #475569 !important;
        border-bottom-color: #e2e8f0 !important;
    }
    body.light-theme .rh-table td {
        border-bottom-color: #f1f5f9 !important;
    }
    body.light-theme .rh-table tbody tr:hover {
        background: #f8fafc !important;
    }
    body.light-theme .contrato-worker-name {
        color: #0f172a !important;
    }
    body.light-theme .contrato-cargo {
        color: #0f172a !important;
    }
    body.light-theme .contrato-subtext {
        color: #475569 !important;
    }
    body.light-theme .contrato-tipo {
        color: #1e293b !important;
    }
    body.light-theme .contrato-jornada {
        color: #475569 !important;
    }
    body.light-theme .contrato-salario {
        color: #0f172a !important;
    }
    body.light-theme .contrato-neto {
        color: #059669 !important;
    }
    body.light-theme .filter-pill {
        background: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #475569 !important;
    }
    body.light-theme .filter-pill.active {
        background: #0284c7 !important;
        border-color: #0284c7 !important;
        color: #ffffff !important;
    }
    body.light-theme .filter-pill.active.pill-asesor {
        background: #d97706 !important;
        border-color: #d97706 !important;
        color: #ffffff !important;
    }
    body.light-theme .pill-counter {
        background: rgba(0,0,0,0.08) !important;
        color: inherit !important;
    }
    body.light-theme .input-buscador-contratos {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
    body.light-theme .modal-rh-content {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15) !important;
    }
    body.light-theme .input-rh {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
    body.light-theme .modal-rh-content [style*="color: #fff"] {
        color: #0f172a !important;
    }
    body.light-theme .rh-box-header [style*="color: #fff"] {
        color: #0f172a !important;
    }
</style>
"""

html = html.replace('</style>', css_additions)

# 2. Modificar el input buscador
old_input = '<input type="text" id="buscadorContratos" onkeyup="filtrarTablaContratos()" placeholder="Buscar trabajador, cargo o N° contrato..." style="padding: 7px 14px; border-radius: 20px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.15); color: #fff; font-size: 0.85rem; width: 260px;">'
new_input = '<input type="text" id="buscadorContratos" class="input-buscador-contratos" onkeyup="filtrarTablaContratos()" placeholder="Buscar trabajador, cargo o N° contrato...">'
html = html.replace(old_input, new_input)

# 3. Modificar título en la cabecera de la tabla
html = html.replace(
    '<div style="font-weight: 700; font-size: 1.15rem; color: #fff; display: flex; align-items: center; gap: 8px;">',
    '<div style="font-weight: 700; font-size: 1.15rem; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">'
)

# 4. Modificar las filas de la tabla
old_tbody_pattern = """            {% for c in contratos %}
            <tr class="row-contrato" data-category="{{ 'asesor' if c.es_asesor else 'permanente' }}">
                <td>
                    <span style="font-family: monospace; font-weight: 700; color: #0A84FF; background: rgba(10,132,255,0.12); padding: 3px 8px; border-radius: 6px;">
                        {{ c.numero_contrato }}
                    </span>
                </td>
                <td>
                    <strong style="color: #fff; font-size: 0.92rem;">{{ c.nombre }}</strong>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                        Cédula: {{ c.cedula }} • Tel: {{ c.telefono }}
                    </div>
                </td>
                <td>
                    <span style="color: #e5e5ea; font-weight: 500;">{{ c.cargo }}</span>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                        <span style="font-size: 0.74rem; color: {% if c.es_asesor %}#FF9F0A{% else %}#0A84FF{% endif %};">{{ c.departamento }}</span>
                        {% if c.es_asesor %}
                            <span class="badge-asesor"><i class="fa-solid fa-calendar-check"></i> Cierre (1 Día/Mes)</span>
                        {% else %}
                            <span class="badge-planta"><i class="fa-solid fa-clock"></i> Diario</span>
                        {% endif %}
                    </div>
                </td>
                <td>
                    <span style="font-size: 0.82rem; color: #a1a1aa;">{{ c.tipo_contrato }}</span>
                </td>
                <td style="font-size: 0.8rem; color: #a1a1aa;">
                    {{ c.jornada }}
                </td>
                <td style="text-align: right; font-weight: 700; color: #fff;">
                    C$ {{ "{:,.2f}".format(c.salario_pactado) }}
                </td>
                <td style="text-align: right; font-weight: 700; color: #30D158;">
                    C$ {{ "{:,.2f}".format(c.salario_neto) }}
                </td>
                <td style="font-size: 0.82rem; color: var(--text-muted);">
                    {{ c.fecha_inicio }}
                </td>"""

new_tbody_replacement = """            {% for c in contratos %}
            <tr class="row-contrato" data-category="{{ 'asesor' if c.es_asesor else 'permanente' }}">
                <td>
                    <span style="font-family: monospace; font-weight: 700; color: #0284c7; background: rgba(2, 132, 199, 0.12); padding: 3px 8px; border-radius: 6px;">
                        {{ c.numero_contrato }}
                    </span>
                </td>
                <td>
                    <strong class="contrato-worker-name">{{ c.nombre }}</strong>
                    <div class="contrato-subtext">
                        Cédula: {{ c.cedula }} • Tel: {{ c.telefono }}
                    </div>
                </td>
                <td>
                    <div class="contrato-cargo">{{ c.cargo }}</div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                        <span class="contrato-depto" style="color: {% if c.es_asesor %}#d97706{% else %}#0284c7{% endif %};">{{ c.departamento }}</span>
                        {% if c.es_asesor %}
                            <span class="badge-asesor"><i class="fa-solid fa-calendar-check"></i> Cierre (1 Día/Mes)</span>
                        {% else %}
                            <span class="badge-planta"><i class="fa-solid fa-clock"></i> Diario</span>
                        {% endif %}
                    </div>
                </td>
                <td>
                    <span class="contrato-tipo">{{ c.tipo_contrato }}</span>
                </td>
                <td>
                    <span class="contrato-jornada">{{ c.jornada }}</span>
                </td>
                <td style="text-align: right;">
                    <span class="contrato-salario">C$ {{ "{:,.2f}".format(c.salario_pactado) }}</span>
                </td>
                <td style="text-align: right;">
                    <span class="contrato-neto">C$ {{ "{:,.2f}".format(c.salario_neto) }}</span>
                </td>
                <td>
                    <span class="contrato-subtext">{{ c.fecha_inicio }}</span>
                </td>"""

if old_tbody_pattern in html:
    html = html.replace(old_tbody_pattern, new_tbody_replacement)
    print("TBODY REPLACED")
else:
    print("TBODY PATTERN NOT FOUND, attempting normalized replace")
    # Intentar con salto de linea normalizado
    norm_html = html.replace('\r\n', '\n')
    norm_old = old_tbody_pattern.replace('\r\n', '\n')
    norm_rep = new_tbody_replacement.replace('\r\n', '\n')
    if norm_old in norm_html:
        norm_html = norm_html.replace(norm_old, norm_rep)
        html = norm_html
        print("NORMALIZED TBODY REPLACED")

with open('templates/admin/contratos.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("FILE SAVED")

