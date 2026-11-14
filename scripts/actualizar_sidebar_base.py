import re

def update_base_html():
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Atención al Cliente
    old_atencion = """            <!-- Módulo Atención al Cliente -->
            {% if session.get('rol_id') in [1, 1008] %}
            <div class="module-header">
                <div class="module-title">
                    <i class="fa-solid fa-headset"></i>
                    <span>Atención al Cliente</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list">"""

    new_atencion = """            <!-- Módulo Atención al Cliente -->
            {% if session.get('rol_id') in [1, 1008] %}
            <div class="module-header {% if request.endpoint and request.endpoint.startswith('atencion.') %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-headset"></i>
                    <span>Atención al Cliente</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint and request.endpoint.startswith('atencion.') %}style="display: block;"{% endif %}>"""

    # 2. Taller
    old_taller = """            <!-- Módulo Taller -->
            {% if session.get('rol_id') in [1, 3] %}
            <div class="module-header">
                <div class="module-title">
                    <i class="fa-solid fa-wrench"></i>
                    <span>Taller</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list">"""

    new_taller = """            <!-- Módulo Taller -->
            {% if session.get('rol_id') in [1, 3] %}
            <div class="module-header {% if request.endpoint and (request.endpoint.startswith('mechanic.') or request.endpoint.startswith('taller.')) %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-wrench"></i>
                    <span>Taller</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint and (request.endpoint.startswith('mechanic.') or request.endpoint.startswith('taller.')) %}style="display: block;"{% endif %}>"""

    # 3. Caja
    old_caja = """            <!-- Módulo Caja y Ventas -->
            {% if session.get('rol_id') in [1, 2] %}
            <div class="module-header">
                <div class="module-title">
                    <i class="fa-solid fa-cash-register"></i>
                    <span>Caja</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list">"""

    new_caja = """            <!-- Módulo Caja y Ventas -->
            {% if session.get('rol_id') in [1, 2] %}
            <div class="module-header {% if request.endpoint and request.endpoint.startswith('cashier.') %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-cash-register"></i>
                    <span>Caja</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint and request.endpoint.startswith('cashier.') %}style="display: block;"{% endif %}>"""

    # 4. RRHH
    old_rrhh = """            <!-- Módulo Recursos Humanos -->
            {% if session.get('rol_id') in [1, 5, 1007] and session.get('username') not in ['carlos.finanzas', 'carlos.contabilidad'] %}
            <div class="module-header">
                <div class="module-title">
                    <i class="fa-solid fa-users-gear"></i>
                    <span>Recursos Humanos</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list">"""

    new_rrhh = """            <!-- Módulo Recursos Humanos -->
            {% if session.get('rol_id') in [1, 5, 1007] and session.get('username') not in ['carlos.finanzas', 'carlos.contabilidad'] %}
            <div class="module-header {% if request.endpoint and (request.endpoint.startswith('planilla.') or 'empleado' in request.endpoint or 'rrhh' in request.endpoint) %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-users-gear"></i>
                    <span>Recursos Humanos</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint and (request.endpoint.startswith('planilla.') or 'empleado' in request.endpoint or 'rrhh' in request.endpoint) %}style="display: block;"{% endif %}>"""

    # 5. Bodega
    old_bodega = """            <!-- Módulo Bodega -->
            {% if session.get('rol_id') in [1, 7] %}
            <div class="module-header">
                <div class="module-title">
                    <i class="fa-solid fa-boxes-stacked"></i>
                    <span>Producción(Bodega)</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list">"""

    new_bodega = """            <!-- Módulo Bodega -->
            {% if session.get('rol_id') in [1, 7] %}
            <div class="module-header {% if request.endpoint and request.endpoint.startswith('bodega.') %}active{% endif %}">
                <div class="module-title">
                    <i class="fa-solid fa-boxes-stacked"></i>
                    <span>Producción(Bodega)</span>
                </div>
                <i class="fa-solid fa-chevron-down"></i>
            </div>
            <ul class="nav-links submodule-list" {% if request.endpoint and request.endpoint.startswith('bodega.') %}style="display: block;"{% endif %}>"""

    # Normalize line endings for replacement
    content = content.replace(old_atencion.replace('\n', '\r\n'), new_atencion.replace('\n', '\r\n'))
    content = content.replace(old_atencion, new_atencion)

    content = content.replace(old_taller.replace('\n', '\r\n'), new_taller.replace('\n', '\r\n'))
    content = content.replace(old_taller, new_taller)

    content = content.replace(old_caja.replace('\n', '\r\n'), new_caja.replace('\n', '\r\n'))
    content = content.replace(old_caja, new_caja)

    content = content.replace(old_rrhh.replace('\n', '\r\n'), new_rrhh.replace('\n', '\r\n'))
    content = content.replace(old_rrhh, new_rrhh)

    content = content.replace(old_bodega.replace('\n', '\r\n'), new_bodega.replace('\n', '\r\n'))
    content = content.replace(old_bodega, new_bodega)

    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/base.html actualizado exitosamente!")

if __name__ == '__main__':
    update_base_html()

