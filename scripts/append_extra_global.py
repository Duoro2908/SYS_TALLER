with open('static/css/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

extra_global = """
/* Botón Conectar mi WhatsApp en Citas */
[data-theme="light"] .btn-conectar-wa,
body.light-theme .btn-conectar-wa {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
}

/* Agenda de Hoy Vacía (Mecánico / Dashboard) */
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

/* Buscador de Colaboradores en Planilla */
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

with open('static/css/styles.css', 'a', encoding='utf-8') as f:
    f.write(extra_global)

print("GLOBAL STYLES UPDATED WITH 3 FIXES")

