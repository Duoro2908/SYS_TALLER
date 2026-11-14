from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import get_db_connection

mechanic_bp = Blueprint('mechanic', __name__, url_prefix='/mecanico')
mecanico_bp = mechanic_bp

@mechanic_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('mechanic.citas_programadas'))

@mechanic_bp.route('/crear_orden', methods=['POST'])
def crear_orden():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3, 5, 8, 1008]:
        return redirect(url_for('auth.login'))

    next_endpoint = request.form.get('next_endpoint', 'mechanic.citas_programadas')
    if next_endpoint not in ('mechanic.citas_programadas', 'atencion.citas_taller'):
        next_endpoint = 'mechanic.citas_programadas'
        
    moto_id = request.form.get('moto_id')
    mantenimiento_id = request.form.get('mantenimiento_id')
    precio_final = request.form.get('precio_final', type=float, default=0.0)
    
    mecanico_id = session['usuario_id']
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for(next_endpoint))
        
    cursor = conn.cursor()
    try:
        # Pre-validación de repuestos y stock disponible en inventario
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        
        repuestos_validados = []
        for pid_val, cant_val in zip(productos_ids, cantidades):
            if not pid_val or not cant_val:
                continue
            try:
                pid = int(pid_val)
                cant = int(cant_val)
            except (ValueError, TypeError):
                continue
                
            if cant <= 0:
                continue
                
            # Consultar existencias reales en inventario
            cursor.execute("SELECT Nombre, StockActual, Categoria FROM Productos WHERE ProductoID = ?", (pid,))
            prod = cursor.fetchone()
            if not prod:
                flash('⚠️ Uno de los repuestos seleccionados no existe en el catálogo.', 'warning')
                return redirect(url_for(next_endpoint))
                
            nombre_prod, stock_actual, categoria = prod[0], int(prod[1] or 0), prod[2] or 'Repuesto'
            
            # Caso 1: Sin stock disponible (0 unidades)
            if stock_actual <= 0:
                flash(
                    f"⚠️ Sin stock disponible: El repuesto '{nombre_prod}' se encuentra actualmente sin unidades en almacén (Stock: 0). "
                    f"Es necesario agregar nuevo stock de este producto en el módulo de Bodega/Inventario para poder procesar la orden.",
                    "warning"
                )
                return redirect(url_for(next_endpoint))
                
            # Caso 2: Cantidad solicitada excede las existencias
            if cant > stock_actual:
                flash(
                    f"⚠️ Stock insuficiente: Intentaste utilizar {cant} unidad(es) de '{nombre_prod}', pero solo hay {stock_actual} unidad(es) disponible(s) en inventario. "
                    f"Es necesario agregar nuevo stock de este producto en el módulo de Bodega/Inventario antes de procesar esta cantidad.",
                    "warning"
                )
                return redirect(url_for(next_endpoint))
                
            repuestos_validados.append((pid, cant, nombre_prod))
            
        # Obtener el tipo de servicio
        cursor.execute("SELECT Tipo, DescripcionDetallada FROM CatalogoMantenimientos WHERE MantenimientoID = ?", (mantenimiento_id,))
        mantenimiento = cursor.fetchone()
        tipo_servicio = mantenimiento[0] if mantenimiento else 'Preventivo'
        desc = mantenimiento[1] if mantenimiento else 'Mantenimiento de taller'
        
        cita_id = request.form.get('cita_id')
        
        # 1. Crear OrdenTrabajo
        cursor.execute("""
            INSERT INTO OrdenesTrabajo (MotoID, MecanicoID, TipoServicio, Estado, CitaID)
            VALUES (?, ?, ?, 'En Proceso', ?)
        """, (moto_id, mecanico_id, tipo_servicio, cita_id if cita_id else None))
        
        cursor.execute("SELECT @@IDENTITY")
        orden_id = cursor.fetchone()[0]
        
        # 2. Agregar Mano de Obra (el precio del mantenimiento)
        cursor.execute("""
            INSERT INTO OrdenManoObra (OrdenID, DescripcionServicio, CostoSugerido)
            VALUES (?, ?, ?)
        """, (orden_id, f"Mantenimiento {tipo_servicio} - {desc}", precio_final))
        
        # 3. Insertar Repuestos Utilizados ya verificados con stock
        for pid, cant, _ in repuestos_validados:
            cursor.execute("""
                INSERT INTO OrdenRepuestos (OrdenID, ProductoID, Cantidad)
                VALUES (?, ?, ?)
            """, (orden_id, pid, cant))
                
        # 4. Marcar como finalizada / Pendiente de Pago para pasar a caja
        cursor.execute("""
            UPDATE OrdenesTrabajo SET Estado = 'Pendiente de Pago' WHERE OrdenID = ?
        """, (orden_id,))
        
        conn.commit()
        flash('Orden enviada exitosamente a la Caja con sus repuestos.', 'success')
    except Exception as e:
        conn.rollback()
        err_msg = str(e)
        if 'CHK_Prod_Stock' in err_msg or 'StockActual' in err_msg:
            flash(
                "⚠️ Stock insuficiente o no disponible: Uno de los repuestos seleccionados no cuenta con existencias suficientes en almacén. "
                "Es necesario registrar nueva entrada de stock de ese producto en el módulo de Bodega.",
                "warning"
            )
        else:
            flash(
                "⚠️ No se pudo procesar la orden de trabajo. Por favor revise los datos ingresados o contacte al supervisor de taller.",
                "error"
            )
    finally:
        conn.close()
        
    return redirect(url_for(next_endpoint))

@mechanic_bp.route('/ordenes')
def ordenes_list():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3, 5]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('mechanic.index'))
        
    cursor = conn.cursor()
    
    # Obtener todas las órdenes del día agrupadas por fecha (convertida a date para agrupar)
    cursor.execute("""
        SELECT 
            o.OrdenID,
            c.NombreCompleto,
            m.Placa,
            o.TipoServicio,
            o.Estado,
            o.FechaIngreso,
            (SELECT ISNULL(SUM(CostoSugerido), 0) FROM OrdenManoObra WHERE OrdenID = o.OrdenID) +
            (SELECT ISNULL(SUM(r.Cantidad * p.PrecioVenta), 0) FROM OrdenRepuestos r JOIN Productos p ON r.ProductoID = p.ProductoID WHERE r.OrdenID = o.OrdenID) as TotalGeneral,
            CAST(o.FechaIngreso AS DATE) as FechaFiltro,
            (SELECT TOP 1 Estado FROM ControlCaja WHERE CAST(FechaApertura AS DATE) = CAST(o.FechaIngreso AS DATE) ORDER BY CajaID DESC) as EstadoCaja,
            (SELECT COUNT(*) FROM ControlCaja WHERE CAST(FechaApertura AS DATE) = CAST(o.FechaIngreso AS DATE)) as Aperturas
        FROM OrdenesTrabajo o
        JOIN Motocicletas m ON o.MotoID = m.MotoID
        JOIN Clientes c ON m.ClienteID = c.ClienteID
        ORDER BY o.FechaIngreso DESC
    """)
    
    ordenes_raw = cursor.fetchall()
    conn.close()
    
    # Agrupar por fecha en un diccionario { 'YYYY-MM-DD': [ordenes] }
    ordenes_por_dia = {}
    estado_caja_por_dia = {}
    
    for o in ordenes_raw:
        fecha_str = o[7].strftime('%Y-%m-%d')
        if fecha_str not in ordenes_por_dia:
            ordenes_por_dia[fecha_str] = []
            
            estado_caja_raw = o[8] or 'Abierta'
            aperturas = o[9] or 1
            if estado_caja_raw == 'Abierta':
                if aperturas > 1:
                    estado_caja_por_dia[fecha_str] = 'Abierta (Emergencia)'
                else:
                    estado_caja_por_dia[fecha_str] = 'Abierta'
            else:
                estado_caja_por_dia[fecha_str] = 'Cerrada'
            
        ordenes_por_dia[fecha_str].append({
            'id': o[0],
            'cliente': o[1],
            'placa': o[2],
            'tipo': o[3],
            'estado': o[4],
            'fecha': o[5].strftime('%I:%M %p'),
            'total': float(o[6] or 0)
        })
        
    return render_template('mecanico/ordenes_list.html', ordenes_por_dia=ordenes_por_dia, estado_caja_por_dia=estado_caja_por_dia)

@mechanic_bp.route('/eliminar_orden/<int:orden_id>', methods=['POST'])
def eliminar_orden(orden_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3, 5, 8, 1008]:
        flash("Acceso denegado.", "error")
        return redirect(url_for('mechanic.ordenes_list'))
        
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('mechanic.ordenes_list'))
        
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Estado FROM OrdenesTrabajo WHERE OrdenID = ?", (orden_id,))
        orden = cursor.fetchone()
        if not orden:
            flash("La orden no existe o ya fue eliminada.", "warning")
            return redirect(url_for('mechanic.ordenes_list'))
            
        cursor.execute("SELECT COUNT(*) FROM Facturas WHERE OrdenID = ?", (orden_id,))
        if cursor.fetchone()[0] > 0:
            flash("No se puede eliminar una orden que ya tiene factura emitida.", "warning")
            return redirect(url_for('mechanic.ordenes_list'))
            
        cursor.execute("DELETE FROM OrdenRepuestos WHERE OrdenID = ?", (orden_id,))
        cursor.execute("DELETE FROM OrdenManoObra WHERE OrdenID = ?", (orden_id,))
        cursor.execute("DELETE FROM OrdenesTrabajo WHERE OrdenID = ?", (orden_id,))
        conn.commit()
        flash(f"Orden ORD-{orden_id:04d} eliminada exitosamente del sistema.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar la orden: {str(e)}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('mechanic.ordenes_list'))

@mechanic_bp.route('/cerrar_caja_dia/<fecha>', methods=['POST'])
def cerrar_caja_dia(fecha):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3, 5]:
        flash("Acceso denegado.", "error")
        return redirect(url_for('mechanic.ordenes_list'))
        
    conn = get_db_connection()
    if not conn:
        flash("Error de base de datos.", "error")
        return redirect(url_for('mechanic.ordenes_list'))
        
    cursor = conn.cursor()
    try:
        # Cerrar cajas de ese día
        cursor.execute("""
            UPDATE ControlCaja 
            SET Estado = 'Cerrada', FechaCierre = GETDATE()
            WHERE CAST(FechaApertura AS DATE) = ? AND Estado = 'Abierta'
        """, (fecha,))
        
        # Si no había caja explícita, podríamos crear un registro fantasma o simplemente 
        # el update anterior ya marca la intención. Pero para reportes del gerente, 
        # las órdenes de venta y trabajo del día ya quedarán fijadas.
        conn.commit()
        flash(f"Corte del día {fecha} realizado. Órdenes enviadas al Gerente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al cerrar la caja del día: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('mechanic.ordenes_list'))

def obtener_datos_citas_programadas(conn, rol_id, usuario_id):
    """Retorna (citas, mantenimientos, productos) para el panel unificado de Citas Programadas."""
    cursor = conn.cursor()
    if rol_id == 3:
        cursor.execute("""
            SELECT cw.CitaID, cw.ClienteID, c.NombreCompleto, c.Telefono, 
                   cw.MotoID, m.Marca, m.Modelo, m.Placa, cw.FechaProgramada, 
                   cw.TipoMantenimiento, cw.Estado, cw.Origen
            FROM CitasWhatsApp cw
            JOIN Clientes c ON cw.ClienteID = c.ClienteID
            JOIN Motocicletas m ON cw.MotoID = m.MotoID
            WHERE cw.MecanicoAsignadoID = ? AND cw.Estado = 'Confirmada'
              AND CAST(cw.FechaProgramada AS DATE) >= CAST(GETDATE() - 1 AS DATE)
              AND NOT EXISTS (SELECT 1 FROM OrdenesTrabajo ot WHERE ot.CitaID = cw.CitaID)
            ORDER BY cw.FechaProgramada ASC
        """, (usuario_id,))
    else:
        cursor.execute("""
            SELECT cw.CitaID, cw.ClienteID, c.NombreCompleto, c.Telefono, 
                   cw.MotoID, m.Marca, m.Modelo, m.Placa, cw.FechaProgramada, 
                   cw.TipoMantenimiento, cw.Estado, cw.Origen
            FROM CitasWhatsApp cw
            JOIN Clientes c ON cw.ClienteID = c.ClienteID
            JOIN Motocicletas m ON cw.MotoID = m.MotoID
            WHERE cw.Estado = 'Confirmada'
              AND CAST(cw.FechaProgramada AS DATE) >= CAST(GETDATE() - 1 AS DATE)
              AND NOT EXISTS (SELECT 1 FROM OrdenesTrabajo ot WHERE ot.CitaID = cw.CitaID)
            ORDER BY cw.FechaProgramada ASC
        """)

    citas = cursor.fetchall()

    cursor.execute("SELECT MantenimientoID, Tipo, PrecioBase, DescripcionDetallada FROM CatalogoMantenimientos")
    mantenimientos = cursor.fetchall()

    cursor.execute("""
        SELECT ProductoID, Nombre, Categoria, TipoMoto, StockActual, PrecioVenta 
        FROM Productos 
        WHERE Activo = 1
        ORDER BY CASE WHEN StockActual > 0 THEN 0 ELSE 1 END, Nombre ASC
    """)
    productos = cursor.fetchall()
    return citas, mantenimientos, productos


@mechanic_bp.route('/citas_programadas', methods=['GET'])
def citas_programadas():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 3]:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('mechanic.index'))
        
    citas, mantenimientos, productos = obtener_datos_citas_programadas(
        conn, session.get('rol_id'), session.get('usuario_id')
    )
    conn.close()
    
    return render_template(
        'mecanico/citas_programadas.html',
        citas=citas,
        mantenimientos=mantenimientos,
        productos=productos,
        next_endpoint='mechanic.citas_programadas',
    )
