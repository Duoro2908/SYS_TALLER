import re

def update_citas_whatsapp():
    filepath = 'templates/atencion/citas_whatsapp.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update page title
    content = content.replace(
        '{% block page_title %}Gestión de Citas WhatsApp ({{ numero_oficial }}){% endblock %}',
        '{% block page_title %}Gestión de Citas WhatsApp (Canal Virtual Taller CR){% endblock %}'
    )

    # 2. Update subtitle
    content = content.replace(
        'Bandeja inteligente de WhatsApp integrada al sistema &bull; Línea oficial: <strong>{{ numero_oficial }}</strong>',
        'Bandeja inteligente de WhatsApp integrada al sistema &bull; Línea oficial: <strong>Canal Virtual Taller CR</strong>'
    )

    # 3. Update top right phone badge
    content = re.sub(
        r'<button\s+type="button"\s+onclick="copiarLineaOficialWA\(\'\{\{\s*numero_oficial\s*\}\}\'\)"\s+class="wa-phone-badge"[\s\S]*?<\/button>',
        '''<div class="wa-phone-badge" style="cursor:default;" title="Canal Virtual Activo del Taller">
            <span class="pulse-dot"></span>
            <span id="badgeLineaOficialWA">Canal Virtual Activo</span>
        </div>''',
        content
    )

    # 4. Update panel connected line
    content = re.sub(
        r'Línea conectada:\s*<strong\s+style="color:\s*#25D366;">\{\{\s*numero_oficial\s*\}\}<\/strong>',
        'Línea conectada: <strong style="color: #25D366;">Canal Virtual Activo</strong>',
        content
    )

    # 5. Remove the WhatsApp Real button
    content = re.sub(
        r'<a\s+href="https:\/\/api\.whatsapp\.com\/send\?phone=\{\{\s*c\.telefono_clean\s*\}\}&text=[^"]*"\s+target="_blank"\s+class="btn-sm-action"[^>]*>[\s\S]*?WhatsApp Real\s*<\/a>',
        '',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/atencion/citas_whatsapp.html updated successfully!")


def update_login_html():
    filepath = 'templates/auth/login.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace placeholder 7732-6738
    content = content.replace('placeholder="Ej: 7732-6738"', 'placeholder="Ej: 8888-8888"')

    # 2. Replace header in WhatsApp live modal
    content = content.replace(
        'Conectado al sistema • +505 7732–6738',
        'Conectado al sistema • Canal Virtual de Atención'
    )
    content = content.replace(
        'Conectado al sistema • +505 7732-6738',
        'Conectado al sistema • Canal Virtual de Atención'
    )

    # 3. Remove window.open WhatsApp redirection in quick actions and appointments
    # First pattern in waLiveQuick
    pattern1 = r'const\s+waUrl\s*=\s*[\'"]https:\/\/api\.whatsapp\.com\/send\?phone=50577326738&text=[\'"]\s*\+\s*encodeURIComponent\(waText\);\s*setTimeout\(\(\)\s*=>\s*\{\s*window\.open\(waUrl,\s*[\'"]_blank[\'"]\);\s*\},\s*\d+\);'
    content = re.sub(pattern1, '// Enlace externo a WhatsApp real desactivado por privacidad\n                    console.log("Mensaje registrado en sistema:", waText);', content)

    # Any remaining occurrences of api.whatsapp.com/send?phone=50577326738
    content = re.sub(r'const\s+waUrl\s*=\s*[\'"]https:\/\/api\.whatsapp\.com\/send\?phone=\d+&text=[\'"]\s*\+\s*encodeURIComponent\([^)]+\);\s*setTimeout\(\(\)\s*=>\s*\{\s*window\.open\([^)]+\);\s*\},\s*\d+\);',
                     '// Notificación interna sin salir a WhatsApp externo', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("templates/auth/login.html updated successfully!")


def update_routes_autenticacion():
    filepath = 'routes/autenticacion.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace(
        '• Línea oficial +505 7732-6738. Puedes trazar tu ruta',
        '• Canal Virtual Taller CR. Puedes trazar tu ruta'
    )
    content = content.replace(
        'de WhatsApp (+505 7732-6738). Un asesor de Atención al Cliente',
        'de Atención al Cliente. Un asesor'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("routes/autenticacion.py updated successfully!")


if __name__ == '__main__':
    update_citas_whatsapp()
    update_login_html()
    update_routes_autenticacion()


def update_db_config():
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath('.'))
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ConfiguracionWhatsApp SET TelefonoNumero = 'Canal Virtual Taller CR'")
            conn.commit()
            conn.close()
            print("Database ConfiguracionWhatsApp updated successfully!")
    except Exception as e:
        print(f"DB update notice: {e}")

if __name__ == '__main__':
    update_db_config()
