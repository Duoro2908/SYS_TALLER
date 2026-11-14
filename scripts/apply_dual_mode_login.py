import re

login_path = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\auth\login.html"
with open(login_path, "r", encoding="utf-8") as f:
    text = f.read()

# CSS to add for dual mode
css_addition = """
        /* Estilos Modo Cliente vs Acceso Personal */
        .staff-toggle-wrapper {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px dashed rgba(255, 255, 255, 0.12);
            text-align: center;
        }

        .btn-staff-toggle {
            background: rgba(242, 192, 41, 0.08);
            border: 1px solid rgba(242, 192, 41, 0.25);
            color: var(--primary);
            padding: 10px 18px;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: inherit;
        }

        .btn-staff-toggle:hover {
            background: rgba(242, 192, 41, 0.18);
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(242, 192, 41, 0.2);
        }

        .btn-client-back {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #cbd5e1;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 16px;
            font-family: inherit;
        }

        .btn-client-back:hover {
            background: rgba(255, 255, 255, 0.12);
            color: #ffffff;
        }

        .client-service-grid {
            display: flex;
            flex-direction: column;
            gap: 11px;
            margin-top: 14px;
        }

        .client-service-card {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            text-decoration: none;
            color: inherit;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .client-service-card:hover {
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(242, 192, 41, 0.35);
            transform: translateX(4px);
        }

        .client-card-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }

        .client-card-info h4 {
            font-size: 0.96rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 3px;
        }

        .client-card-info p {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin: 0;
            line-height: 1.3;
        }

        .client-card-arrow {
            margin-left: auto;
            color: var(--text-muted);
            font-size: 0.85rem;
            transition: transform 0.2s ease;
        }

        .client-service-card:hover .client-card-arrow {
            color: var(--primary);
            transform: translateX(3px);
        }
"""

# Insert CSS before </style>
if "/* Estilos Modo Cliente vs Acceso Personal */" not in text:
    text = text.replace("</style>", css_addition + "\n    </style>")

# Find card-right in html
card_right_target = """        <!-- Lado Derecho (Formulario) -->
        <div class="card-right">"""

new_card_right_content = """        <!-- Lado Derecho (Dual: Portal Cliente por Defecto / Acceso Personal) -->
        <div class="card-right">
            
            <!-- VISTA 1: MODO CLIENTE PÚBLICO (Por Defecto) -->
            <div id="clientPortalView">
                <div class="form-header">
                    <h2>Portal de Clientes & Servicios</h2>
                    <p>Atención al público, repuestos certificados y citas de taller</p>
                </div>

                <div class="client-service-grid">
                    <!-- 1. Tienda / Catálogo de Repuestos -->
                    <a href="{{ url_for('cashier.pos_publico') }}" class="client-service-card">
                        <div class="client-card-icon" style="background: rgba(242, 192, 41, 0.12); color: #f2c029; border: 1px solid rgba(242, 192, 41, 0.25);">
                            <i class="fa-solid fa-store"></i>
                        </div>
                        <div class="client-card-info">
                            <h4>Catálogo & Tienda de Repuestos</h4>
                            <p>Filtros Génesis (KA, SX, CR4), aceites Motul y bujías en stock</p>
                        </div>
                        <i class="fa-solid fa-chevron-right client-card-arrow"></i>
                    </a>

                    <!-- 2. Agendar Cita de Mantenimiento -->
                    <a href="{{ url_for('auth.agendar_cita') }}" class="client-service-card">
                        <div class="client-card-icon" style="background: rgba(33, 150, 243, 0.12); color: #2196f3; border: 1px solid rgba(33, 150, 243, 0.25);">
                            <i class="fa-solid fa-calendar-check"></i>
                        </div>
                        <div class="client-card-info">
                            <h4>Agendar Cita de Taller</h4>
                            <p>Programa mantenimiento preventivo, afinado o cambio de aceite</p>
                        </div>
                        <i class="fa-solid fa-chevron-right client-card-arrow"></i>
                    </a>

                    <!-- 3. Buzón de Sugerencias y Quejas -->
                    <a href="javascript:void(0)" onclick="document.getElementById('quejasModal').style.display='flex'" class="client-service-card">
                        <div class="client-card-icon" style="background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.25);">
                            <i class="fa-solid fa-bullhorn"></i>
                        </div>
                        <div class="client-card-info">
                            <h4>Buzón Directo a Gerencia</h4>
                            <p>Reporta tu experiencia o envía sugerencias al Gerente General</p>
                        </div>
                        <i class="fa-solid fa-chevron-right client-card-arrow"></i>
                    </a>

                    <!-- 4. Contacto WhatsApp Inmediato -->
                    <a href="https://wa.me/50588888888?text=Hola%20Taller%20CR,%20deseo%20información%20sobre%20repuestos%20y%20servicios" target="_blank" class="client-service-card">
                        <div class="client-card-icon" style="background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25);">
                            <i class="fa-brands fa-whatsapp"></i>
                        </div>
                        <div class="client-card-info">
                            <h4>Atención WhatsApp Inmediata</h4>
                            <p>Consulta directa con mecánicos certificados en Managua</p>
                        </div>
                        <i class="fa-solid fa-arrow-up-right-from-square client-card-arrow" style="font-size: 0.8rem;"></i>
                    </a>
                </div>

                <!-- Botón Discreto para Empleados / Colaboradores -->
                <div class="staff-toggle-wrapper">
                    <button type="button" class="btn-staff-toggle" onclick="toggleStaffLogin(true)">
                        <i class="fa-solid fa-user-lock"></i> Acceso Personal del Taller
                    </button>
                </div>
            </div>

            <!-- VISTA 2: FORMULARIO DE INICIO DE SESIÓN PARA EMPLEADOS (Oculto para Clientes) -->
            <div id="staffLoginFormView" style="display: none;">
                <button type="button" class="btn-client-back" onclick="toggleStaffLogin(false)">
                    <i class="fa-solid fa-arrow-left"></i> Volver a Portal Clientes
                </button>

                <div class="form-header" style="margin-top: 5px;">
                    <h2>Acceso Restringido</h2>
                    <p>Portal de Gestión Operativa para Colaboradores</p>
                </div>

                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        <ul class="flash-messages">
                            {% for category, message in messages %}
                                <li class="flash-{{ category }}">
                                    <i class="fa-solid fa-circle-exclamation"></i>
                                    {{ message }}
                                </li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                {% endwith %}

                <form action="{{ url_for('auth.login') }}" method="POST">
                    <div class="input-group">
                        <input type="text" id="email" name="email" required autocomplete="off">
                        <label>ID de Empleado / Usuario</label>
                    </div>
                    
                    <div class="input-group">
                        <input type="password" id="password" name="password" required>
                        <label>Clave de Autorización</label>
                        <i class="fa-solid fa-eye input-icon-right" onclick="togglePassword()" id="eye-icon"></i>
                    </div>
                    
                    <button type="submit" class="btn-login">
                        Ingresar al Sistema
                        <i class="fa-solid fa-chevron-right"></i>
                    </button>
                </form>
            </div>"""

# Replace the card-right block
regex_card_right = r'<div class="card-right">[\s\S]*?<div class="footer-rights">'
replacement = new_card_right_content + """
            
            <div class="footer-rights">"""

if re.search(regex_card_right, text):
    text = re.sub(regex_card_right, replacement, text)
    print("Replaced card-right successfully!")
else:
    print("Regex match failed for card-right")

# Add toggleStaffLogin JS function
js_toggle = """
        // ========================================================
        // CONTROL MODO CLIENTE vs ACCESO PERSONAL (EMPLEADOS)
        // ========================================================
        function toggleStaffLogin(showStaff) {
            const clientView = document.getElementById('clientPortalView');
            const staffView = document.getElementById('staffLoginFormView');
            if (!clientView || !staffView) return;

            if (showStaff) {
                clientView.style.display = 'none';
                staffView.style.display = 'block';
                const emailInput = document.getElementById('email');
                if (emailInput) setTimeout(() => emailInput.focus(), 150);
            } else {
                staffView.style.display = 'none';
                clientView.style.display = 'block';
            }
        }

        // Si hay mensajes de error o la URL contiene ?staff=1 o #staff, mostrar login directo
        document.addEventListener('DOMContentLoaded', function() {
            const hasFlashErrors = document.querySelector('.flash-messages');
            const urlParams = new URLSearchParams(window.location.search);
            const isStaffParam = urlParams.get('staff') === '1' || window.location.hash === '#staff';
            if (hasFlashErrors || isStaffParam) {
                toggleStaffLogin(true);
            }
        });
"""

if "function toggleStaffLogin" not in text:
    text = text.replace("</script>", js_toggle + "\n    </script>")
    print("Added toggleStaffLogin script!")

with open(login_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated login.html successfully!")

