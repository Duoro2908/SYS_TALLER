extra_css_rules = """
/* --- RECURSOS HUMANOS: Personal, Colaboradores y Cierres ([data-theme="light"]) --- */
[data-theme="light"] .kpi-card-emp {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .kpi-card-emp:hover {
  border-color: #cbd5e1 !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
}
[data-theme="light"] .kpi-val-emp {
  color: #0f172a !important;
}
[data-theme="light"] .kpi-label-emp {
  color: #64748b !important;
}
[data-theme="light"] .kpi-sub-emp {
  color: #94a3b8 !important;
}
[data-theme="light"] .atelier-box {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .toolbar-emp {
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .filter-pill-emp {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #475569 !important;
}
[data-theme="light"] .filter-pill-emp:hover {
  background: #e2e8f0 !important;
  color: #0f172a !important;
}
[data-theme="light"] .filter-pill-emp.active {
  background: #d97706 !important;
  color: #ffffff !important;
  border-color: #d97706 !important;
}
[data-theme="light"] .table-emp th {
  background: #f8fafc !important;
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .table-emp td {
  color: #0f172a !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
[data-theme="light"] .table-emp tbody tr:hover {
  background: #f8fafc !important;
}
[data-theme="light"] .avatar-badge-emp {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
}
[data-theme="light"] .badge-rol-tag {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #475569 !important;
}
[data-theme="light"] .btn-atelier-action {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
}
[data-theme="light"] .btn-atelier-action:hover {
  background: #e2e8f0 !important;
}
[data-theme="light"] .modal-atelier-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.12) !important;
}
[data-theme="light"] .input-atelier,
[data-theme="light"] .input-rh {
  background: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  color: #0f172a !important;
}
[data-theme="light"] .input-atelier:focus,
[data-theme="light"] .input-rh:focus {
  border-color: #2563eb !important;
  background: #ffffff !important;
}
[data-theme="light"] .current-cierre-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .kpi-cierre-box {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .kpi-cierre-box .value {
  color: #0f172a !important;
}
[data-theme="light"] .periodo-selector-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .periodo-selector-card select {
  background: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  color: #0f172a !important;
}
[data-theme="light"] .rh-side-box {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .rh-side-title {
  color: #0f172a !important;
}
[data-theme="light"] .side-row {
  border-bottom: 1px solid #f1f5f9 !important;
  color: #475569 !important;
}

/* --- PRODUCCION Y BODEGA: Compras e Historial ([data-theme="light"]) --- */
[data-theme="light"] .history-card {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  border-left: 4px solid #2563eb !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .history-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08) !important;
  border-color: #cbd5e1 !important;
  border-left-color: #2563eb !important;
}
[data-theme="light"] .history-card .prov {
  color: #0f172a !important;
}
[data-theme="light"] .history-card .date {
  color: #64748b !important;
}
[data-theme="light"] .order-table-container {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .order-table th {
  background: #f8fafc !important;
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .order-table td {
  color: #0f172a !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
[data-theme="light"] .btn-action {
  background: #f1f5f9 !important;
  color: #0f172a !important;
  border: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .btn-action:hover {
  background: #e2e8f0 !important;
}
[data-theme="light"] .grand-total-label {
  color: #0f172a !important;
}
[data-theme="light"] .sku-badge {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #475569 !important;
}
[data-theme="light"] .card-header {
  background: #ffffff !important;
}
[data-theme="light"] .card-details {
  background: #f8fafc !important;
  border-top: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .details-table th {
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .details-table td {
  color: #0f172a !important;
  border-bottom: 1px dashed #e2e8f0 !important;
}
"""

with open('static/css/styles.css', 'r', encoding='utf-8') as f:
    current_css = f.read()

# Append extra rules if not already present
if 'RECURSOS HUMANOS: Personal, Colaboradores' not in current_css:
    current_css += "\n" + extra_css_rules
    with open('static/css/styles.css', 'w', encoding='utf-8') as f:
        f.write(current_css)
    print("Appended extra light mode rules to styles.css successfully")
else:
    print("Rules already in styles.css")

