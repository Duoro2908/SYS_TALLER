new_historial_html = """{% extends "base.html" %}

{% block title %}Historial de Inventario - Bodega{% endblock %}
{% block page_title %}Historial de Compras y Abastecimiento{% endblock %}

{% block content %}
<style>
    /* Premium Themed History Layout */
    .history-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        background: var(--bg-surface);
        padding: 18px 22px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        flex-wrap: wrap;
        gap: 16px;
    }
    
    .search-box {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 10px 18px;
        border-radius: 10px;
        font-size: 0.92rem;
        min-width: 280px;
        transition: all 0.25s ease;
    }
    .search-box:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }

    /* Purchase Cards */
    .purchase-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .purchase-card {
        background: var(--bg-surface);
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        transition: all 0.25s ease;
    }

    .purchase-card:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 22px;
        cursor: pointer;
        user-select: none;
        background: var(--bg-surface);
    }

    .card-header-left { display: flex; align-items: center; gap: 16px; }
    
    .order-icon {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        background: rgba(37, 99, 235, 0.1);
        color: #2563eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
    }

    .order-info h4 { margin: 0 0 4px 0; color: var(--text-primary); font-size: 1.15rem; font-weight: 700; }
    .order-info p { margin: 0; color: var(--text-muted); font-size: 0.85rem; font-family: monospace; font-weight: 600; }
    
    .card-header-right { text-align: right; }
    .order-total { display: block; font-size: 1.35rem; font-weight: 800; color: #10b981; margin-bottom: 3px; }
    .btn-expand { background: none; border: none; color: var(--text-muted); font-size: 1.1rem; cursor: pointer; transition: transform 0.3s; }
    
    /* Details Table (Hidden by default) */
    .card-details {
        display: none;
        padding: 22px;
        background: var(--bg-primary);
        border-top: 1px solid var(--border-color);
    }

    .details-table {
        width: 100%;
        border-collapse: collapse;
    }

    .details-table th {
        text-align: left;
        color: var(--text-secondary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-color);
    }

    .details-table td {
        padding: 12px 0;
        border-bottom: 1px dashed var(--border-color);
        color: var(--text-primary);
        font-size: 0.9rem;
    }

    .details-table th.num, .details-table td.num { text-align: right; }

    .sku-badge {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        padding: 3px 7px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.78rem;
        color: var(--text-muted);
        font-weight: 600;
        margin-right: 8px;
    }

    /* Active State for Accordion */
    .purchase-card.active .btn-expand { transform: rotate(180deg); color: var(--text-primary); }
    .purchase-card.active .card-details { display: block; animation: slideDown 0.3s ease-out; }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>

<div class="history-toolbar">
    <div style="display: flex; align-items: center; gap: 12px;">
        <i class="fa-solid fa-clock-rotate-left" style="font-size: 1.4rem; color: #2563eb;"></i>
        <h3 style="margin: 0; color: var(--text-primary); font-size: 1.25rem; font-weight: 700;">Registro Completo de Ingresos</h3>
    </div>
    <input type="text" id="searchBox" class="search-box" placeholder="Buscar por Proveedor u Orden..." onkeyup="filterHistory()">
</div>

<div class="purchase-list" id="purchaseList">
    {% for c in historial_compras %}
    <div class="purchase-card searchable-card" data-search="{{ c.proveedor | lower }} {{ c.compra_id }}">
        <div class="card-header" onclick="toggleDetails(this)">
            <div class="card-header-left">
                <div class="order-icon"><i class="fa-solid fa-file-invoice"></i></div>
                <div class="order-info">
                    <h4>{{ c.proveedor }}</h4>
                    <p><i class="fa-regular fa-calendar"></i> {{ c.fecha.strftime('%d/%m/%Y %I:%M %p') }} &nbsp;|&nbsp; Orden #{{ c.compra_id }}</p>
                </div>
            </div>
            <div class="card-header-right">
                <span class="order-total">C$ {{ "{:,.2f}".format(c.total) }}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">IVA (15%) incluido</span>
                <button class="btn-expand"><i class="fa-solid fa-chevron-down"></i></button>
            </div>
        </div>
        
        <div class="card-details">
            <h5 style="color: var(--text-primary); margin-top: 0; margin-bottom: 14px; font-size: 0.98rem; font-weight: 700;">
                <i class="fa-solid fa-box-open" style="color: #2563eb;"></i> Detalle de Mercadería Ingresada
            </h5>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th class="num">Cant.</th>
                        <th class="num">Costo Unit. (C$)</th>
                        <th class="num">Subtotal (C$)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in c.detalles %}
                    <tr>
                        <td>
                            <span class="sku-badge">{{ d.sku }}</span>
                            {{ d.nombre }}
                        </td>
                        <td class="num">{{ d.cantidad }}</td>
                        <td class="num">C$ {{ "{:,.2f}".format(d.precio_unitario) }}</td>
                        <td class="num" style="color: #10b981; font-weight: 700;">C$ {{ "{:,.2f}".format(d.subtotal) }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px;">Sin detalles registrados.</td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" style="text-align: right; padding-top: 14px; color: var(--text-secondary); font-weight: 600; border: none;">Subtotal Mercadería:</td>
                        <td class="num" style="padding-top: 14px; color: var(--text-primary); font-weight: 700; border: none;">C$ {{ "{:,.2f}".format(c.subtotal) }}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="text-align: right; color: #2563eb; font-weight: 600; border: none;">IVA Compra (15%):</td>
                        <td class="num" style="color: #2563eb; font-weight: 700; border: none;">+ C$ {{ "{:,.2f}".format(c.iva) }}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="text-align: right; font-size: 1.05rem; font-weight: 800; color: var(--text-primary); border-top: 1px dashed var(--border-color); padding-top: 10px;">Total Factura Proveedor:</td>
                        <td class="num" style="font-size: 1.15rem; font-weight: 800; color: #10b981; border-top: 1px dashed var(--border-color); padding-top: 10px;">C$ {{ "{:,.2f}".format(c.total) }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>
    {% else %}
    <div style="text-align: center; padding: 50px 20px; background: var(--bg-surface); border-radius: 16px; border: 1px dashed var(--border-color);">
        <i class="fa-solid fa-folder-open" style="font-size: 3.5rem; color: #2563eb; opacity: 0.5; margin-bottom: 16px;"></i>
        <h3 style="color: var(--text-primary); margin-bottom: 8px; font-weight: 700;">No hay historial de compras</h3>
        <p style="color: var(--text-muted); margin: 0;">Los abastecimientos registrados en bodega aparecerán aquí.</p>
    </div>
    {% endfor %}
</div>

<script>
    function toggleDetails(element) {
        const card = element.closest('.purchase-card');
        card.classList.toggle('active');
    }

    function filterHistory() {
        const query = document.getElementById('searchBox').value.toLowerCase();
        const cards = document.querySelectorAll('.searchable-card');
        
        cards.forEach(card => {
            const searchData = card.getAttribute('data-search');
            if(searchData.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
</script>

{% endblock %}
"""

with open('templates/bodega/historial.html', 'w', encoding='utf-8') as f:
    f.write(new_historial_html)

print("Updated templates/bodega/historial.html successfully")

