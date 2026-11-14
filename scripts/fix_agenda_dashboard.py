with open('templates/mecanico/citas_programadas.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Reemplazar empty state
old_empty = """    <div class="empty-state">
        <i class="fa-solid fa-mug-hot" style="font-size: 50px; color: rgba(255,255,255,0.2); margin-bottom: 20px;"></i>
        <h3 style="color: var(--text-muted);">Agenda Libre</h3>
        <p style="color: rgba(255,255,255,0.4);">No tienes citas asignadas para hoy. ¡Disfruta tu tiempo!</p>
    </div>"""

new_empty = """    <div class="empty-state agenda-empty-box">
        <div class="agenda-icon-wrap">
            <i class="fa-solid fa-mug-hot agenda-icon"></i>
        </div>
        <h3 class="agenda-title">Agenda Libre</h3>
        <p class="agenda-desc">No tienes citas o mantenimientos programados para hoy. ¡Disfruta tu tiempo o revisa el taller!</p>
    </div>"""

if old_empty in c:
    c = c.replace(old_empty, new_empty)
    print("AGENDA EMPTY REPLACED DIRECTLY")
else:
    # Intento con saltos de línea normalizados
    c_norm = c.replace('\r\n', '\n')
    old_norm = old_empty.replace('\r\n', '\n')
    new_norm = new_empty.replace('\r\n', '\n')
    if old_norm in c_norm:
        c_norm = c_norm.replace(old_norm, new_norm)
        c = c_norm
        print("AGENDA EMPTY REPLACED NORMALIZED")
    else:
        print("AGENDA EMPTY NOT FOUND")

# 2. Reemplazar badge del header
old_badge = '<span class="badge" style="background: rgba(242, 192, 41, 0.2); color: var(--primary); padding: 10px 15px; font-size: 0.9rem;">'
new_badge = '<span class="badge badge-mantenimientos" style="padding: 10px 15px; font-size: 0.9rem;">'
c = c.replace(old_badge, new_badge)

# 3. Añadir CSS
css_agenda = """
    .agenda-empty-box {
        grid-column: 1 / -1;
        text-align: center;
        padding: 60px 24px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 18px;
        border: 2px dashed rgba(255, 255, 255, 0.12);
    }
    .agenda-icon-wrap {
        width: 80px;
        height: 80px;
        margin: 0 auto 18px auto;
        border-radius: 50%;
        background: rgba(245, 158, 11, 0.12);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .agenda-icon {
        font-size: 2.4rem;
        color: #f59e0b;
    }
    .agenda-title {
        color: var(--text-primary, #ffffff);
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .agenda-desc {
        color: var(--text-secondary, #94a3b8);
        font-size: 0.95rem;
        max-width: 440px;
        margin: 0 auto;
        line-height: 1.5;
    }
    .badge-mantenimientos {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    [data-theme="light"] .dashboard-title,
    body.light-theme .dashboard-title {
        color: #0f172a !important;
    }
    [data-theme="light"] .agenda-empty-box,
    body.light-theme .agenda-empty-box {
        background: #f8fafc !important;
        border: 2px dashed #cbd5e1 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02) !important;
    }
    [data-theme="light"] .agenda-title,
    body.light-theme .agenda-title {
        color: #0f172a !important;
    }
    [data-theme="light"] .agenda-desc,
    body.light-theme .agenda-desc {
        color: #475569 !important;
    }
    [data-theme="light"] .badge-mantenimientos,
    body.light-theme .badge-mantenimientos {
        background: #fef3c7 !important;
        color: #b45309 !important;
        border: 1px solid #fde68a !important;
    }
"""

c = c.replace('</style>', css_agenda + '\n</style>')

with open('templates/mecanico/citas_programadas.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("CITAS PROGRAMADAS SAVED")

