new_compras_html = """{% extends "base.html" %}

{% block title %}Compras y Abastecimiento - Bodega{% endblock %}
{% block page_title %}Compras y Abastecimiento{% endblock %}

{% block content %}
<style>
    /* Premium Themed Layout for Compras */
    .purchase-container {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 25px;
        align-items: start;
    }
    
    @media (max-width: 1100px) {
        .purchase-container { grid-template-columns: 1fr; }
    }

    .glass-panel {
        background: var(--bg-surface);
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        padding: 26px;
        position: relative;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 22px;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 14px;
    }

    .section-header i {
        font-size: 1.6rem;
        color: #2563eb;
    }

    .section-header h3 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; margin-bottom: 7px; font-weight: 600; color: var(--text-secondary); font-size: 0.88rem; }
    
    .form-control {
        width: 100%;
        padding: 11px 15px;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        background: var(--bg-primary);
        color: var(--text-primary);
        font-size: 0.92rem;
        transition: all 0.25s ease;
        box-sizing: border-box;
    }
    .form-control:focus {
        border-color: #2563eb;
        outline: none;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    /* Supplier Row */
    .supplier-row {
        display: flex;
        gap: 14px;
        align-items: flex-end;
    }

    .btn-action {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        height: 44px;
    }
    .btn-action:hover { background: var(--border-color); transform: translateY(-1px); }
    
    .btn-primary {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #ffffff !important;
        border: none;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }
    .btn-primary:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
    }

    /* Professional Order Table */
    .order-table-container {
        margin-top: 24px;
        background: var(--bg-surface);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        overflow: hidden;
    }

    .order-table {
        width: 100%;
        border-collapse: collapse;
    }

    .order-table th {
        background: var(--bg-secondary);
        padding: 12px 14px;
        text-align: left;
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        border-bottom: 1px solid var(--border-color);
    }

    .order-table td {
        padding: 12px 14px;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
        vertical-align: middle;
    }

    .order-table .td-number { text-align: right; width: 125px;}
    .order-table .td-action { text-align: center; width: 55px; }

    .td-number input {
        text-align: right;
    }

    .btn-remove {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 8px;
        width: 34px;
        height: 34px;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .btn-remove:hover { background: #ef4444; color: white; transform: scale(1.05); }

    /* Grand Total Section */
    .grand-total-section {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-top: 22px;
        padding-top: 20px;
        border-top: 1px dashed var(--border-color);
    }

    .grand-total-label {
        font-size: 1.1rem;
        color: var(--text-primary);
        font-weight: 700;
        margin-right: 15px;
    }

    .grand-total-value {
        font-size: 2.0rem;
        font-weight: 800;
        color: #10b981;
    }

    /* History Cards */
    .history-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        border-left: 4px solid #2563eb;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    .history-card:hover { 
        transform: translateX(4px); 
        box-shadow: var(--shadow-md); 
        border-color: #2563eb;
    }
    
    .history-card .date { 
        font-size: 0.82rem; 
        color: var(--text-muted); 
        margin-bottom: 6px; 
        font-family: monospace; 
        font-weight: 600;
    }
    .history-card .prov { 
        font-weight: 700; 
        color: var(--text-primary); 
        font-size: 1.02rem; 
        margin-bottom: 8px; 
    }
    .history-card .subinfo {
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        font-size: 0.82rem; 
        color: var(--text-secondary); 
        margin-bottom: 6px;
    }
    .history-card .total { 
        font-weight: 800; 
        color: #10b981; 
        font-size: 1.15rem; 
        display: flex; 
        justify-content: space-between; 
        align-items: baseline; 
    }

    /* Modals */
    .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(5px); }
    .modal-content { background: var(--bg-surface); padding: 28px; border-radius: 16px; width: 100%; max-width: 500px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); color: var(--text-primary); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
    .modal-header h3 { margin: 0; color: var(--text-primary); font-weight: 700; font-size: 1.25rem; }
    .close-btn { background: none; border: none; font-size: 1.6rem; color: var(--text-muted); cursor: pointer; line-height: 1; }
    .close-btn:hover { color: var(--text-primary); }

</style>

<div class="purchase-container">
    
    <!-- Main Purchase Form -->
    <div class="glass-panel">
        <div class="section-header">
            <i class="fa-solid fa-truck-ramp-box"></i>
            <h3>Orden de Compra y Abastecimiento</h3>
        </div>

        <form action="{{ url_for('bodega.compras') }}" method="POST" id="comprasForm">
            
            <div class="supplier-row">
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                    <label>Proveedor</label>
                    <select name="proveedor_id" class="form-control" required>
                        <option value="">-- Seleccione Proveedor --</option>
                        {% for prov in proveedores %}
                        <option value="{{ prov[0] }}">{{ prov[1] }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="button" class="btn-action" onclick="document.getElementById('nuevoProveedorModal').style.display='flex'">
                    <i class="fa-solid fa-user-plus"></i> Nuevo
                </button>
            </div>

            <div class="order-table-container">
                <table class="order-table" id="productsTable">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th class="td-number">Cantidad</th>
                            <th class="td-number">Costo Unit. (C$)</th>
                            <th class="td-number">Subtotal (C$)</th>
                            <th class="td-action"></th>
                        </tr>
                    </thead>
                    <tbody id="productosContainer">
                        <tr class="product-row">
                            <td>
                                <select name="producto_id[]" class="form-control select-product" required>
                                    <option value="">-- Buscar Producto --</option>
                                    {% for prod in productos %}
                                    <option value="{{ prod[0] }}">{{ prod[1] }} - {{ prod[2] }}</option>
                                    {% endfor %}
                                </select>
                            </td>
                            <td class="td-number">
                                <input type="number" name="cantidad[]" class="form-control input-qty" placeholder="0" min="1" required oninput="calculateRow(this)">
                            </td>
                            <td class="td-number">
                                <input type="number" step="0.01" name="precio[]" class="form-control input-price" placeholder="0.00" min="0" required oninput="calculateRow(this)">
                            </td>
                            <td class="td-number">
                                <input type="text" class="form-control input-subtotal" value="0.00" readonly style="background: transparent; border-color: transparent; font-weight: 700; color: #10b981;">
                            </td>
                            <td class="td-action">
                                <button type="button" class="btn-remove" onclick="removeRow(this)"><i class="fa-solid fa-trash"></i></button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div style="padding: 14px; border-top: 1px solid var(--border-color);">
                    <button type="button" class="btn-action" style="width: 100%; justify-content: center; border-style: dashed;" onclick="addRow()">
                        <i class="fa-solid fa-plus"></i> Añadir Línea de Producto
                    </button>
                </div>
            </div>

            <div class="grand-total-section" style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
                <div style="display: flex; justify-content: space-between; width: 320px; font-size: 1rem; color: var(--text-secondary);">
                    <span>Subtotal Mercadería:</span>
                    <strong id="subtotalDisplay" style="color: var(--text-primary);">C$ 0.00</strong>
                </div>
                <div style="display: flex; justify-content: space-between; width: 320px; font-size: 1rem; color: var(--text-secondary);">
                    <span>IVA Compra (15.0%):</span>
                    <strong id="ivaDisplay" style="color: #2563eb;">+ C$ 0.00</strong>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; width: 320px; border-top: 1px dashed var(--border-color); padding-top: 10px; margin-top: 4px;">
                    <span class="grand-total-label" style="margin: 0;">Total Factura Proveedor:</span>
                    <span class="grand-total-value" id="grandTotalDisplay">C$ 0.00</span>
                </div>
            </div>

            <div style="margin-top: 25px;">
                <button type="submit" class="btn-action btn-primary" style="width: 100%; justify-content: center; height: 50px; font-size: 1.05rem;">
                    <i class="fa-solid fa-check-circle" style="font-size: 1.2rem;"></i> Procesar e Ingresar a Bodega
                </button>
            </div>
        </form>
    </div>

    <!-- History Panel -->
    <div class="glass-panel">
        <div class="section-header">
            <i class="fa-solid fa-clock-rotate-left"></i>
            <h3>Últimos Ingresos</h3>
        </div>
        
        {% for h in historial %}
        <div class="history-card">
            <div class="date">
                <i class="fa-regular fa-calendar"></i> {{ h[2].strftime('%d/%m/%Y %I:%M %p') }} 
                <span style="float: right;">OC #{{ h[0] }}</span>
            </div>
            <div class="prov">{{ h[1] }}</div>
            <div class="subinfo">
                <span>Subtotal: C$ {{ "{:,.2f}".format(h[4] if h|length > 4 and h[4] is not none else h[3] / 1.15) }}</span>
                <span style="color: #2563eb; font-weight: 600;">+ IVA 15%: C$ {{ "{:,.2f}".format(h[5] if h|length > 5 and h[5] is not none else h[3] - (h[3] / 1.15)) }}</span>
            </div>
            <div class="total">
                <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: normal;">Total con IVA:</span>
                <span>C$ {{ "{:,.2f}".format(h[3]) }}</span>
            </div>
        </div>
        {% else %}
        <div style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
            <i class="fa-solid fa-inbox" style="font-size: 2.8rem; margin-bottom: 12px; opacity: 0.5;"></i>
            <p style="margin: 0; font-size: 0.95rem;">No hay registros de compras recientes.</p>
        </div>
        {% endfor %}
    </div>

</div>

<!-- Modal: Nuevo Proveedor -->
<div id="nuevoProveedorModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3><i class="fa-solid fa-user-tie"></i> Registrar Proveedor</h3>
            <button class="close-btn" onclick="document.getElementById('nuevoProveedorModal').style.display='none'">&times;</button>
        </div>
        <form action="{{ url_for('bodega.nuevo_proveedor') }}" method="POST">
            <div class="form-group">
                <label>Nombre o Razón Social</label>
                <input type="text" name="nombre" class="form-control" required placeholder="Ej: Distribuidora de Repuestos S.A.">
            </div>
            <div class="form-group">
                <label>RUC (Opcional)</label>
                <input type="text" name="ruc" class="form-control" placeholder="Ej: J0310000000000">
            </div>
            <div class="form-group">
                <label>Teléfono de Contacto (Opcional)</label>
                <input type="text" name="telefono" class="form-control" placeholder="Ej: 2222-3333">
            </div>
            <button type="submit" class="btn-action btn-primary" style="width: 100%; justify-content: center; margin-top: 15px; height: 46px;">
                Guardar Proveedor
            </button>
        </form>
    </div>
</div>

<script>
    function calculateRow(element) {
        const row = element.closest('.product-row');
        const qty = parseFloat(row.querySelector('.input-qty').value) || 0;
        const price = parseFloat(row.querySelector('.input-price').value) || 0;
        const subtotal = qty * price;
        
        row.querySelector('.input-subtotal').value = subtotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        calculateGrandTotal();
    }

    function calculateGrandTotal() {
        let subtotal = 0;
        const rows = document.querySelectorAll('.product-row');
        rows.forEach(row => {
            const qty = parseFloat(row.querySelector('.input-qty').value) || 0;
            const price = parseFloat(row.querySelector('.input-price').value) || 0;
            subtotal += (qty * price);
        });
        
        const iva = Math.round(subtotal * 0.15 * 100) / 100;
        const grandTotal = Math.round((subtotal + iva) * 100) / 100;
        
        document.getElementById('subtotalDisplay').innerText = 'C$ ' + subtotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.getElementById('ivaDisplay').innerText = '+ C$ ' + iva.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.getElementById('grandTotalDisplay').innerText = 'C$ ' + grandTotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }

    function addRow() {
        const container = document.getElementById('productosContainer');
        const firstRow = container.querySelector('.product-row');
        const newRow = firstRow.cloneNode(true);
        
        // Reset values
        newRow.querySelector('.select-product').value = "";
        newRow.querySelector('.input-qty').value = "";
        newRow.querySelector('.input-price').value = "";
        newRow.querySelector('.input-subtotal').value = "0.00";
        
        container.appendChild(newRow);
        calculateGrandTotal();
    }

    function removeRow(btn) {
        const rows = document.querySelectorAll('.product-row');
        if(rows.length > 1) {
            btn.closest('.product-row').remove();
            calculateGrandTotal();
        } else {
            alert("Debe incluir al menos un producto en la orden.");
        }
    }
</script>

{% endblock %}
"""

with open('templates/bodega/compras.html', 'w', encoding='utf-8') as f:
    f.write(new_compras_html)
print("Updated templates/bodega/compras.html successfully")

