from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database import get_db_connection

inventory_bp = Blueprint('inventory', __name__)
inventario_bp = inventory_bp

@inventory_bp.route('/inventario')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    rol = session.get('rol_id')
    # Solo Super Administrador y Gerente tienen acceso
    if rol not in [1, 5]:
        flash("Acceso denegado al módulo de inventario.", "error")
        return redirect(url_for('index'))
        
    productos = []
    categorias = set()
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ProductoID, CodigoSKU, Categoria, Nombre, Descripcion, 
                       PrecioVenta, StockActual, Activo, ImagenURL 
                FROM Productos 
                WHERE Activo = 1
                ORDER BY Nombre ASC
            """)
            
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                productos.append(producto)
                if producto['Categoria']:
                    categorias.add(producto['Categoria'])
        except Exception as e:
            flash(f"Error al cargar el inventario: {e}", "error")
        finally:
            conn.close()
            
    # Ordenar las categorías alfabéticamente
    categorias = sorted(list(categorias))
            
    return render_template('inventory/index.html', productos=productos, categorias=categorias)
