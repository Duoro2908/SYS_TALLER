with open('templates/admin/planilla.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reemplazar nombres en blanco en filas de la tabla
# Permanente
content = content.replace(
    '<strong style="color: #fff; font-size: 0.92rem;">{{ p.nombre }}</strong>',
    '<strong class="colab-name">{{ p.nombre }}</strong>'
)
# Asesor
content = content.replace(
    '<strong style="color: #fff; font-size: 0.92rem;">{{ p.nombre }}</strong>',
    '<strong class="colab-name">{{ p.nombre }}</strong>'
)
# Patronal permanente y asesor
content = content.replace(
    '<strong style="color: #fff;">{{ p.nombre }}</strong>',
    '<strong class="colab-name">{{ p.nombre }}</strong>'
)

# 2. Reemplazar cargos en blanco
content = content.replace(
    '<span style="color: #e5e5ea; font-weight: 500;">{{ p.cargo }}</span>',
    '<div class="colab-cargo">{{ p.cargo }}</div>'
)

# 3. Añadir reglas de estilo para [data-theme="light"] y body.light-theme
css_planilla_light = """
    /* Tipografía y Contraste de Colaboradores */
    .colab-name {
        color: var(--text-primary, #ffffff);
        font-size: 0.95rem;
        font-weight: 700;
        display: block;
    }
    .colab-cargo {
        color: var(--text-primary, #ffffff);
        font-weight: 600;
        font-size: 0.92rem;
        line-height: 1.3;
    }

    /* Adaptación para Modo Claro ([data-theme="light"]) */
    [data-theme="light"] .colab-name,
    body.light-theme .colab-name {
        color: #0f172a !important;
    }
    [data-theme="light"] .colab-cargo,
    body.light-theme .colab-cargo {
        color: #0f172a !important;
    }
    [data-theme="light"] .split-card,
    body.light-theme .split-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
    }
    [data-theme="light"] .split-card h3,
    body.light-theme .split-card h3 {
        color: #0f172a !important;
    }
    [data-theme="light"] .split-card p,
    body.light-theme .split-card p {
        color: #64748b !important;
    }
    [data-theme="light"] .split-card div[style*="border-top"],
    body.light-theme .split-card div[style*="border-top"] {
        border-top-color: #e2e8f0 !important;
    }
    [data-theme="light"] #kpiPlantaBruto,
    [data-theme="light"] #kpiAsesorBruto,
    body.light-theme #kpiPlantaBruto,
    body.light-theme #kpiAsesorBruto {
        color: #0f172a !important;
    }
    [data-theme="light"] .rh-box,
    body.light-theme .rh-box {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
    }
    [data-theme="light"] .rh-box-header [style*="color: #fff"],
    body.light-theme .rh-box-header [style*="color: #fff"] {
        color: #0f172a !important;
    }
    [data-theme="light"] .rh-table th,
    body.light-theme .rh-table th {
        background: #f8fafc !important;
        color: #475569 !important;
        border-bottom-color: #e2e8f0 !important;
    }
    [data-theme="light"] .rh-table td,
    body.light-theme .rh-table td {
        color: #0f172a !important;
        border-bottom-color: #f1f5f9 !important;
    }
    [data-theme="light"] .rh-table tbody tr:hover,
    body.light-theme .rh-table tbody tr:hover {
        background: #f8fafc !important;
    }
    [data-theme="light"] .group-header-row td,
    body.light-theme .group-header-row td {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border-top: 1px solid #cbd5e1 !important;
        border-bottom: 1px solid #cbd5e1 !important;
    }
    [data-theme="light"] .filter-pill,
    body.light-theme .filter-pill {
        background: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #475569 !important;
    }
    [data-theme="light"] .filter-pill.active,
    body.light-theme .filter-pill.active {
        background: #0284c7 !important;
        border-color: #0284c7 !important;
        color: #ffffff !important;
    }
    [data-theme="light"] .pill-counter,
    body.light-theme .pill-counter {
        background: rgba(0,0,0,0.08) !important;
        color: inherit !important;
    }
    [data-theme="light"] .kpi-card-rh,
    body.light-theme .kpi-card-rh {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03) !important;
    }
"""

content = content.replace('</style>', css_planilla_light + '\n</style>')

with open('templates/admin/planilla.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("PLANILLA HTML UPDATED")

