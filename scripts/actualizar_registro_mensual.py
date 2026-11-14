with open('templates/admin/registro_mensual.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Corregir título h3 en history-card
content = content.replace(
    '<h3 style="margin: 0; color: #fff; font-size: 1.15rem; font-weight: 700;">',
    '<h3 style="margin: 0; color: var(--text-primary); font-size: 1.15rem; font-weight: 700;">'
)

# 2. Reemplazar empty state
old_empty = """        <div style="text-align: center; padding: 45px 20px; background: rgba(0, 0, 0, 0.2); border-radius: 14px; border: 1px dashed var(--atelier-border);">
            <i class="fa-solid fa-calendar-xmark" style="font-size: 2.5rem; color: var(--atelier-gold); margin-bottom: 12px; opacity: 0.6;"></i>
            <h4 style="margin: 0 0 6px 0; color: #fff; font-size: 1.1rem;">Aún no se han ejecutado cierres mensuales</h4>
            <p style="margin: 0 0 16px 0; color: var(--atelier-text-muted); font-size: 0.85rem; max-width: 450px; margin-inline: auto;">
                Presione el botón <strong>"Realizar Cierre de Mes (Manual)"</strong> en la parte superior para emitir y registrar el acta oficial de nómina de este período.
            </p>
        </div>"""

new_empty = """        <div class="cierre-empty-card">
            <i class="fa-solid fa-calendar-xmark cierre-empty-icon"></i>
            <h4 class="cierre-empty-title">Aún no se han ejecutado cierres mensuales</h4>
            <p class="cierre-empty-desc">
                Presione el botón <strong>"Realizar Cierre de Mes (Manual)"</strong> en la parte superior para emitir y registrar el acta oficial de nómina de este período.
            </p>
        </div>"""

if old_empty in content:
    content = content.replace(old_empty, new_empty)
    print("EMPTY STATE REPLACED DIRECTLY")
else:
    import re
    m = re.search(r'<div style="text-align: center; padding: 45px 20px; background: rgba\(0, 0, 0, 0\.2\);.*?</div>', content, re.DOTALL)
    if m:
        content = content[:m.start()] + new_empty + content[m.end():]
        print("EMPTY STATE REPLACED VIA REGEX")
    else:
        print("EMPTY STATE NOT FOUND")

# 3. Añadir estilos CSS
css_cierre_light = """
    .cierre-empty-card {
        text-align: center;
        padding: 50px 20px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 14px;
        border: 2px dashed rgba(255, 255, 255, 0.12);
    }
    .cierre-empty-icon {
        font-size: 2.6rem;
        color: #f59e0b;
        margin-bottom: 14px;
        opacity: 0.85;
        display: block;
    }
    .cierre-empty-title {
        margin: 0 0 6px 0;
        color: var(--text-primary, #ffffff);
        font-size: 1.15rem;
        font-weight: 700;
    }
    .cierre-empty-desc {
        margin: 0 auto;
        color: var(--text-secondary, #94a3b8);
        font-size: 0.88rem;
        max-width: 460px;
        line-height: 1.5;
    }

    [data-theme="light"] .cierre-empty-card,
    body.light-theme .cierre-empty-card {
        background: #f8fafc !important;
        border: 2px dashed #cbd5e1 !important;
    }
    [data-theme="light"] .cierre-empty-title,
    body.light-theme .cierre-empty-title {
        color: #0f172a !important;
    }
    [data-theme="light"] .cierre-empty-desc,
    body.light-theme .cierre-empty-desc {
        color: #475569 !important;
    }
    [data-theme="light"] .cierre-empty-desc strong,
    body.light-theme .cierre-empty-desc strong {
        color: #0f172a !important;
    }

    [data-theme="light"] .current-cierre-card,
    body.light-theme .current-cierre-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
    }
    [data-theme="light"] .history-card,
    body.light-theme .history-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
    }
    [data-theme="light"] .history-card h3,
    body.light-theme .history-card h3 {
        color: #0f172a !important;
    }
    [data-theme="light"] .kpi-cierre-box,
    body.light-theme .kpi-cierre-box {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-theme="light"] .kpi-cierre-box .label,
    body.light-theme .kpi-cierre-box .label {
        color: #475569 !important;
    }
    [data-theme="light"] .kpi-cierre-box .value,
    body.light-theme .kpi-cierre-box .value {
        color: #0f172a !important;
    }
    [data-theme="light"] .kpi-cierre-box .subtext,
    body.light-theme .kpi-cierre-box .subtext {
        color: #64748b !important;
    }
    [data-theme="light"] .periodo-picker-box select,
    body.light-theme .periodo-picker-box select {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
"""

content = content.replace('</style>', css_cierre_light + '\n</style>')

with open('templates/admin/registro_mensual.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("REGISTRO MENSUAL SAVED")

