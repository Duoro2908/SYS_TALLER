import re

def update_base_html():
    filepath = 'templates/base.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Chart.js to head if not present
    if 'chart.js' not in content.lower():
        content = content.replace('{% block extra_css %}{% endblock %}',
                                  '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n    {% block extra_css %}{% endblock %}')

    # 2. Update Estadistica del Taller and Gerencia headers & links in sidebar
    # Estadistica del Taller module
    old_est = """            {% if session.get('rol_id') in [1, 1009] or 'Estadística' in session.get('rol_nombre', '') or 'Estadistica' in session.get('rol_nombre', '') %}
            <!-- Módulo Estadística del Taller (Superadmin y Administradora de Estadística) -->
            <div class=\"module-header {% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller'] %}active{% endif %}\">
                <div class=\"module-title\">
                    <i class=\"fa-solid fa-chart-line\"></i>
                    <span>Estadística del Taller</span>
                </div>
                <i class=\"fa-solid fa-chevron-down\"></i>
            </div>
            <ul class=\"nav-links submodule-list\" {% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller'] %}style=\"display: block;\"{% endif %}>
                <li>
                    <a href=\"{{ url_for('gerencia.estadisticas') }}\" class=\"{% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller'] %}active{% endif %}\">
                        <i class=\"fa-solid fa-gauge-high\"></i>
                        <span>Panel Estadístico</span>
                    </a>
                </li>
            </ul>
            {% endif %}"""

    new_est = """            {% if session.get('rol_id') in [1, 1009] or 'Estadística' in session.get('rol_nombre', '') or 'Estadistica' in session.get('rol_nombre', '') %}
            <!-- Módulo Estadística del Taller (Superadmin y Administradora de Estadística) -->
            {% set es_taller_act = (request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller'] and request.args.get('origen') != 'gerencia') %}
            <div class=\"module-header {% if es_taller_act %}active{% endif %}\" data-module=\"estadistica_taller\">
                <div class=\"module-title\">
                    <i class=\"fa-solid fa-chart-line\"></i>
                    <span>Estadística del Taller</span>
                </div>
                <i class=\"fa-solid fa-chevron-down\"></i>
            </div>
            <ul class=\"nav-links submodule-list\" {% if es_taller_act %}style=\"display: block;\"{% endif %}>
                <li>
                    <a href=\"{{ url_for('gerencia.estadisticas', origen='taller') }}\" class=\"{% if es_taller_act %}active{% endif %}\">
                        <i class=\"fa-solid fa-gauge-high\"></i>
                        <span>Panel Estadístico</span>
                    </a>
                </li>
            </ul>
            {% endif %}"""

    content = content.replace(old_est, new_est)

    # Gerencia module Panel Estadistico
    old_ger = """            <!-- Módulo Gerencia -->
            {% if session.get('rol_id') in [1, 5] %}
            <div class=\"module-header {% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller', 'gerencia'] and session.get('rol_id') != 1 %}active{% endif %}\">
                <div class=\"module-title\">
                    <i class=\"fa-solid fa-user-tie\"></i>
                    <span>Gerencia</span>
                </div>
                <i class=\"fa-solid fa-chevron-down\"></i>
            </div>
            <ul class=\"nav-links submodule-list\" {% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller', 'gerencia'] and session.get('rol_id') != 1 %}style=\"display: block;\"{% endif %}>
                <li>
                    <a href=\"{{ url_for('gerencia.estadisticas') }}\" class=\"{% if request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller', 'gerencia'] %}active{% endif %}\">
                        <i class=\"fa-solid fa-chart-line\"></i>
                        <span>Panel Estadístico</span>
                    </a>
                </li>"""

    new_ger = """            <!-- Módulo Gerencia -->
            {% if session.get('rol_id') in [1, 5] %}
            {% set es_ger_act = (request.endpoint in ['gerencia.estadisticas', 'estadisticas_taller'] and request.args.get('origen') == 'gerencia') or request.endpoint == 'gerencia' %}
            <div class=\"module-header {% if es_ger_act %}active{% endif %}\" data-module=\"gerencia\">
                <div class=\"module-title\">
                    <i class=\"fa-solid fa-user-tie\"></i>
                    <span>Gerencia</span>
                </div>
                <i class=\"fa-solid fa-chevron-down\"></i>
            </div>
            <ul class=\"nav-links submodule-list\" {% if es_ger_act %}style=\"display: block;\"{% endif %}>
                <li>
                    <a href=\"{{ url_for('gerencia.estadisticas', origen='gerencia') }}\" class=\"{% if es_ger_act %}active{% endif %}\">
                        <i class=\"fa-solid fa-chart-line\"></i>
                        <span>Panel Estadístico</span>
                    </a>
                </li>"""

    content = content.replace(old_ger, new_ger)

    # 3. Update updateSidebarActive function in JS
    old_update_fn = """            function updateSidebarActive(targetUrl) {
                try {
                    const urlObj = new URL(targetUrl, window.location.origin);
                    const targetPath = urlObj.pathname;
                    $('.sidebar .nav-links a').removeClass('active');
                    $('.sidebar .nav-links a').each(function() {
                        const href = $(this).attr('href');
                        if (href) {
                            const linkPath = new URL(href, window.location.origin).pathname;
                            if (linkPath === targetPath) {
                                $(this).addClass('active');
                                const $parentH = $(this).closest('.submodule-list').prev('.module-header');
                                if ($parentH.length) {
                                    $parentH.addClass('active');
                                }
                            }
                        }
                    });
                } catch(e) {}
            }"""

    new_update_fn = """            function updateSidebarActive(targetUrl, $clickedLink) {
                try {
                    const urlObj = new URL(targetUrl, window.location.origin);
                    const targetFull = urlObj.pathname + (urlObj.search || '');
                    
                    $('.sidebar .nav-links a').removeClass('active');
                    $('.sidebar .module-header').removeClass('active');

                    if ($clickedLink && $clickedLink.length) {
                        $clickedLink.addClass('active');
                        const $parentHeader = $clickedLink.closest('.submodule-list').prev('.module-header');
                        if ($parentHeader.length) $parentHeader.addClass('active');
                        return;
                    }

                    // Buscar coincidencia exacta (pathname + query string)
                    let matched = false;
                    $('.sidebar .nav-links a').each(function() {
                        const href = $(this).attr('href');
                        if (href) {
                            const linkObj = new URL(href, window.location.origin);
                            const linkFull = linkObj.pathname + (linkObj.search || '');
                            if (linkFull === targetFull) {
                                $(this).addClass('active');
                                const $parentHeader = $(this).closest('.submodule-list').prev('.module-header');
                                if ($parentHeader.length) $parentHeader.addClass('active');
                                matched = true;
                                return false; // break
                            }
                        }
                    });

                    // Fallback solo pathname si no hubo coincidencia con query
                    if (!matched) {
                        $('.sidebar .nav-links a').each(function() {
                            const href = $(this).attr('href');
                            if (href) {
                                const linkObj = new URL(href, window.location.origin);
                                if (linkObj.pathname === urlObj.pathname) {
                                    $(this).addClass('active');
                                    const $parentHeader = $(this).closest('.submodule-list').prev('.module-header');
                                    if ($parentHeader.length) $parentHeader.addClass('active');
                                    return false; // break
                                }
                            }
                        });
                    }
                } catch(e) {}
            }"""

    content = content.replace(old_update_fn, new_update_fn)

    # 4. In pjaxNavigate, pass clicked element and re-init charts
    old_call = "updateSidebarActive(url);"
    new_call = "updateSidebarActive(url, window._lastPjaxClickedLink || null); window._lastPjaxClickedLink = null;"
    content = content.replace(old_call, new_call)

    old_click = "$('.sidebar').on('click', '.nav-links a', function(e) {"
    new_click = """$('.sidebar').on('click', '.nav-links a', function(e) {
                window._lastPjaxClickedLink = $(this);"""
    content = content.replace(old_click, new_click)

    # Re-init charts after PJAX content swap
    old_init = "if (window.initThemeToggle) window.initThemeToggle();"
    new_init = """if (window.initThemeToggle) window.initThemeToggle();
                    if (window.initEstadisticasCharts) {
                        setTimeout(function() { window.initEstadisticasCharts(); }, 50);
                    }"""
    content = content.replace(old_init, new_init)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/base.html updated successfully!")


def update_styles_css():
    filepath = 'static/css/styles.css'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace blue colors with executive Charcoal / Slate & Warm Amber Gold
    # 1. Nav links active dark
    old_dark_nav = """[data-theme="dark"] .nav-links a.active {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.24) 0%, rgba(37, 99, 235, 0.08) 100%) !important;
  color: #93c5fd !important;
  font-weight: 700 !important;
  border-left: 3.5px solid #3b82f6 !important;
  padding-left: 10px !important;
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.18) !important;
}"""
    new_dark_nav = """[data-theme="dark"] .nav-links a.active {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(245, 158, 11, 0.05) 100%) !important;
  color: #fbbf24 !important;
  font-weight: 700 !important;
  border-left: 3.5px solid #f59e0b !important;
  padding-left: 10px !important;
  box-shadow: 0 2px 10px rgba(245, 158, 11, 0.14) !important;
}"""
    content = content.replace(old_dark_nav, new_dark_nav)

    # 2. Nav links active light
    old_light_nav = """[data-theme="light"] .nav-links a.active {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
  color: #1d4ed8 !important;
  font-weight: 700 !important;
  border-left: 3.5px solid #2563eb !important;
  padding-left: 10px !important;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.14) !important;
}"""
    new_light_nav = """[data-theme="light"] .nav-links a.active {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(245, 158, 11, 0.04) 100%) !important;
  color: #92400e !important;
  font-weight: 700 !important;
  border-left: 3.5px solid #d97706 !important;
  padding-left: 10px !important;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.08) !important;
}"""
    content = content.replace(old_light_nav, new_light_nav)

    # 3. Nav link icons
    content = content.replace(
        '[data-theme="dark"] .nav-links a.active i {\n  color: #60a5fa !important;\n}',
        '[data-theme="dark"] .nav-links a.active i {\n  color: #f59e0b !important;\n}'
    )
    content = content.replace(
        '[data-theme="light"] .nav-links a.active i {\n  color: #2563eb !important;\n}',
        '[data-theme="light"] .nav-links a.active i {\n  color: #d97706 !important;\n}'
    )

    # 4. Module header active dark
    old_dark_mh = """[data-theme="dark"] .module-header.active {
  background: rgba(59, 130, 246, 0.12);
  color: #bfdbfe;
  font-weight: 700;
}"""
    new_dark_mh = """[data-theme="dark"] .module-header.active {
  background: rgba(245, 158, 11, 0.14);
  color: #f8fafc;
  font-weight: 700;
  border: 1px solid rgba(245, 158, 11, 0.32);
}"""
    content = content.replace(old_dark_mh, new_dark_mh)

    # 5. Module header active light: Executive Dark Slate pill with crisp contrast
    old_light_mh = """[data-theme="light"] .module-header.active {
  background: rgba(37, 99, 235, 0.09);
  color: #1d4ed8;
  font-weight: 700;
}"""
    new_light_mh = """[data-theme="light"] .module-header.active {
  background: #0f172a !important;
  color: #ffffff !important;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(15, 23, 42, 0.18);
}"""
    content = content.replace(old_light_mh, new_light_mh)

    # 6. Module header active icons
    content = content.replace(
        '[data-theme="light"] .module-header.active .module-title i {\n  color: #2563eb;\n}',
        '[data-theme="light"] .module-header.active .module-title i {\n  color: #f59e0b !important;\n}\n[data-theme="light"] .module-header.active i.fa-chevron-down {\n  color: #f59e0b !important;\n}'
    )
    content = content.replace(
        '[data-theme="dark"] .module-header.active .module-title i {\n  color: #60a5fa;\n}',
        '[data-theme="dark"] .module-header.active .module-title i {\n  color: #f59e0b !important;\n}\n[data-theme="dark"] .module-header.active i.fa-chevron-down {\n  color: #f59e0b !important;\n}'
    )

    # 7. Progress bar
    content = content.replace(
        'background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa);',
        'background: linear-gradient(90deg, #f59e0b, #d97706, #fbbf24);'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("static/css/styles.css updated successfully!")


if __name__ == '__main__':
    update_base_html()
    update_styles_css()

