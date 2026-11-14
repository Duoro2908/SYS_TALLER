with open('templates/atencion/citas_whatsapp.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_btn = '<button onclick="abrirConfigModal()" class="btn-sm-action" style="background: rgba(255,255,255,0.08); color: #fff; border: 1px solid rgba(255,255,255,0.15); padding: 9px 16px;">'
new_btn = '<button onclick="abrirConfigModal()" class="btn-sm-action btn-conectar-wa">'

if old_btn in c:
    c = c.replace(old_btn, new_btn)
    print("CONECTAR BTN CLASS REPLACED")
else:
    print("CONECTAR BTN NOT FOUND DIRECTLY")

css_btn = """
    .btn-conectar-wa {
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 9px 16px;
        transition: all 0.2s ease;
    }
    .btn-conectar-wa:hover {
        background: rgba(255, 255, 255, 0.16);
        color: #ffffff;
    }
    [data-theme="light"] .btn-conectar-wa,
    body.light-theme .btn-conectar-wa {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    }
    [data-theme="light"] .btn-conectar-wa:hover,
    body.light-theme .btn-conectar-wa:hover {
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
"""

c = c.replace('</style>', css_btn + '\n</style>')

with open('templates/atencion/citas_whatsapp.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("CITAS WHATSAPP SAVED")

