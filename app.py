"""
====================================================================
TALLER Y LUBRICANTES CR - SISTEMA DE GESTIÓN INTEGRAL
Punto de Entrada Principal y Orquestador de Módulos (Flask Application)
====================================================================
Este archivo es el orquestador central del backend.
Inicializa la aplicación, conecta la configuración y registra los 
11 módulos (Blueprints) que componen la lógica de negocio del taller.
====================================================================
"""

from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify, send_from_directory
from config import Config
from database import get_db_connection, ensure_schema_migrations

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)
ensure_schema_migrations()

# ====================================================================
# 1. IMPORTACIÓN Y REGISTRO DE MÓDULOS DEL SISTEMA (BLUEPRINTS)
# ====================================================================
from routes.autenticacion import auth_bp
from routes.caja import cashier_bp
from routes.mecanico import mechanic_bp
from routes.bodega import bodega_bp
from routes.atencion import atencion_bp
from routes.contador import contador_bp
from routes.planilla import planilla_bp
from routes.mercadotecnia import mercadotecnia_bp
from routes.configuracion import settings_bp
from routes.inventario import inventory_bp
from routes.estadisticas import estadisticas_bp, gerencia_bp

# Conectar cada módulo independiente a la aplicación central
app.register_blueprint(auth_bp)
app.register_blueprint(cashier_bp)
app.register_blueprint(mechanic_bp)
app.register_blueprint(bodega_bp)
app.register_blueprint(atencion_bp)
app.register_blueprint(contador_bp)
app.register_blueprint(planilla_bp)
app.register_blueprint(mercadotecnia_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(estadisticas_bp)


# ====================================================================
# 2. ENRUTAMIENTO INICIAL POR ROLES DE USUARIO (ROUTING RBAC)
# ====================================================================
@app.route('/')
def index():
    """Redirige al usuario a su panel correspondiente según su rol al iniciar sesión."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    rol = session.get('rol_id')
    
    # 1: Super Administrador (Panel general del sistema)
    if rol == 1:
        from database import get_db_connection
        conn = get_db_connection()
        stats = {'usuarios': 0, 'productos': 0, 'ordenes': 0, 'proveedores': 0}
        if conn:
            cursor = conn.cursor()
            # 10 Colaboradores activos del taller (excluye al creador/admin técnico y duplicados)
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Activo = 1 AND UsuarioID != 1 AND Email NOT IN ('carlos.contabilidad', 'elvin.admin')")
            stats['usuarios'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Productos")
            stats['productos'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo")
            stats['ordenes'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Proveedores")
            stats['proveedores'] = cursor.fetchone()[0]
            conn.close()
        return render_template('dashboard/superadmin.html', stats=stats)
        
    # 5: Gerente General (Analítica ejecutiva)
    elif rol == 5:
        return redirect(url_for('gerencia.estadisticas'))
        
    # 2: Caja y Facturación
    elif rol == 2:
        return redirect(url_for('cashier.index'))
        
    # 3: Taller Mecánico
    elif rol == 3:
        return redirect(url_for('mechanic.index'))
        
    # Finanzas y Tesorería (Carlos René)
    elif session.get('username') == 'carlos.finanzas':
        return redirect(url_for('contador.resumen_finanzas'))
        
    # Contabilidad General (Carlos René)
    elif session.get('username') == 'carlos.contabilidad':
        return redirect(url_for('contador.balance'))
        
    # 4 o 6: Contador General
    elif rol in (4, 6) or 'Contador' in session.get('rol_nombre', ''):
        return redirect(url_for('contador.index'))
        
    # 7: Bodega y Abastecimiento
    elif rol == 7:
        return redirect(url_for('bodega.inventario'))
        
    # 1008: Atención al Cliente y CRM WhatsApp
    elif rol == 1008:
        return redirect(url_for('atencion.index'))
        
    # 1007: Recursos Humanos y Nómina Legal
    elif rol == 1007:
        return redirect(url_for('planilla.index'))
        
    # 1009: Administradora de Estadísticas (Martha Jovana)
    elif rol == 1009 or 'Estadística' in session.get('rol_nombre', '') or 'Estadistica' in session.get('rol_nombre', ''):
        return redirect(url_for('gerencia.estadisticas'))
        
    # 1010: Mercadotecnia y Rifas (Carlos Huete)
    elif session.get('username') == 'carlos.merca' or rol == 1010 or 'Mercadotecnia' in session.get('rol_nombre', ''):
        return redirect(url_for('mercadotecnia.resumen'))
        
    # Cualquier otro caso
    else:
        return redirect(url_for('auth.login'))





@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    if not session.get('user_id'):
        return jsonify({'error': 'No autorizado'}), 401
    
    from database import get_db_connection
    import datetime
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a base de datos'}), 500

    try:
        cursor = conn.cursor()
        # 10 Colaboradores de nómina y operaciones
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Activo = 1 AND UsuarioID != 1 AND Email NOT IN ('carlos.contabilidad', 'elvin.admin')")
        usuarios = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE Activo = 1")
        productos = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo")
        ordenes = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM Proveedores")
        proveedores = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM CitasWhatsApp WHERE Estado IN ('Pendiente', 'Confirmada')")
        citas_activas = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE Estado IN ('En Proceso', 'Pendiente')")
        ordenes_activas = cursor.fetchone()[0] or 0
        conn.close()

        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'productos': productos,
            'ordenes': ordenes,
            'proveedores': proveedores,
            'citas_activas': citas_activas,
            'ordenes_activas': ordenes_activas,
            'timestamp': datetime.datetime.now().strftime('%I:%M:%S %p')
        })
        # @app.route('/integrantes')
#def integrantes():
    #conn = get_db_connection()
    #filas = conn.cursor().execute("SELECT Nombre FROM Integrantes").fetchall()
    #conn.close()
    #return render_template('integrantes.html', integrantes=filas)
    
    
    except Exception as e:
        
        #{% extends 'base.html' %}
#{% block content %}
#<h2>Integrantes</h2>
#{% for i in integrantes %}
   # <p>{{ i[0] }}</p>
#{% endfor %}
#{% endblock %}



        conn.close()
        return jsonify({'error': str(e)}), 500
    

    
    

    
    




















@app.route('/descargar-manual')
@app.route('/manual')
def descargar_manual():
    """Permite descargar directamente el Manual de Usuario en formato Word."""
    return send_from_directory('static/docs', 'Manual_de_Usuario_Taller_CR.docx', as_attachment=True, download_name='Manual_de_Usuario_Taller_CR.docx')

# ====================================================================
# 3. ARRANQUE DEL SERVIDOR
# ====================================================================
if __name__ == '__main__':
    app.run(debug=True)
