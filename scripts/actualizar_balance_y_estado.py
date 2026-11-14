import re

def update_all():
    # -------------------------------------------------------------
    # 1. ACTUALIZAR RAZONES.HTML (Mandar Imprimir a Historial)
    # -------------------------------------------------------------
    with open('templates/contador/razones.html', 'r', encoding='utf-8') as f:
        raz_content = f.read()

    old_btn_print = """            <button type="button" class="btn-nav-action primary" onclick="window.print()" title="Imprimir Informe Oficial">
                <i class="fa-solid fa-print"></i> Imprimir Informe
            </button>"""

    new_btn_hist = """            <a href="{{ url_for('contador.historial_finanzas', anio=anio_seleccionado, mes=mes_seleccionado) }}" class="btn-nav-action primary" title="Ver Historial Certificado e Imprimir">
                <i class="fa-solid fa-clock-rotate-left"></i> Historial e Imprimir
            </a>"""

    raz_content = raz_content.replace(old_btn_print.replace('\n', '\r\n'), new_btn_hist.replace('\n', '\r\n'))
    raz_content = raz_content.replace(old_btn_print, new_btn_hist)
    with open('templates/contador/razones.html', 'w', encoding='utf-8') as f:
        f.write(raz_content)
    print("templates/contador/razones.html actualizado!")

    # -------------------------------------------------------------
    # MODALES Y ESTILOS COMUNES PARA AGREGAR Y EDITAR CUENTAS
    # -------------------------------------------------------------
    modal_styles_and_scripts = """
<style>
    .btn-table-icon {
        background: transparent;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }
    .btn-table-icon.edit:hover {
        background: rgba(37, 99, 235, 0.15);
        color: #2563eb;
        border-color: #2563eb;
    }
    .btn-table-icon.delete:hover {
        background: rgba(255, 69, 58, 0.15);
        color: #ff453a;
        border-color: #ff453a;
    }
    .custom-account-row {
        background: rgba(37, 99, 235, 0.03);
        border-left: 3px solid #2563eb !important;
    }
    .modal-backdrop-custom {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 99999;
        align-items: center;
        justify-content: center;
    }
    .modal-card-custom {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        width: 100%;
        max-width: 500px;
        padding: 26px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        display: flex;
        flex-direction: column;
        gap: 18px;
    }
    .modal-card-custom h4 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 800;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .form-group-custom {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .form-group-custom label {
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .form-input-custom, .form-select-custom {
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-primary);
        font-size: 0.92rem;
        outline: none;
        transition: border-color 0.2s;
    }
    .form-input-custom:focus, .form-select-custom:focus {
        border-color: #2563eb;
    }
    .modal-actions-custom {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 10px;
    }
</style>

<!-- MODAL AGREGAR CUENTA -->
<div id="modalAgregarCuenta" class="modal-backdrop-custom">
    <div class="modal-card-custom">
        <h4><i class="fa-solid fa-plus-circle" style="color: #2563eb;"></i> Agregar Cuenta Contable</h4>
        <form method="POST" action="{{ url_for('contador.agregar_cuenta') }}">
            <input type="hidden" name="tipo_reporte" id="inputTipoReporte" value="Balance">
            <input type="hidden" name="mes" value="{{ mes_seleccionado }}">
            <input type="hidden" name="anio" value="{{ anio_seleccionado }}">
            <div class="form-group-custom">
                <label for="selectCategoriaCuenta">Categoría Contable:</label>
                <select name="categoria" id="selectCategoriaCuenta" class="form-select-custom" required>
                    <!-- Dinámico según tipo_reporte -->
                </select>
            </div>
            <div class="form-group-custom" style="margin-top: 12px;">
                <label for="inputNombreCuenta">Nombre de la Cuenta:</label>
                <input type="text" name="nombre_cuenta" id="inputNombreCuenta" class="form-input-custom" placeholder="Ej: Herramientas Neumáticas Especializadas" required>
            </div>
            <div class="form-group-custom" style="margin-top: 12px;">
                <label for="inputMontoCuenta">Monto en Córdobas (C$):</label>
                <input type="number" step="0.01" min="0" name="monto" id="inputMontoCuenta" class="form-input-custom" placeholder="0.00" required>
            </div>
            <div class="modal-actions-custom">
                <button type="button" class="btn-cont-action" onclick="cerrarModalAgregarCuenta()">Cancelar</button>
                <button type="submit" class="btn-cont-action primary"><i class="fa-solid fa-check"></i> Guardar Cuenta</button>
            </div>
        </form>
    </div>
</div>

<!-- MODAL EDITAR CUENTA -->
<div id="modalEditarCuenta" class="modal-backdrop-custom">
    <div class="modal-card-custom">
        <h4><i class="fa-solid fa-pen-to-square" style="color: #2563eb;"></i> Editar Cuenta Contable</h4>
        <form method="POST" action="{{ url_for('contador.editar_cuenta') }}">
            <input type="hidden" name="ajuste_id" id="editAjusteId">
            <input type="hidden" name="tipo_reporte" id="editTipoReporte">
            <input type="hidden" name="mes" value="{{ mes_seleccionado }}">
            <input type="hidden" name="anio" value="{{ anio_seleccionado }}">
            <div class="form-group-custom">
                <label for="editSelectCategoria">Categoría Contable:</label>
                <select name="categoria" id="editSelectCategoria" class="form-select-custom" required>
                </select>
            </div>
            <div class="form-group-custom" style="margin-top: 12px;">
                <label for="editNombreCuenta">Nombre de la Cuenta:</label>
                <input type="text" name="nombre_cuenta" id="editNombreCuenta" class="form-input-custom" required>
            </div>
            <div class="form-group-custom" style="margin-top: 12px;">
                <label for="editMontoCuenta">Monto en Córdobas (C$):</label>
                <input type="number" step="0.01" min="0" name="monto" id="editMontoCuenta" class="form-input-custom" required>
            </div>
            <div class="modal-actions-custom">
                <button type="button" class="btn-cont-action" onclick="cerrarModalEditarCuenta()">Cancelar</button>
                <button type="submit" class="btn-cont-action primary"><i class="fa-solid fa-save"></i> Actualizar</button>
            </div>
        </form>
    </div>
</div>

<!-- FORMULARIO OCULTO PARA ELIMINAR -->
<form id="formEliminarCuenta" method="POST" style="display: none;">
    <input type="hidden" name="tipo_reporte" id="delTipoReporte">
    <input type="hidden" name="mes" value="{{ mes_seleccionado }}">
    <input type="hidden" name="anio" value="{{ anio_seleccionado }}">
</form>

<script>
    const CATEGORIAS_BALANCE = [
        'Activo Corriente',
        'Activo No Corriente',
        'Pasivo Corriente',
        'Pasivo No Corriente',
        'Patrimonio'
    ];

    const CATEGORIAS_ESTADO = [
        'Ingresos Operativos',
        'Costos de Ventas',
        'Gastos Operativos',
        'Otros Ingresos / Gastos'
    ];

    function abrirModalAgregarCuenta(tipo) {
        document.getElementById('inputTipoReporte').value = tipo;
        const select = document.getElementById('selectCategoriaCuenta');
        select.innerHTML = '';
        const cats = tipo === 'Balance' ? CATEGORIAS_BALANCE : CATEGORIAS_ESTADO;
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            select.appendChild(opt);
        });
        document.getElementById('inputNombreCuenta').value = '';
        document.getElementById('inputMontoCuenta').value = '';
        const modal = document.getElementById('modalAgregarCuenta');
        modal.style.display = 'flex';
    }

    function cerrarModalAgregarCuenta() {
        document.getElementById('modalAgregarCuenta').style.display = 'none';
    }

    function editarCuentaPersonalizada(id, nombre, monto, categoria, tipo) {
        document.getElementById('editAjusteId').value = id;
        document.getElementById('editTipoReporte').value = tipo;
        document.getElementById('editNombreCuenta').value = nombre;
        document.getElementById('editMontoCuenta').value = monto;
        const select = document.getElementById('editSelectCategoria');
        select.innerHTML = '';
        const cats = tipo === 'Balance' ? CATEGORIAS_BALANCE : CATEGORIAS_ESTADO;
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            if (c.toLowerCase() === categoria.toLowerCase()) opt.selected = true;
            select.appendChild(opt);
        });
        document.getElementById('modalEditarCuenta').style.display = 'flex';
    }

    function cerrarModalEditarCuenta() {
        document.getElementById('modalEditarCuenta').style.display = 'none';
    }

    function eliminarCuentaPersonalizada(id, tipo) {
        if (confirm('¿Estás seguro de que deseas eliminar esta cuenta contable?')) {
            const form = document.getElementById('formEliminarCuenta');
            form.action = '/contador/eliminar_cuenta/' + id;
            document.getElementById('delTipoReporte').value = tipo;
            form.submit();
        }
    }
</script>
"""

    # -------------------------------------------------------------
    # 2. ACTUALIZAR BALANCE.HTML
    # -------------------------------------------------------------
    with open('templates/contador/balance.html', 'r', encoding='utf-8') as f:
        bal_content = f.read()

    # Replace PYMES with MiPyMEs
    bal_content = bal_content.replace('(NIIF para PYMES)', '(NIIF para las MiPyMEs)')
    bal_content = bal_content.replace('PYME', 'MiPyME')
    bal_content = bal_content.replace('PyME', 'MiPyME')

    # Add "+ Agregar Cuenta" button
    old_bal_actions = """            <!-- Sellar Cierre Oficial -->
            {% if not es_oficial_cerrado %}
            <form method="POST" action="{{ url_for('contador.balance', mes=mes_seleccionado, anio=anio_seleccionado) }}" style="display: inline;">
                <input type="hidden" name="action" value="guardar_cierre">
                <button type="submit" class="btn-cont-action success" title="Sella y archiva el balance oficial del mes para auditoría">
                    <i class="fa-solid fa-shield-halved"></i>
                    Sellar Cierre Oficial
                </button>
            </form>"""

    new_bal_actions = """            <!-- Botón Agregar Cuenta Contable -->
            <button type="button" class="btn-cont-action primary" onclick="abrirModalAgregarCuenta('Balance')" title="Añadir nueva cuenta contable o ajuste dinámico">
                <i class="fa-solid fa-plus-circle"></i> Agregar Cuenta
            </button>

            <!-- Sellar Cierre Oficial -->
            {% if not es_oficial_cerrado %}
            <form method="POST" action="{{ url_for('contador.balance', mes=mes_seleccionado, anio=anio_seleccionado) }}" style="display: inline;">
                <input type="hidden" name="action" value="guardar_cierre">
                <button type="submit" class="btn-cont-action success" title="Sella y archiva el balance oficial del mes para auditoría">
                    <i class="fa-solid fa-shield-halved"></i>
                    Sellar Cierre Oficial
                </button>
            </form>"""

    bal_content = bal_content.replace(old_bal_actions.replace('\n', '\r\n'), new_bal_actions.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_bal_actions, new_bal_actions)

    # Add custom accounts in 1.1 Activo Corriente
    old_subtotal_act_corr = """            <div class="subtotal-row">
                <span>TOTAL ACTIVO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.activo_circulante) }}</span>
            </div>"""

    new_subtotal_act_corr = """            {% for c in fin.cuentas_pers_activo_corriente %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">1.1.{{ loop.index + 4 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'Balance')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'Balance')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL ACTIVO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.activo_circulante) }}</span>
            </div>"""

    bal_content = bal_content.replace(old_subtotal_act_corr.replace('\n', '\r\n'), new_subtotal_act_corr.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_subtotal_act_corr, new_subtotal_act_corr)

    # Add custom accounts in 1.2 Activo No Corriente
    old_subtotal_act_fijo = """            <div class="subtotal-row">
                <span>TOTAL ACTIVO NO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.activo_fijo_total) }}</span>
            </div>"""

    new_subtotal_act_fijo = """            {% for c in fin.cuentas_pers_activo_no_corriente %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">1.2.{{ loop.index + 4 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'Balance')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'Balance')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL ACTIVO NO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.activo_fijo_total) }}</span>
            </div>"""

    bal_content = bal_content.replace(old_subtotal_act_fijo.replace('\n', '\r\n'), new_subtotal_act_fijo.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_subtotal_act_fijo, new_subtotal_act_fijo)

    # Add custom accounts in 2.1 Pasivo Corriente
    old_subtotal_pas_corr = """            <div class="subtotal-row">
                <span>TOTAL PASIVO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.pasivo_circulante) }}</span>
            </div>"""

    new_subtotal_pas_corr = """            {% for c in fin.cuentas_pers_pasivo_corriente %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">2.1.{{ loop.index + 4 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'Balance')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'Balance')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL PASIVO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.pasivo_circulante) }}</span>
            </div>"""

    bal_content = bal_content.replace(old_subtotal_pas_corr.replace('\n', '\r\n'), new_subtotal_pas_corr.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_subtotal_pas_corr, new_subtotal_pas_corr)

    # Add custom accounts in 2.2 Pasivo No Corriente
    old_subtotal_pas_fijo = """            <div class="subtotal-row">
                <span>TOTAL PASIVO NO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.pasivo_largo_plazo) }}</span>
            </div>"""

    new_subtotal_pas_fijo = """            {% for c in fin.cuentas_pers_pasivo_no_corriente %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">2.2.{{ loop.index + 1 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'Balance')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'Balance')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL PASIVO NO CORRIENTE</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.pasivo_largo_plazo) }}</span>
            </div>"""

    bal_content = bal_content.replace(old_subtotal_pas_fijo.replace('\n', '\r\n'), new_subtotal_pas_fijo.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_subtotal_pas_fijo, new_subtotal_pas_fijo)

    # Add custom accounts in 3.1 Patrimonio
    old_subtotal_patri = """            <div class="subtotal-row">
                <span>TOTAL PATRIMONIO NETO</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.patrimonio) }}</span>
            </div>"""

    new_subtotal_patri = """            {% for c in fin.cuentas_pers_patrimonio %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">3.1.{{ loop.index + 3 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'Balance')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'Balance')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL PATRIMONIO NETO</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.patrimonio) }}</span>
            </div>"""

    bal_content = bal_content.replace(old_subtotal_patri.replace('\n', '\r\n'), new_subtotal_patri.replace('\n', '\r\n'))
    bal_content = bal_content.replace(old_subtotal_patri, new_subtotal_patri)

    # Append modals and scripts before {% endblock %}
    if 'id="modalAgregarCuenta"' not in bal_content:
        bal_content = bal_content.replace('{% endblock %}', modal_styles_and_scripts + '\n{% endblock %}')

    with open('templates/contador/balance.html', 'w', encoding='utf-8') as f:
        f.write(bal_content)
    print("templates/contador/balance.html actualizado exitosamente!")

    # -------------------------------------------------------------
    # 3. ACTUALIZAR ESTADO_RESULTADOS.HTML
    # -------------------------------------------------------------
    with open('templates/contador/estado_resultados.html', 'r', encoding='utf-8') as f:
        est_content = f.read()

    est_content = est_content.replace('(NIIF para PYMES)', '(NIIF para las MiPyMEs)')
    est_content = est_content.replace('PYME', 'MiPyME')
    est_content = est_content.replace('PyME', 'MiPyME')

    # Add "+ Agregar Cuenta" button in estado_resultados
    old_est_actions = """            <!-- Sellar Cierre Oficial -->
            {% if not es_oficial_cerrado %}
            <form method="POST" action="{{ url_for('contador.estado_resultados', mes=mes_seleccionado, anio=anio_seleccionado) }}" style="display: inline;">
                <input type="hidden" name="action" value="guardar_cierre">
                <button type="submit" class="btn-cont-action success" title="Sella y archiva el estado oficial para auditoría">
                    <i class="fa-solid fa-shield-halved"></i>
                    Sellar Cierre Oficial
                </button>
            </form>"""

    new_est_actions = """            <!-- Botón Agregar Cuenta Contable -->
            <button type="button" class="btn-cont-action primary" onclick="abrirModalAgregarCuenta('EstadoResultados')" title="Añadir nueva cuenta contable o ajuste dinámico">
                <i class="fa-solid fa-plus-circle"></i> Agregar Cuenta
            </button>

            <!-- Sellar Cierre Oficial -->
            {% if not es_oficial_cerrado %}
            <form method="POST" action="{{ url_for('contador.estado_resultados', mes=mes_seleccionado, anio=anio_seleccionado) }}" style="display: inline;">
                <input type="hidden" name="action" value="guardar_cierre">
                <button type="submit" class="btn-cont-action success" title="Sella y archiva el estado oficial para auditoría">
                    <i class="fa-solid fa-shield-halved"></i>
                    Sellar Cierre Oficial
                </button>
            </form>"""

    est_content = est_content.replace(old_est_actions.replace('\n', '\r\n'), new_est_actions.replace('\n', '\r\n'))
    est_content = est_content.replace(old_est_actions, new_est_actions)

    # In Gastos Operativos: add Mercadotecnia and custom gastos
    old_subtotal_gastos = """            <div class="subtotal-row">
                <span>TOTAL GASTOS OPERATIVOS Y ADMINISTRATIVOS</span>
                <span class="amount" style="color: #ef4444;">C$ {{ "{:,.2f}".format(fin.gastos_operativos) }}</span>
            </div>"""

    new_subtotal_gastos = """            <div class="account-row">
                <div class="account-name">
                    <span class="account-code">6.1.08</span>
                    <span>Mercadotecnia, Publicidad y Costo de Premios de Rifas</span>
                    <span class="account-detail-tag"><i class="fa-solid fa-bullhorn"></i> Módulo Mercadotecnia</span>
                </div>
                <div class="account-amount">C$ {{ "{:,.2f}".format(fin.gastos_mercadotecnia) }}</div>
            </div>

            {% for c in fin.cuentas_pers_gastos %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">6.1.{{ loop.index + 8 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'EstadoResultados')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'EstadoResultados')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL GASTOS OPERATIVOS Y ADMINISTRATIVOS</span>
                <span class="amount" style="color: #ef4444;">C$ {{ "{:,.2f}".format(fin.gastos_operativos) }}</span>
            </div>"""

    est_content = est_content.replace(old_subtotal_gastos.replace('\n', '\r\n'), new_subtotal_gastos.replace('\n', '\r\n'))
    est_content = est_content.replace(old_subtotal_gastos, new_subtotal_gastos)

    # In Ingresos: add custom ingresos
    old_subtotal_ingresos = """            <div class="subtotal-row">
                <span>TOTAL VENTAS NETAS FACTURADAS</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.ventas_netas) }}</span>
            </div>"""

    new_subtotal_ingresos = """            {% for c in fin.cuentas_pers_ingresos %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">4.1.{{ loop.index + 3 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'EstadoResultados')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'EstadoResultados')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL VENTAS NETAS FACTURADAS</span>
                <span class="amount">C$ {{ "{:,.2f}".format(fin.ventas_netas) }}</span>
            </div>"""

    est_content = est_content.replace(old_subtotal_ingresos.replace('\n', '\r\n'), new_subtotal_ingresos.replace('\n', '\r\n'))
    est_content = est_content.replace(old_subtotal_ingresos, new_subtotal_ingresos)

    # In Costos: add custom costos
    old_subtotal_costos = """            <div class="subtotal-row">
                <span>TOTAL COSTO DE VENTAS</span>
                <span class="amount" style="color: #f59e0b;">C$ {{ "{:,.2f}".format(fin.costo_ventas) }}</span>
            </div>"""

    new_subtotal_costos = """            {% for c in fin.cuentas_pers_costos %}
            <div class="account-row custom-account-row">
                <div class="account-name">
                    <span class="account-code">5.1.{{ loop.index + 2 }}</span>
                    <span>{{ c.nombre }}</span>
                    <span class="account-detail-tag" style="background: rgba(37, 99, 235, 0.15); color: #2563eb;">Personalizada</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="account-amount">C$ {{ "{:,.2f}".format(c.monto) }}</div>
                    <button type="button" class="btn-table-icon edit" onclick="editarCuentaPersonalizada({{ c.id }}, '{{ c.nombre }}', {{ c.monto }}, '{{ c.categoria }}', 'EstadoResultados')" title="Editar Cuenta"><i class="fa-solid fa-pen"></i></button>
                    <button type="button" class="btn-table-icon delete" onclick="eliminarCuentaPersonalizada({{ c.id }}, 'EstadoResultados')" title="Eliminar Cuenta"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}

            <div class="subtotal-row">
                <span>TOTAL COSTO DE VENTAS</span>
                <span class="amount" style="color: #f59e0b;">C$ {{ "{:,.2f}".format(fin.costo_ventas) }}</span>
            </div>"""

    est_content = est_content.replace(old_subtotal_costos.replace('\n', '\r\n'), new_subtotal_costos.replace('\n', '\r\n'))
    est_content = est_content.replace(old_subtotal_costos, new_subtotal_costos)

    # Append modals and scripts before {% endblock %}
    if 'id="modalAgregarCuenta"' not in est_content:
        est_content = est_content.replace('{% endblock %}', modal_styles_and_scripts + '\n{% endblock %}')

    with open('templates/contador/estado_resultados.html', 'w', encoding='utf-8') as f:
        f.write(est_content)
    print("templates/contador/estado_resultados.html actualizado exitosamente!")

if __name__ == '__main__':
    update_all()

