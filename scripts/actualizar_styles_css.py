with open('static/css/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

append_rules = """

/* ==========================================================================
   REGLAS GLOBALES DE ALTO CONTRASTE PARA MODO CLARO ([data-theme="light"])
   ========================================================================== */

/* 1. Bandeja de Sugerencias y Quejas */
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

/* 2. Módulo de Citas WhatsApp */
[data-theme="light"] .wa-header h1,
body.light-theme .wa-header h1 {
  color: #0f172a !important;
}
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

/* 3. Planilla de Pago y Recursos Humanos */
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
[data-theme="light"] #kpiPlantaBruto,
[data-theme="light"] #kpiAsesorBruto,
body.light-theme #kpiPlantaBruto,
body.light-theme #kpiAsesorBruto {
  color: #0f172a !important;
}
[data-theme="light"] .group-header-row td,
body.light-theme .group-header-row td {
  background: #f1f5f9 !important;
  color: #0f172a !important;
  border-top: 1px solid #cbd5e1 !important;
  border-bottom: 1px solid #cbd5e1 !important;
}

/* 4. Registro Mensual y Cierres de Nómina */
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
[data-theme="light"] .history-card h3,
body.light-theme .history-card h3 {
  color: #0f172a !important;
}
[data-theme="light"] .current-cierre-card,
body.light-theme .current-cierre-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
}
"""

with open('static/css/styles.css', 'a', encoding='utf-8') as f:
    f.write(append_rules)

print("GLOBAL STYLES.CSS UPDATED")

