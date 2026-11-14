with open('templates/dashboard/superadmin.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        <div class="live-sync-indicator">
            <i class="fa-solid fa-arrows-rotate fa-spin" id="syncSpinner" style="opacity: 0.7;"></i>
            <span>Auto-Sync: <strong id="syncTimestamp">Iniciando...</strong></span>
        </div>
        <button type="button" class="btn-manual-sync" onclick="forzarActualizacionDashboard()" title="Actualizar datos de la base de datos de inmediato">
            <i class="fa-solid fa-rotate"></i> Actualizar
        </button>"""

new_block = """        <button type="button" class="btn-manual-sync" onclick="forzarActualizacionDashboard()" title="Recalcular métricas en vivo desde la Base de Datos">
            <i class="fa-solid fa-rotate" id="syncSpinner"></i> Recalcular en Vivo
        </button>"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('templates/dashboard/superadmin.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated superadmin.html successfully")
else:
    print("Block not found in superadmin.html")

