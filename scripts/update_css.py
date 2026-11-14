import os

css_content = """/* ==========================================================================
   TALLER Y LUBRICANTES CR - SISTEMA GLOBAL DE ESTILOS Y TEMAS
   Modo Oscuro (Predeterminado) & Modo Claro (Showroom Silver)
   ========================================================================== */

:root, [data-theme="light"] {
  /* Brand Colors */
  --accent-primary: #0f172a; /* Slate 900 */
  --accent-primary-hover: #334155;
  --accent-warning: #f59e0b;
  --accent-red: #ef4444;
  --accent-red-hover: #dc2626;
  --accent-green: #10b981;
  --accent-gold: #f59e0b;
  --accent-orange: #f97316;
  
  /* Light Theme Surfaces & Backgrounds */
  --bg-color: #f1f3f6; /* Pristine showroom floor */
  --bg-surface: #ffffff;
  --bg-sidebar: #ffffff;
  --bg-primary: #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-tertiary: #e2e8f0;
  --bg-panel: #ffffff;
  --bg-dark: #f8fafc;
  --bg-deep: #ffffff;
  --bg-void: #f8fafc;
  
  /* Text */
  --text-primary: #0f172a; /* Ultra legible slate */
  --text-secondary: #475569;
  --text-muted: #64748b;
  --text-main: #0f172a;
  
  /* Borders */
  --border-color: #e2e8f0;
  --border-glass: rgba(0, 0, 0, 0.08);
  --border-gold: rgba(217, 119, 6, 0.3);
  --card-border: #e2e8f0;
  --card-bg: #ffffff;
  
  /* Form & UI Elements */
  --input-bg: #ffffff;
  --surface-color: #ffffff;
  --img-container-bg: #ffffff;
  
  /* Accents */
  --apple-blue: #0284c7;
  --atelier-blue: #0284c7;
  --atelier-border: #e2e8f0;
  --atelier-card: #ffffff;
  --atelier-gold: #d97706;
  --atelier-text-muted: #64748b;
  
  /* Dashboard Status Colors */
  --dash-primary: #2563eb;
  --dash-success: #16a34a;
  --dash-warning: #d97706;
  --dash-danger: #dc2626;
  --dash-info: #0284c7;
  --dash-purple: #7c3aed;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.08);
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.04);
  --shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.08);
  
  --backdrop: blur(25px);
  --backdrop-blur: blur(20px);
}

[data-theme="dark"] {
  /* Brand Colors */
  --accent-primary: #f8fafc;
  --accent-primary-hover: #e2e8f0;
  --accent-warning: #f59e0b;
  --accent-red: #ef4444;
  --accent-red-hover: #dc2626;
  --accent-green: #10b981;
  --accent-gold: #f59e0b;
  --accent-orange: #f97316;
  
  /* Dark Theme Surfaces & Backgrounds */
  --bg-color: #08090a;
  --bg-surface: #121316;
  --bg-sidebar: #0e0f12;
  --bg-primary: #15161b;
  --bg-secondary: #1c1d22;
  --bg-tertiary: #25262c;
  --bg-panel: rgba(20, 20, 24, 0.85);
  --bg-dark: #121316;
  --bg-deep: #0a0b0d;
  --bg-void: #050506;
  
  /* Text */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-main: #f8fafc;
  
  /* Borders */
  --border-color: rgba(255, 255, 255, 0.08);
  --border-glass: rgba(255, 255, 255, 0.1);
  --border-gold: rgba(245, 158, 11, 0.3);
  --card-border: rgba(255, 255, 255, 0.08);
  --card-bg: #121316;
  
  /* Form & UI Elements */
  --input-bg: rgba(0, 0, 0, 0.4);
  --surface-color: #121316;
  --img-container-bg: #ffffff;
  
  /* Accents */
  --apple-blue: #38bdf8;
  --atelier-blue: #38bdf8;
  --atelier-border: rgba(255, 255, 255, 0.08);
  --atelier-card: rgba(20, 20, 24, 0.7);
  --atelier-gold: #fbbf24;
  --atelier-text-muted: #94a3b8;
  
  /* Dashboard Status Colors */
  --dash-primary: #60a5fa;
  --dash-success: #34d399;
  --dash-warning: #fbbf24;
  --dash-danger: #f87171;
  --dash-info: #38bdf8;
  --dash-purple: #c084fc;
  
  /* Shadows */
  --shadow-sm: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 10px 20px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.7);
  --shadow-card: 0 4px 15px rgba(0, 0, 0, 0.3);
  --shadow-hover: 0 12px 30px rgba(0, 0, 0, 0.5);
  
  --backdrop: blur(25px);
  --backdrop-blur: blur(20px);
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-primary);
  display: flex;
  height: 100vh;
  overflow: hidden;
  transition: background-color 0.25s ease, color 0.25s ease;
}

/* Sidebar Ultra Premium */
.sidebar {
  width: 270px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  box-sizing: border-box;
  z-index: 100;
  transition: background-color 0.25s ease, border-color 0.25s ease;
  overflow-y: auto;
  overflow-x: hidden;
}

[data-theme="light"] .sidebar {
  background: #ffffff !important;
  border-right: 1px solid #e2e8f0 !important;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
}

.sidebar::-webkit-scrollbar {
  width: 5px;
}
.sidebar::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar::-webkit-scrollbar-thumb {
  background: rgba(150, 150, 150, 0.3);
  border-radius: 10px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--accent-red);
  box-shadow: 0 0 8px var(--accent-red);
}

.nav-links {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}

.nav-links li {
  margin-bottom: 6px;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.nav-links a:hover, .nav-links a.active {
  background: rgba(15, 23, 42, 0.05);
  color: var(--text-primary);
}

[data-theme="dark"] .nav-links a:hover, [data-theme="dark"] .nav-links a.active {
  background: rgba(248, 250, 252, 0.05);
}

[data-theme="light"] .nav-links a:hover, [data-theme="light"] .nav-links a.active {
  background: #f1f5f9 !important;
  color: #0f172a !important;
}

.nav-links a i {
  color: var(--text-secondary);
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
  transition: color 0.2s ease;
}

.nav-links a:hover i, .nav-links a.active i {
  color: var(--accent-primary);
}

/* Collapsible Submenus */
.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  border-radius: 8px;
  margin-bottom: 2px;
}

.module-header:hover {
  background: rgba(15, 23, 42, 0.05);
  color: var(--text-primary);
}

[data-theme="dark"] .module-header:hover {
  background: rgba(248, 250, 252, 0.05);
}

[data-theme="light"] .module-header:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.module-header .module-title {
  display: flex;
  align-items: center;
  gap: 14px;
}
.module-header .module-title i {
  width: 20px;
  text-align: center;
  font-size: 1.1rem;
}
.module-header i.fa-chevron-down {
  font-size: 0.7rem;
  transition: transform 0.3s;
}
.module-header.active {
  color: var(--text-primary);
}
.module-header.active .module-title i {
  color: var(--accent-primary);
}
.module-header.active i.fa-chevron-down {
  transform: rotate(180deg);
}

.submodule-list {
  display: none;
  padding-left: 34px !important;
  margin-bottom: 10px;
}

.settings-btn {
  margin-top: auto;
}

.settings-btn a {
  color: var(--text-secondary);
}

/* Main Content Area */
.main-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  position: relative;
  transition: background-color 0.25s ease;
}

/* Topbar */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  gap: 20px;
  flex-wrap: wrap;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 14px;
}

/* BOTON DE CAMBIO DE MODO OSCURO / CLARO (LUNITA) */
.theme-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
}

.theme-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent-gold);
}

.theme-toggle-btn:active {
  transform: translateY(0);
}

.theme-toggle-btn i {
  font-size: 1.15rem;
  transition: transform 0.4s ease, color 0.3s ease;
}

.theme-toggle-btn:hover i {
  transform: rotate(20deg) scale(1.15);
}

[data-theme="light"] .theme-toggle-btn {
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  color: #0f172a !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}

[data-theme="light"] .theme-toggle-btn:hover {
  border-color: #f59e0b !important;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.15) !important;
}

/* Flat Cards */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(245, 158, 11, 0.3);
}

/* Buttons Ultra Premium Neutral */
.btn-primary {
  background: var(--accent-primary);
  color: var(--bg-surface);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255,255,255,0.1);
}

.btn-primary:hover {
  background: var(--accent-primary-hover);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(1px);
}

/* Native Select */
select.form-control option {
  background-color: var(--bg-surface);
  color: var(--text-primary);
  font-weight: normal;
  padding: 10px;
}

/* Select2 Custom Styling */
.select2-container--default .select2-selection--single {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  height: 42px !important;
  display: flex !important;
  align-items: center !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.2s ease !important;
}

.select2-container--default.select2-container--open .select2-selection--single {
  border-color: var(--accent-primary) !important;
  box-shadow: 0 0 0 3px rgba(100, 100, 100, 0.15) !important;
}

.select2-container--default .select2-selection--single .select2-selection__rendered {
  color: var(--text-primary) !important;
  line-height: normal !important;
  padding-left: 12px !important;
  font-size: 0.95rem !important;
}

.select2-container--default .select2-selection--single .select2-selection__arrow {
  height: 40px !important;
  right: 10px !important;
}

.select2-dropdown {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  box-shadow: var(--shadow-lg) !important;
  overflow: hidden;
}

.select2-search--dropdown .select2-search__field {
  background-color: rgba(0,0,0,0.05) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  color: var(--text-primary) !important;
  padding: 8px 12px !important;
}
[data-theme="dark"] .select2-search--dropdown .select2-search__field {
  background-color: rgba(255,255,255,0.05) !important;
}

.select2-container--default .select2-results__option {
  color: var(--text-primary) !important;
  padding: 10px 15px !important;
  transition: background 0.2s;
}

.select2-container--default .select2-results__option--highlighted[aria-selected],
.select2-container--default .select2-results__option--highlighted.select2-results__option--selectable {
  background-color: rgba(100, 100, 100, 0.1) !important;
  color: var(--text-primary) !important;
}

.select2-container--default .select2-results__option[aria-selected=true] {
  background-color: rgba(150, 150, 150, 0.1) !important;
}

/* ==========================================================================
   REGLAS ESPECIFICAS PARA MODO CLARO ([data-theme="light"])
   ========================================================================== */

/* 1. RECURSOS HUMANOS (Planilla, Contratos, Registro Mensual, Personal) */
[data-theme="light"] .kpi-card-rh {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .kpi-card-rh:hover {
  border-color: #cbd5e1 !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
}
[data-theme="light"] .kpi-val {
  color: #0f172a !important;
}
[data-theme="light"] .kpi-label {
  color: #64748b !important;
}
[data-theme="light"] .rh-box {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .rh-box-title {
  color: #0f172a !important;
}
[data-theme="light"] .rh-table th {
  background: #f8fafc !important;
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .rh-table td {
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
[data-theme="light"] .rh-table tbody tr:hover {
  background: #f8fafc !important;
}
[data-theme="light"] .rh-table tfoot td {
  background: #f1f5f9 !important;
  color: #0f172a !important;
  border-top: 2px solid #cbd5e1 !important;
}
[data-theme="light"] .rh-tabs {
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .rh-tab-btn {
  color: #64748b !important;
}
[data-theme="light"] .rh-tab-btn:hover {
  color: #0f172a !important;
  background: #f1f5f9 !important;
}
[data-theme="light"] .rh-tab-btn.active {
  color: #0284c7 !important;
  background: #e0f2fe !important;
  border: 1px solid #bae6fd !important;
}
[data-theme="light"] .rh-badge-legal {
  background: #e0f2fe !important;
  border-color: #bae6fd !important;
  color: #0284c7 !important;
}
[data-theme="light"] .rh-badge-dgi {
  background: #dcfce7 !important;
  border-color: #bbf7d0 !important;
  color: #15803d !important;
}
[data-theme="light"] .badge-tramo-dgi {
  background: #fef3c7 !important;
  border-color: #fde68a !important;
  color: #b45309 !important;
}
[data-theme="light"] .badge-tramo-exento {
  background: #f1f5f9 !important;
  border-color: #e2e8f0 !important;
  color: #64748b !important;
}
[data-theme="light"] .val-deduction {
  color: #dc2626 !important;
}
[data-theme="light"] .val-neto {
  color: #16a34a !important;
}
[data-theme="light"] .rh-modal-content,
[data-theme="light"] .modal-content {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12) !important;
}
[data-theme="light"] .rh-form-group input,
[data-theme="light"] .rh-form-group select,
[data-theme="light"] .form-control {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}
[data-theme="light"] .rh-form-group input:focus,
[data-theme="light"] .rh-form-group select:focus,
[data-theme="light"] .form-control:focus {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}
[data-theme="light"] .rh-form-group label,
[data-theme="light"] .form-group label {
  color: #475569 !important;
}

/* 2. PRODUCCION Y BODEGA (Inventario, Compras, Historial) */
[data-theme="light"] .inventory-toolbar,
[data-theme="light"] .history-toolbar {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .filters input,
[data-theme="light"] .filters select,
[data-theme="light"] .search-box {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .filters input::placeholder,
[data-theme="light"] .search-box::placeholder {
  color: #94a3b8 !important;
}
[data-theme="light"] .product-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
}
[data-theme="light"] .product-card:hover {
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.1) !important;
  border-color: #cbd5e1 !important;
}
[data-theme="light"] .product-img-container {
  background: #f8fafc !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .product-sku {
  color: #64748b !important;
}
[data-theme="light"] .product-title {
  color: #0f172a !important;
}
[data-theme="light"] .product-price {
  color: #0f172a !important;
}
[data-theme="light"] .product-stock-text {
  color: #475569 !important;
}
[data-theme="light"] .glass-panel {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .section-header {
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .section-header h3 {
  color: #0f172a !important;
}
[data-theme="light"] .purchase-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .purchase-card:hover {
  border-color: #cbd5e1 !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
}
[data-theme="light"] .card-header h4,
[data-theme="light"] .card-header span {
  color: #0f172a !important;
}
[data-theme="light"] .purchase-table th,
[data-theme="light"] .history-table th {
  background: #f8fafc !important;
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .purchase-table td,
[data-theme="light"] .history-table td {
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
[data-theme="light"] .summary-card,
[data-theme="light"] .summary-box {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
}

/* 3. ATENCION AL CLIENTE & WHATSAPP */
[data-theme="light"] .clients-table-container,
[data-theme="light"] .citas-table-container,
[data-theme="light"] .gestion-citas-wrapper {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .cita-card,
[data-theme="light"] .ticket-card,
[data-theme="light"] .wa-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .chat-box,
[data-theme="light"] .msg-box {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
}
[data-theme="light"] #configWaModal > div {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.15) !important;
}
[data-theme="light"] #configWaModal input,
[data-theme="light"] #configWaModal textarea {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}

/* 4. TALLER Y MECANICA */
[data-theme="light"] .citas-grid .cita-card,
[data-theme="light"] .mantenimiento-card,
[data-theme="light"] .orden-card,
[data-theme="light"] .taller-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
  color: #0f172a !important;
}
[data-theme="light"] .cita-title,
[data-theme="light"] .orden-title,
[data-theme="light"] .mantenimiento-title {
  color: #0f172a !important;
}
[data-theme="light"] .cita-body,
[data-theme="light"] .orden-body {
  color: #475569 !important;
}

/* 5. CAJA Y FACTURACION */
[data-theme="light"] .pos-card,
[data-theme="light"] .ventas-container,
[data-theme="light"] .cierre-caja-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
  color: #0f172a !important;
}
[data-theme="light"] .pos-table th {
  background: #f8fafc !important;
  color: #475569 !important;
  border-bottom: 1px solid #e2e8f0 !important;
}
[data-theme="light"] .pos-table td {
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

/* 6. CONTABILIDAD Y FINANZAS */
[data-theme="light"] .period-control-bar,
[data-theme="light"] .report-sheet {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .period-select-custom {
  background: #f8fafc !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
}
[data-theme="light"] .category-header {
  background: #eff6ff !important;
  color: #1e40af !important;
}
[data-theme="light"] .account-row {
  color: #1e293b !important;
}
[data-theme="light"] .account-row:hover {
  background: #f8fafc !important;
}
[data-theme="light"] .report-sheet-header h2 {
  color: #0f172a !important;
}

/* 7. DASHBOARD & SUPERADMIN */
[data-theme="light"] .kpi-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .kpi-details h3 {
  color: #0f172a !important;
}
[data-theme="light"] .kpi-details p {
  color: #64748b !important;
}
[data-theme="light"] .admin-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
[data-theme="light"] .admin-card h3 {
  color: #0f172a !important;
}
[data-theme="light"] .action-btn {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
}
[data-theme="light"] .action-btn:hover {
  background: #f1f5f9 !important;
  border-color: #cbd5e1 !important;
}
[data-theme="light"] .btn-manual-sync {
  background: #f1f5f9 !important;
  border: 1px solid #cbd5e1 !important;
  color: #0f172a !important;
}
[data-theme="light"] .btn-manual-sync:hover {
  background: #e2e8f0 !important;
  color: #0f172a !important;
}

/* 8. BOTON CANCELAR / SECUNDARIO GLOBAL */
[data-theme="light"] .btn-cancelar {
  background: #f1f5f9 !important;
  color: #475569 !important;
  border: 1px solid #cbd5e1 !important;
}
[data-theme="light"] .btn-cancelar:hover {
  background: #e2e8f0 !important;
  color: #0f172a !important;
}

/* Flash Messages en Modo Claro */
[data-theme="light"] .flash-banner.flash-success {
  background: #f0fdf4 !important;
  border: 1px solid #bbf7d0 !important;
  border-left: 5px solid #22c55e !important;
  color: #15803d !important;
}
[data-theme="light"] .flash-banner.flash-success div {
  color: #15803d !important;
}
[data-theme="light"] .flash-banner.flash-error {
  background: #fef2f2 !important;
  border: 1px solid #fecaca !important;
  border-left: 5px solid #ef4444 !important;
  color: #991b1b !important;
}
[data-theme="light"] .flash-banner.flash-error div {
  color: #991b1b !important;
}
[data-theme="light"] .flash-banner.flash-warning {
  background: #fffbeb !important;
  border: 1px solid #fde68a !important;
  border-left: 5px solid #f59e0b !important;
  color: #92400e !important;
}
[data-theme="light"] .flash-banner.flash-warning div {
  color: #92400e !important;
}
"""

with open('static/css/styles.css', 'w', encoding='utf-8') as f:
    f.write(css_content.strip())

print("styles.css successfully updated with comprehensive light/dark mode support")

