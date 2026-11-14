with open('templates/admin/empleados_rrhh.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <style> block
idx_start = content.find("<style>")
idx_end = content.find("</style>")

new_style = """<style>
    .rrhh-emp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        flex-wrap: wrap;
        gap: 15px;
    }

    .kpi-row-emp {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 25px;
    }

    .kpi-card-emp {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 18px 20px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    .kpi-card-emp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--atelier-gold, #d97706);
        opacity: 0.9;
    }

    .kpi-card-emp:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-color);
    }

    .kpi-label-emp {
        font-size: 0.74rem;
        text-transform: uppercase;
        color: var(--text-secondary);
        letter-spacing: 0.6px;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .kpi-val-emp {
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .kpi-sub-emp {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    .atelier-box {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 30px;
        box-shadow: var(--shadow-sm);
    }

    .toolbar-emp {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-color);
    }

    .filter-pills-emp {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }

    .filter-pill-emp {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
    }

    .filter-pill-emp:hover {
        background: var(--border-color);
        color: var(--text-primary);
    }

    .filter-pill-emp.active {
        background: #d97706;
        color: #ffffff;
        border-color: #d97706;
        font-weight: 700;
    }

    .table-emp {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.87rem;
    }

    .table-emp th {
        background: var(--bg-secondary);
        padding: 12px 14px;
        text-align: left;
        font-size: 0.74rem;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        border-bottom: 1px solid var(--border-color);
    }

    .table-emp td {
        padding: 13px 14px;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
        vertical-align: middle;
    }

    .table-emp tbody tr:hover {
        background: var(--bg-primary);
    }

    .avatar-badge-emp {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.95rem;
        color: var(--text-primary);
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        flex-shrink: 0;
    }

    .badge-status-activo {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-status-inactivo {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-rol-tag {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        background: var(--bg-secondary);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
    }

    .btn-atelier-action {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        text-decoration: none;
    }

    .btn-atelier-action:hover {
        background: var(--border-color);
        color: var(--text-primary);
        transform: translateY(-1px);
    }

    .btn-atelier-primary {
        background: #d97706;
        color: #ffffff !important;
        border: 1px solid #d97706;
        font-weight: 700;
    }

    .btn-atelier-primary:hover {
        background: #b45309;
        color: #ffffff !important;
        border-color: #b45309;
    }

    .btn-atelier-danger {
        border-color: rgba(239, 68, 68, 0.3);
        color: #ef4444;
        background: rgba(239, 68, 68, 0.08);
    }

    .btn-atelier-danger:hover {
        background: #ef4444;
        border-color: #ef4444;
        color: #fff;
    }

    /* Modal Estilo Atelier */
    .modal-atelier {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 99999;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-sizing: border-box;
    }

    .modal-atelier.active {
        display: flex;
    }

    .modal-atelier-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        width: 100%;
        max-width: 820px;
        max-height: 92vh;
        overflow-y: auto;
        padding: 28px;
        box-shadow: var(--shadow-lg);
        box-sizing: border-box;
        color: var(--text-primary);
    }

    .form-group-atelier {
        margin-bottom: 16px;
    }

    .form-group-atelier label {
        display: block;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-secondary);
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .input-atelier {
        width: 100%;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 10px 14px;
        color: var(--text-primary);
        font-size: 0.88rem;
        outline: none;
        box-sizing: border-box;
        transition: border-color 0.2s, background 0.2s;
    }

    .input-atelier:focus {
        border-color: #d97706;
        box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15);
    }

    .section-title-modal {
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--atelier-gold, #d97706);
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>"""

content = content[:idx_start] + new_style + content[idx_end + len("</style>"):]

# Replace inline white texts that cause invisible labels in light mode
content = content.replace('style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #fff; letter-spacing: -0.5px;"',
                          'style="margin: 0; font-size: 1.85rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px;"')
content = content.replace('style="font-weight: 700; color: #fff; font-size: 0.92rem;"',
                          'style="font-weight: 700; color: var(--text-primary); font-size: 0.92rem;"')
content = content.replace('style="font-weight: 600; color: #e5e5ea;"',
                          'style="font-weight: 600; color: var(--text-secondary);"')
content = content.replace('style="text-align: right; font-weight: 700; color: #fff;"',
                          'style="text-align: right; font-weight: 700; color: var(--text-primary);"')
content = content.replace('style="font-size: 1.25rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px;"',
                          'style="font-size: 1.25rem; font-weight: 800; color: var(--text-primary); display: flex; align-items: center; gap: 10px;"')

with open('templates/admin/empleados_rrhh.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates/admin/empleados_rrhh.html successfully")

