import re

def patch_routes_caja():
    filepath = 'routes/caja.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'def eliminar_orden' not in content:
        route_code = '''
@cashier_bp.route('/eliminar_orden/<int:orden_id>', methods=['POST'])
def eliminar_orden(orden_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5, 8, 1008]:
        flash('No tienes permisos para eliminar órdenes.', 'error')
        return redirect(url_for('cashier.ordenes_taller'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('cashier.ordenes_taller'))
        
    cursor = conn.cursor()
    try:
        # 1. Desvincular o cancelar CitaWhatsApp si estaba vinculada
        cursor.execute("""
            UPDATE CitasWhatsApp 
            SET Estado = 'Cancelada' 
            WHERE CitaID = (SELECT TOP 1 CitaID FROM OrdenesTrabajo WHERE OrdenID = ?)
        """, (orden_id,))
        
        # 2. Eliminar repuestos y mano de obra asociados
        cursor.execute("DELETE FROM OrdenRepuestos WHERE OrdenID = ?", (orden_id,))
        cursor.execute("DELETE FROM OrdenManoObra WHERE OrdenID = ?", (orden_id,))
        
        # 3. Eliminar la orden de trabajo
        cursor.execute("DELETE FROM OrdenesTrabajo WHERE OrdenID = ?", (orden_id,))
        
        conn.commit()
        flash(f'¡Orden de Trabajo #{orden_id} eliminada exitosamente de Caja!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar la Orden #{orden_id}: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('cashier.ordenes_taller'))
'''
        content += route_code
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("routes/caja.py patched with eliminar_orden!")
    else:
        print("routes/caja.py already has eliminar_orden")


def patch_templates_caja():
    filepath = 'templates/caja/index.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add styling for .btn-del-orden-caja in <style>
    style_target = ".btn-facturar:disabled {"
    idx = content.find(style_target)
    if idx != -1:
        css_del = """    .btn-del-orden-caja {
        background: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.32);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .btn-del-orden-caja:hover {
        background: #ef4444;
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
        transform: translateY(-2px);
    }
    [data-theme="light"] .btn-del-orden-caja {
        background: #fee2e2 !important;
        border-color: #fca5a5 !important;
        color: #dc2626 !important;
    }
    [data-theme="light"] .btn-del-orden-caja:hover {
        background: #dc2626 !important;
        color: #ffffff !important;
    }
"""
        content = content[:idx] + css_del + content[idx:]

    # Add delete button next to facturar
    old_form = """                    <form action="{{ url_for('cashier.facturar', orden_id=o[0]) }}" method="POST" class="order-pay-form">
                        <select name="metodo_pago" class="select-metodo-pago">
                            <option value="Efectivo">💵 Efectivo (C$ / USD)</option>
                            <option value="Tarjeta">💳 Tarjeta / POS</option>
                            <option value="Transferencia">📲 Transferencia (BAC / Lafise)</option>
                        </select>
                        <button type="submit" class="btn-facturar">
                            <i class="fa-solid fa-receipt"></i> Facturar
                        </button>
                    </form>
                {% else %}
                    <button class="btn-facturar" disabled title="Debes abrir turno de caja para facturar" style="width: 100%;">
                        <i class="fa-solid fa-lock"></i> Turno Cerrado
                    </button>
                {% endif %}"""

    new_form = """                    <form action="{{ url_for('cashier.facturar', orden_id=o[0]) }}" method="POST" class="order-pay-form">
                        <select name="metodo_pago" class="select-metodo-pago">
                            <option value="Efectivo">💵 Efectivo (C$ / USD)</option>
                            <option value="Tarjeta">💳 Tarjeta / POS</option>
                            <option value="Transferencia">📲 Transferencia (BAC / Lafise)</option>
                        </select>
                        <button type="submit" class="btn-facturar">
                            <i class="fa-solid fa-receipt"></i> Facturar
                        </button>
                        <button type="button" class="btn-del-orden-caja" title="Eliminar Orden #{{ o[0] }}" onclick="confirmarEliminarOrdenCaja('{{ o[0] }}')">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </form>
                {% else %}
                    <div style="display: flex; gap: 8px; width: 100%;">
                        <button class="btn-facturar" disabled title="Debes abrir turno de caja para facturar" style="flex: 1;">
                            <i class="fa-solid fa-lock"></i> Turno Cerrado
                        </button>
                        <button type="button" class="btn-del-orden-caja" title="Eliminar Orden #{{ o[0] }}" onclick="confirmarEliminarOrdenCaja('{{ o[0] }}')">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                {% endif %}"""

    content = content.replace(old_form, new_form)

    # Add confirmation modal before {% endblock %}
    if 'id="modalConfirmarDelOrden"' not in content:
        modal_html = """
<!-- Modal Confirmación Eliminar Orden de Caja -->
<div id="modalConfirmarDelOrden" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(6px); z-index: 10000; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 18px; max-width: 440px; width: 100%; padding: 26px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); text-align: center;">
        <div style="width: 58px; height: 58px; border-radius: 50%; background: rgba(239, 68, 68, 0.15); color: #ef4444; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 1.6rem; border: 1px solid rgba(239, 68, 68, 0.3);">
            <i class="fa-solid fa-trash-can"></i>
        </div>
        <h3 style="margin: 0 0 8px 0; color: var(--text-primary); font-size: 1.3rem; font-weight: 800;">¿Eliminar Orden de Trabajo?</h3>
        <p id="delOrdenModalDesc" style="color: var(--text-secondary); font-size: 0.92rem; margin: 0 0 22px 0; line-height: 1.5;"></p>
        <form id="formEliminarOrdenCaja" method="POST" action="" style="display: flex; gap: 12px; justify-content: center;">
            <button type="button" onclick="cerrarModalDelOrden()" style="flex: 1; padding: 11px 18px; border-radius: 10px; border: 1px solid var(--border-color); background: var(--bg-primary); color: var(--text-primary); font-weight: 600; cursor: pointer;">Cancelar</button>
            <button type="submit" style="flex: 1; padding: 11px 18px; border-radius: 10px; border: none; background: #ef4444; color: #fff; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(239,68,68,0.4);"><i class="fa-solid fa-trash-can"></i> Sí, Eliminar</button>
        </form>
    </div>
</div>

<script>
function confirmarEliminarOrdenCaja(ordenId) {
    const modal = document.getElementById('modalConfirmarDelOrden');
    const form = document.getElementById('formEliminarOrdenCaja');
    const desc = document.getElementById('delOrdenModalDesc');
    form.action = '/caja/eliminar_orden/' + ordenId;
    desc.innerText = '¿Estás seguro de eliminar permanentemente la Orden #' + ordenId + ' de la Caja? La motocicleta y sus detalles serán removidos de la lista de cobro.';
    modal.style.display = 'flex';
}
function cerrarModalDelOrden() {
    const modal = document.getElementById('modalConfirmarDelOrden');
    if (modal) modal.style.display = 'none';
}
</script>
{% endblock %}"""
        content = content.replace("{% endblock %}", modal_html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/caja/index.html patched with delete button and modal!")


def patch_estadisticas_taller_html():
    filepath = 'templates/dashboard/estadisticas_taller.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the script section starting at <script>
    start_tag = "<!-- Chart.js CDN -->"
    idx = content.find(start_tag)
    if idx == -1:
        start_tag = "<script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>"
        idx = content.find(start_tag)

    if idx != -1:
        new_script = """<script>
window.initEstadisticasCharts = function() {
    if (typeof Chart === 'undefined') {
        setTimeout(window.initEstadisticasCharts, 60);
        return;
    }

    const canvasEv = document.getElementById('evolucionTallerChart');
    if (!canvasEv) return;

    if (window._estadisticasChartInstances && window._estadisticasChartInstances.length) {
        window._estadisticasChartInstances.forEach(c => { try { c.destroy(); } catch(e){} });
    }
    window._estadisticasChartInstances = [];

    function getChartThemeTokens() {
        const theme = document.documentElement.getAttribute('data-theme') || 'dark';
        const isLight = (theme === 'light');
        return {
            textColor: isLight ? '#334155' : '#cbd5e1',
            legendColor: isLight ? '#0f172a' : '#e2e8f0',
            gridColor: isLight ? 'rgba(15, 23, 42, 0.08)' : 'rgba(255, 255, 255, 0.08)',
            surfaceBorder: isLight ? '#ffffff' : '#121316'
        };
    }

    let tokens = getChartThemeTokens();
    Chart.defaults.color = tokens.textColor;
    Chart.defaults.font.family = "'Inter', sans-serif";

    // 1. Gráfico Evolución
    const ctxEvolucion = canvasEv.getContext('2d');
    let labelsHist = {{ stats.labels_grafico | tojson | safe }};
    let datosIngresos = {{ stats.datos_grafico | tojson | safe }};
    let datosOrdenes = {{ stats.ordenes_grafico | tojson | safe }};

    if (!labelsHist || labelsHist.length === 0) {
        labelsHist = ['Jun 2026', 'Jul 2026', 'Ago 2026', 'Sep 2026', 'Oct 2026', 'Nov 2026'];
        datosIngresos = [0, 0, 0, 0, 0, {{ stats.ingresos_mes | default(0.0) }}];
        datosOrdenes = [0, 0, 0, 0, 0, {{ stats.ordenes_facturadas_mes | default(0) }}];
    }

    const gradienteIngresos = ctxEvolucion.createLinearGradient(0, 0, 0, 300);
    gradienteIngresos.addColorStop(0, 'rgba(245, 158, 11, 0.4)');
    gradienteIngresos.addColorStop(1, 'rgba(245, 158, 11, 0.0)');

    window._estadisticasChartInstances.push(new Chart(ctxEvolucion, {
        type: 'bar',
        data: {
            labels: labelsHist,
            datasets: [
                {
                    type: 'line',
                    label: 'Facturación (C$)',
                    data: datosIngresos,
                    borderColor: '#f59e0b',
                    backgroundColor: gradienteIngresos,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#d97706',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    yAxisID: 'y'
                },
                {
                    type: 'bar',
                    label: 'Órdenes Facturadas',
                    data: datosOrdenes,
                    backgroundColor: 'rgba(59, 130, 246, 0.65)',
                    borderColor: '#2563eb',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    barPercentage: 0.45,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: tokens.legendColor, font: { weight: '600', size: 12 }, padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(c) {
                            return c.dataset.yAxisID === 'y'
                                ? c.dataset.label + ': C$ ' + Number(c.raw).toLocaleString('es-NI', {minimumFractionDigits: 2})
                                : c.dataset.label + ': ' + c.raw + ' órdenes';
                        }
                    }
                }
            },
            scales: {
                x: { grid: { color: tokens.gridColor }, ticks: { color: tokens.textColor } },
                y: {
                    type: 'linear', position: 'left',
                    grid: { color: tokens.gridColor },
                    ticks: {
                        color: tokens.textColor,
                        callback: v => 'C$ ' + Number(v).toLocaleString('es-NI')
                    }
                },
                y1: {
                    type: 'linear', position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: tokens.textColor, precision: 0 }
                }
            }
        }
    }));

    // 2. Gráfico Servicios (Doughnut)
    const canvasSrv = document.getElementById('serviciosChart');
    if (canvasSrv) {
        let srvLabels = {{ stats.servicios_labels | tojson | safe }};
        let srvCounts = {{ stats.servicios_counts | tojson | safe }};
        if (!srvLabels || srvLabels.length === 0) {
            srvLabels = ['Preventivo', 'Correctivo', 'General'];
            srvCounts = [1, 0, 0];
        }
        window._estadisticasChartInstances.push(new Chart(canvasSrv.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: srvLabels,
                datasets: [{
                    data: srvCounts,
                    backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6'],
                    borderColor: tokens.surfaceBorder,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: tokens.legendColor, font: { weight: '600', size: 11 } } }
                },
                cutout: '68%'
            }
        }));
    }

    // 3. Gráfico Mecánicos
    const canvasMec = document.getElementById('mecanicosChart');
    if (canvasMec) {
        let mecLabels = {{ stats.mecanicos_labels | tojson | safe }};
        let mecOrdenes = {{ stats.mecanicos_ordenes | tojson | safe }};
        if (!mecLabels || mecLabels.length === 0) {
            mecLabels = ['Jose Mecánico'];
            mecOrdenes = [{{ stats.ordenes_facturadas_mes | default(1) }}];
        }
        window._estadisticasChartInstances.push(new Chart(canvasMec.getContext('2d'), {
            type: 'bar',
            data: {
                labels: mecLabels,
                datasets: [{
                    label: 'Órdenes Atendidas',
                    data: mecOrdenes,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: tokens.textColor } },
                    y: { grid: { color: tokens.gridColor }, ticks: { precision: 0, color: tokens.textColor } }
                }
            }
        }));
    }

    // 4. Gráfico Composición (Mano de Obra vs Repuestos)
    const canvasComp = document.getElementById('composicionChart');
    if (canvasComp) {
        window._estadisticasChartInstances.push(new Chart(canvasComp.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Mano de Obra', 'Repuestos'],
                datasets: [{
                    data: [{{ stats.pct_mano_obra | default(50) }}, {{ stats.pct_repuestos | default(50) }}],
                    backgroundColor: ['#06b6d4', '#f59e0b'],
                    borderColor: tokens.surfaceBorder,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: tokens.legendColor, font: { weight: '600', size: 11 } } }
                },
                cutout: '68%'
            }
        }));
    }

    // 5. Gráfico Marcas
    const canvasMarcas = document.getElementById('marcasChart');
    if (canvasMarcas) {
        let marcasLabels = {{ stats.marcas_labels | tojson | safe }};
        let marcasCounts = {{ stats.marcas_counts | tojson | safe }};
        if (!marcasLabels || marcasLabels.length === 0) {
            marcasLabels = ['Genesis', 'Serpento', 'Yamaha'];
            marcasCounts = [1, 0, 0];
        }
        window._estadisticasChartInstances.push(new Chart(canvasMarcas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: marcasLabels,
                datasets: [{
                    label: 'Motos Atendidas',
                    data: marcasCounts,
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: tokens.textColor } },
                    y: { grid: { color: tokens.gridColor }, ticks: { precision: 0, color: tokens.textColor } }
                }
            }
        }));
    }

    function refreshChartsTheme() {
        const t = getChartThemeTokens();
        Chart.defaults.color = t.textColor;
        (window._estadisticasChartInstances || []).forEach(chart => {
            if (chart.options?.plugins?.legend?.labels) chart.options.plugins.legend.labels.color = t.legendColor;
            if (chart.options?.scales) {
                Object.values(chart.options.scales).forEach(scale => {
                    if (scale.ticks) scale.ticks.color = t.textColor;
                    if (scale.grid && scale.grid.display !== false && scale.grid.drawOnChartArea !== false) scale.grid.color = t.gridColor;
                });
            }
            if (chart.config?.type === 'doughnut' && chart.data?.datasets) {
                chart.data.datasets.forEach(ds => { ds.borderColor = t.surfaceBorder; });
            }
            chart.update('none');
        });
    }

    if (window._themeObserverCharts) {
        try { window._themeObserverCharts.disconnect(); } catch(e){}
    }
    window._themeObserverCharts = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.attributeName === 'data-theme') {
                refreshChartsTheme();
                break;
            }
        }
    });
    window._themeObserverCharts.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
};

// Inicialización inmediata o al cargar el DOM
if (document.readyState === 'loading') {
    document.addEventListener("DOMContentLoaded", window.initEstadisticasCharts);
} else {
    window.initEstadisticasCharts();
}
</script>
{% endblock %}"""
        content = content[:idx] + new_script
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("templates/dashboard/estadisticas_taller.html patched with robust chart initialization!")
    else:
        print("Could not find script start in estadisticas_taller.html")


if __name__ == '__main__':
    patch_routes_caja()
    patch_templates_caja()
    patch_estadisticas_taller_html()

