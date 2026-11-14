with open('templates/admin/planilla.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_input = '<input type="text" id="buscadorPlanilla" onkeyup="filtrarTablaPlanilla()" placeholder="Buscar empleado o cargo..." style="padding: 7px 14px; border-radius: 20px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.15); color: #fff; font-size: 0.85rem; width: 200px;">'
new_input = '<input type="text" id="buscadorPlanilla" class="input-buscador-planilla" onkeyup="filtrarTablaPlanilla()" placeholder="Buscar empleado o cargo...">'

if old_input in c:
    c = c.replace(old_input, new_input)
    print("BUSCADOR INPUT REPLACED DIRECTLY")
else:
    print("BUSCADOR INPUT NOT FOUND DIRECTLY")

css_buscador = """
    .input-buscador-planilla {
        padding: 8px 16px;
        border-radius: 20px;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
        font-size: 0.85rem;
        width: 220px;
        outline: none;
        transition: all 0.2s ease;
    }
    .input-buscador-planilla:focus {
        border-color: #0A84FF;
        box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.15);
    }
    [data-theme="light"] .input-buscador-planilla,
    body.light-theme .input-buscador-planilla {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    [data-theme="light"] .input-buscador-planilla::placeholder,
    body.light-theme .input-buscador-planilla::placeholder {
        color: #64748b !important;
    }
    [data-theme="light"] .input-buscador-planilla:focus,
    body.light-theme .input-buscador-planilla:focus {
        background: #ffffff !important;
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
    }
"""

c = c.replace('</style>', css_buscador + '\n</style>')

with open('templates/admin/planilla.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("PLANILLA HTML SAVED")

