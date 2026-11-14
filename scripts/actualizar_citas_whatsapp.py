with open('templates/atencion/citas_whatsapp.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Corregir título principal h1
content = content.replace(
    '<h1 style="font-size: 1.8rem; font-weight: 700; color: #fff; margin: 0 0 5px 0;">',
    '<h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: 0 0 5px 0;">'
)

# 2. Corregir título de conversaciones en vivo
content = content.replace(
    '<span style="font-weight: 700; font-size: 1rem; color: #fff; display: flex; align-items: center; gap: 8px;">',
    '<span style="font-weight: 700; font-size: 1rem; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">'
)

# 3. Corregir título en el empty placeholder de citas
content = content.replace(
    '<p style="font-size: 1.05rem; margin-bottom: 6px; color: #fff;">Esperando citas por WhatsApp</p>',
    '<p style="font-size: 1.05rem; margin-bottom: 6px; color: var(--text-primary); font-weight: 700;">Esperando citas por WhatsApp</p>'
)

# 4. Añadir bloque de estilos para [data-theme="light"] y body.light-theme
css_light_rules = """
    /* Adaptación Especial para Modo Claro ([data-theme="light"]) */
    [data-theme="light"] .bot-switch-box,
    body.light-theme .bot-switch-box {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    [data-theme="light"] .switch-title,
    body.light-theme .switch-title {
        color: #64748b !important;
    }
    [data-theme="light"] .banner-off,
    body.light-theme .banner-off {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #991b1b !important;
    }
    [data-theme="light"] .banner-on,
    body.light-theme .banner-on {
        background: #ecfdf5 !important;
        border: 1px solid #a7f3d0 !important;
        color: #065f46 !important;
    }
    [data-theme="light"] .kpi-card,
    body.light-theme .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03) !important;
    }
    [data-theme="light"] .kpi-title,
    body.light-theme .kpi-title {
        color: #475569 !important;
    }
    [data-theme="light"] .kpi-value,
    body.light-theme .kpi-value {
        color: #0f172a !important;
    }
    [data-theme="light"] .panel-box,
    body.light-theme .panel-box {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
    }
    [data-theme="light"] .panel-header,
    body.light-theme .panel-header {
        border-bottom-color: #e2e8f0 !important;
    }
    [data-theme="light"] .panel-title,
    body.light-theme .panel-title {
        color: #0f172a !important;
    }
    [data-theme="light"] .tab-btn,
    body.light-theme .tab-btn {
        background: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        color: #475569 !important;
    }
    [data-theme="light"] .tab-btn.active,
    body.light-theme .tab-btn.active {
        background: #0284c7 !important;
        border-color: #0284c7 !important;
        color: #ffffff !important;
    }
    [data-theme="light"] #citas-empty-placeholder,
    body.light-theme #citas-empty-placeholder {
        background: #f8fafc !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 14px !important;
        color: #475569 !important;
    }
    [data-theme="light"] #citas-empty-placeholder p,
    body.light-theme #citas-empty-placeholder p {
        color: #475569 !important;
    }
    [data-theme="light"] #citas-empty-placeholder p strong,
    body.light-theme #citas-empty-placeholder p strong {
        color: #0f172a !important;
    }
    [data-theme="light"] .cita-card,
    body.light-theme .cita-card {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-theme="light"] .cita-id-tag,
    body.light-theme .cita-id-tag {
        color: #0f172a !important;
    }
    [data-theme="light"] .cita-body-grid,
    body.light-theme .cita-body-grid {
        color: #475569 !important;
    }
    [data-theme="light"] .cita-body-grid strong,
    body.light-theme .cita-body-grid strong {
        color: #0f172a !important;
    }
    [data-theme="light"] .wa-chat-container,
    body.light-theme .wa-chat-container {
        border-color: #e2e8f0 !important;
    }
    [data-theme="light"] .wa-chat-header,
    body.light-theme .wa-chat-header {
        background: #f8fafc !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    [data-theme="light"] #chatHeaderTitle,
    body.light-theme #chatHeaderTitle {
        color: #0f172a !important;
    }
    [data-theme="light"] .wa-chat-body,
    body.light-theme .wa-chat-body {
        background: #ffffff !important;
    }
    [data-theme="light"] #chatPlaceholder,
    body.light-theme #chatPlaceholder {
        color: #475569 !important;
    }
    [data-theme="light"] #chatPlaceholder strong,
    body.light-theme #chatPlaceholder strong {
        color: #0f172a !important;
    }
    [data-theme="light"] .wa-chat-footer,
    body.light-theme .wa-chat-footer {
        background: #f8fafc !important;
        border-top: 1px solid #e2e8f0 !important;
    }
    [data-theme="light"] .wa-input,
    body.light-theme .wa-input {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
    }
    [data-theme="light"] .btn-chat-chip,
    body.light-theme .btn-chat-chip {
        background: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
"""

content = content.replace('</style>', css_light_rules + '\n</style>')

with open('templates/atencion/citas_whatsapp.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("CITAS WHATSAPP UPDATED")

