with open('templates/atencion/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar selectores de modo claro para admitir [data-theme="light"] y body.light-theme
content = content.replace('body.light-theme .glass-panel', '[data-theme="light"] .glass-panel, body.light-theme .glass-panel')
content = content.replace('body.light-theme .section-header', '[data-theme="light"] .section-header, body.light-theme .section-header')
content = content.replace('body.light-theme .section-header h3', '[data-theme="light"] .section-header h3, body.light-theme .section-header h3')
content = content.replace('body.light-theme .ticket-counter-badge', '[data-theme="light"] .ticket-counter-badge, body.light-theme .ticket-counter-badge')
content = content.replace('body.light-theme .ticket-card', '[data-theme="light"] .ticket-card, body.light-theme .ticket-card')
content = content.replace('body.light-theme .ticket-client', '[data-theme="light"] .ticket-client, body.light-theme .ticket-client')
content = content.replace('body.light-theme .ticket-contact', '[data-theme="light"] .ticket-contact, body.light-theme .ticket-contact')
content = content.replace('body.light-theme .ticket-subject', '[data-theme="light"] .ticket-subject, body.light-theme .ticket-subject')
content = content.replace('body.light-theme .ticket-subject strong', '[data-theme="light"] .ticket-subject strong, body.light-theme .ticket-subject strong')
content = content.replace('body.light-theme .ticket-date', '[data-theme="light"] .ticket-date, body.light-theme .ticket-date')
content = content.replace('body.light-theme .modal-content', '[data-theme="light"] .modal-content, body.light-theme .modal-content')
content = content.replace('body.light-theme .modal-header', '[data-theme="light"] .modal-header, body.light-theme .modal-header')
content = content.replace('body.light-theme .modal-header h3', '[data-theme="light"] .modal-header h3, body.light-theme .modal-header h3')
content = content.replace('body.light-theme .msg-box', '[data-theme="light"] .msg-box, body.light-theme .msg-box')

# Reemplazar el contenedor de bandeja vacía
old_empty = """        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: var(--bg-card, rgba(0,0,0,0.2)); border-radius: 16px; border: 1px dashed var(--border-color, rgba(255,255,255,0.1));">
            <i class="fa-solid fa-envelope-open-text" style="font-size: 3.5rem; color: #3b82f6; opacity: 0.7; margin-bottom: 16px; display: block;"></i>
            <h3 style="color: var(--text-primary, #ffffff); margin-bottom: 8px; font-size: 1.3rem;">Bandeja Vacía</h3>
            <p style="color: var(--text-secondary, #94a3b8); margin: 0; font-size: 0.95rem;">No hay quejas ni sugerencias registradas actualmente en el buzón.</p>
        </div>"""

new_empty = """        <div class="empty-mailbox-card">
            <i class="fa-solid fa-envelope-open-text empty-mailbox-icon"></i>
            <h3 class="empty-mailbox-title">Bandeja Vacía</h3>
            <p class="empty-mailbox-desc">No hay quejas ni sugerencias registradas actualmente en el buzón de Taller CR.</p>
        </div>"""

if old_empty in content:
    content = content.replace(old_empty, new_empty)
    print("EMPTY STATE REPLACED DIRECTLY")
else:
    # Buscar con regex flexible
    import re
    pattern = r'<div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: [^>]+>.*?</div>\s*</div>'
    match = re.search(r'<div style="grid-column: 1 / -1;.*?</div>\s*\{% endfor %\}', content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_empty + "\n        {% endfor %}" + content[match.end():]
        print("EMPTY STATE REPLACED VIA REGEX")
    else:
        print("EMPTY STATE NOT FOUND")

# Añadir CSS para empty-mailbox-card
css_extra = """
    .empty-mailbox-card {
        grid-column: 1 / -1;
        text-align: center;
        padding: 60px 24px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        border: 2px dashed rgba(255, 255, 255, 0.12);
        transition: all 0.25s ease;
    }
    .empty-mailbox-icon {
        font-size: 3.5rem;
        color: #3b82f6;
        opacity: 0.85;
        margin-bottom: 16px;
        display: block;
    }
    .empty-mailbox-title {
        color: var(--text-primary, #ffffff);
        margin: 0 0 8px 0;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .empty-mailbox-desc {
        color: var(--text-secondary, #94a3b8);
        margin: 0 auto;
        font-size: 0.95rem;
        max-width: 460px;
        line-height: 1.5;
    }

    [data-theme="light"] .empty-mailbox-card,
    body.light-theme .empty-mailbox-card {
        background: #f8fafc !important;
        border: 2px dashed #cbd5e1 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02) !important;
    }
    [data-theme="light"] .empty-mailbox-title,
    body.light-theme .empty-mailbox-title {
        color: #0f172a !important;
    }
    [data-theme="light"] .empty-mailbox-desc,
    body.light-theme .empty-mailbox-desc {
        color: #475569 !important;
    }
"""

content = content.replace('</style>', css_extra + '\n</style>')

with open('templates/atencion/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("ATENCION INDEX SAVED")

