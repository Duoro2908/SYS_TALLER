from flask import Blueprint, render_template, render_template_string, request, session, redirect, url_for, flash, jsonify
import datetime
from database import get_db_connection
from config import Config
from whatsapp_bot import process_incoming_whatsapp_message, OFFICIAL_PHONE_NUMBER

cashier_bp = Blueprint('cashier', __name__, url_prefix='/caja')
caja_bp = cashier_bp

@cashier_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('cashier.ventas_recibidas'))

@cashier_bp.route('/ordenes_taller', methods=['GET'])
def ordenes_taller():
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))
        
    cursor = conn.cursor()
    # Traer órdenes pendientes de pago enviadas por los mecánicos
    cursor.execute("""
        SELECT o.OrdenID, c.NombreCompleto, m.Modelo, m.Cilindraje, o.TipoServicio, 
               ISNULL((SELECT SUM(CostoSugerido) FROM OrdenManoObra WHERE OrdenID = o.OrdenID), 0) + 
               ISNULL((SELECT SUM(r.Cantidad * p.PrecioVenta) FROM OrdenRepuestos r JOIN Productos p ON r.ProductoID = p.ProductoID WHERE r.OrdenID = o.OrdenID), 0) as TotalGeneral
        FROM OrdenesTrabajo o
        JOIN Motocicletas m ON o.MotoID = m.MotoID
        JOIN Clientes c ON m.ClienteID = c.ClienteID
        WHERE o.Estado = 'Pendiente de Pago'
        ORDER BY o.FechaIngreso DESC
    """)
    ordenes_pendientes = cursor.fetchall()
    
    # Obtener el CajaID abierta actual
    cursor.execute("SELECT CajaID, MontoInicial FROM ControlCaja WHERE Estado = 'Abierta'")
    caja_abierta = cursor.fetchone()
    
    conn.close()
    
    return render_template('caja/index.html', ordenes=ordenes_pendientes, caja_abierta=caja_abierta)

@cashier_bp.route('/facturar/<int:orden_id>', methods=['POST'])
def facturar(orden_id):
        
    metodo_pago = request.form.get('metodo_pago', 'Efectivo')
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('cashier.index'))
        
    cursor = conn.cursor()
    try:
        # Verificar caja abierta
        cursor.execute("SELECT CajaID FROM ControlCaja WHERE Estado = 'Abierta'")
        caja = cursor.fetchone()
        if not caja:
            flash('Debes abrir una caja primero.', 'error')
            return redirect(url_for('cashier.index'))
            
        caja_id = caja[0]
        
        # Obtener total de la orden (Mano de obra + Repuestos)
        cursor.execute("SELECT ISNULL(SUM(CostoSugerido), 0) FROM OrdenManoObra WHERE OrdenID = ?", (orden_id,))
        total_mano_obra = float(cursor.fetchone()[0] or 0)
        
        cursor.execute("""
            SELECT ISNULL(SUM(r.Cantidad * p.PrecioVenta), 0)
            FROM OrdenRepuestos r
            JOIN Productos p ON r.ProductoID = p.ProductoID
            WHERE r.OrdenID = ?
        """, (orden_id,))
        total_repuestos = float(cursor.fetchone()[0] or 0)
        
        total_neto = round(total_mano_obra + total_repuestos, 2)
        
        # Calcular impuestos (asumiendo 15% IVA ya incluido en precio al consumidor)
        subtotal = round(total_neto / 1.15, 2) if total_neto > 0 else 0
        iva = round(total_neto - subtotal, 2)
        
        # Insertar Factura
        import uuid
        numero_factura = str(uuid.uuid4())[:8].upper()
        
        # Buscar ClienteID asociado a la motocicleta de la orden
        cursor.execute("""
            SELECT m.ClienteID 
            FROM OrdenesTrabajo ot 
            JOIN Motocicletas m ON ot.MotoID = m.MotoID 
            WHERE ot.OrdenID = ?
        """, (orden_id,))
        row_cli = cursor.fetchone()
        cliente_id_orden = row_cli[0] if row_cli and row_cli[0] else None

        cursor.execute("""
            SET NOCOUNT ON;
            INSERT INTO Facturas (CajaID, NumeroFactura, OrdenID, ClienteID, SubTotal, TotalIVA, ImpuestoDGI, TotalNeto, MetodoPago, RUC_Emisor)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?);
            SELECT SCOPE_IDENTITY();
        """, (caja_id, numero_factura, orden_id, cliente_id_orden, subtotal, iva, total_neto, metodo_pago, Config.COMPANY_RUC))
        
        factura_id = cursor.fetchone()[0]
        
        # Insertar Repuestos como DetalleFactura
        cursor.execute("""
            SELECT r.ProductoID, r.Cantidad, p.PrecioVenta, p.Nombre 
            FROM OrdenRepuestos r
            JOIN Productos p ON r.ProductoID = p.ProductoID
            WHERE r.OrdenID = ?
        """, (orden_id,))
        repuestos = cursor.fetchall()
        for r in repuestos:
            cursor.execute("""
                INSERT INTO DetalleFactura (FacturaID, ProductoID, Descripcion, Cantidad, PrecioVentaAplicado)
                VALUES (?, ?, ?, ?, ?)
            """, (factura_id, r[0], r[3], r[1], r[2]))
        
        # Insertar Mano de Obra como DetalleFactura
        cursor.execute("""
            SELECT DescripcionServicio, CostoSugerido 
            FROM OrdenManoObra 
            WHERE OrdenID = ?
        """, (orden_id,))
        mano_obra_items = cursor.fetchall()
        for mo in mano_obra_items:
            desc_servicio = f"{mo[0]} (Mano de Obra)"
            cursor.execute("""
                INSERT INTO DetalleFactura (FacturaID, ProductoID, Descripcion, Cantidad, PrecioVentaAplicado)
                VALUES (?, NULL, ?, 1, ?)
            """, (factura_id, desc_servicio, mo[1]))
        
        # Actualizar estado de la orden
        cursor.execute("UPDATE OrdenesTrabajo SET Estado = 'Facturada' WHERE OrdenID = ?", (orden_id,))
        
        conn.commit()
        flash(f'Orden #{orden_id} facturada exitosamente. Recibo: {numero_factura}', 'success')
        return redirect(url_for('cashier.factura_digital', factura_id=factura_id))
    except Exception as e:
        conn.rollback()
        flash(f'Error al facturar: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('cashier.index'))

@cashier_bp.route('/emision_factura', methods=['GET', 'POST'])
def emision_factura():
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('cashier.index'))
        
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Procesar Venta Directa
        cliente_id_str = request.form.get('cliente_id')
        nombre_paso = request.form.get('nombre_paso')
        ruc_paso = request.form.get('ruc_paso')
        metodo_pago = request.form.get('metodo_pago', 'Efectivo')
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        
        if not productos_ids:
            flash('Debes agregar al menos un producto a la factura.', 'error')
            conn.close()
            return redirect(url_for('cashier.emision_factura'))
            
        try:
            cursor.execute("SELECT CajaID FROM ControlCaja WHERE Estado = 'Abierta'")
            caja = cursor.fetchone()
            if not caja:
                flash('Debes abrir una caja primero.', 'error')
                conn.close()
                return redirect(url_for('cashier.index'))
                
            caja_id = caja[0]
            
            # Calcular subtotales
            subtotal_bruto = 0
            for cant, prec in zip(cantidades, precios):
                subtotal_bruto += int(cant) * float(prec)
                
            cliente_id = int(cliente_id_str) if cliente_id_str else None
            
            # Check if top 5
            descuento_top5 = 0
            if cliente_id:
                cursor.execute("""
                    SELECT TOP 5 C.ClienteID
                    FROM Clientes C
                    ORDER BY (
                        SELECT COUNT(F.FacturaID) 
                        FROM Facturas F 
                        WHERE F.ClienteID = C.ClienteID OR 
                              F.OrdenID IN (SELECT OrdenID FROM OrdenesTrabajo O JOIN Motocicletas M ON O.MotoID = M.MotoID WHERE M.ClienteID = C.ClienteID)
                    ) DESC, C.ClienteID DESC
                """)
                top_5 = [row[0] for row in cursor.fetchall()]
                if cliente_id in top_5:
                    descuento_top5 = subtotal_bruto * 0.01 # 1% discount
            
            # Manual Discount
            descuento_manual_pct = request.form.get('descuento_manual', 0)
            try:
                descuento_manual_pct = float(descuento_manual_pct)
            except:
                descuento_manual_pct = 0.0
                
            if descuento_manual_pct > 20:
                descuento_manual_pct = 20.0
            elif descuento_manual_pct < 0:
                descuento_manual_pct = 0.0
                
            descuento_manual_monto = subtotal_bruto * (descuento_manual_pct / 100.0)
            
            descuento = descuento_top5 + descuento_manual_monto
            
            neto_despues_desc = round(subtotal_bruto - descuento, 2)
            subtotal = round(neto_despues_desc / 1.15, 2)
            iva = round(neto_despues_desc - subtotal, 2)
            total_neto = neto_despues_desc
            
            import uuid
            numero_factura = 'VD-' + str(uuid.uuid4())[:6].upper()
            
            cursor.execute("""
                SET NOCOUNT ON;
                INSERT INTO Facturas (CajaID, NumeroFactura, ClienteID, NombreClienteDePaso, SubTotal, TotalIVA, ImpuestoDGI, TotalNeto, MetodoPago, DescuentoAplicado, RUC_Emisor, RUCCliente)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?);
                SELECT SCOPE_IDENTITY();
            """, (caja_id, numero_factura, cliente_id, nombre_paso, subtotal, iva, total_neto, metodo_pago, descuento, Config.COMPANY_RUC, ruc_paso))
            
            factura_id = cursor.fetchone()[0]
            
            # Insert Details
            for pid, cant, prec in zip(productos_ids, cantidades, precios):
                cursor.execute("""
                    SELECT Nombre FROM Productos WHERE ProductoID = ?
                """, (pid,))
                prod_nombre = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO DetalleFactura (FacturaID, ProductoID, Descripcion, Cantidad, PrecioVentaAplicado)
                    VALUES (?, ?, ?, ?, ?)
                """, (factura_id, pid, prod_nombre, cant, prec))
                
            conn.commit()
            flash(f'Factura emitida exitosamente: {numero_factura}', 'success')
            return redirect(url_for('cashier.factura_digital', factura_id=factura_id))
            
        except Exception as e:
            conn.rollback()
            err_msg = str(e)
            if 'CHK_Prod_Stock' in err_msg or 'StockActual' in err_msg:
                flash('⚠️ Stock insuficiente o no disponible: Uno de los productos no cuenta con existencias suficientes en almacén. Es necesario agregar nuevo stock en Bodega.', 'warning')
            else:
                flash('⚠️ No se pudo emitir la factura. Por favor verifique los datos del comprobante.', 'error')
        finally:
            conn.close()
            
        return redirect(url_for('cashier.emision_factura'))

    else:
        # GET form
        cursor.execute("SELECT ProductoID, CodigoSKU, Nombre, PrecioVenta, StockActual FROM Productos WHERE StockActual > 0 AND Activo = 1")
        productos = cursor.fetchall()
        
        cursor.execute("""
            SELECT C.ClienteID, C.NombreCompleto, C.Telefono,
                   (SELECT COUNT(F.FacturaID) 
                    FROM Facturas F 
                    WHERE F.ClienteID = C.ClienteID OR 
                          F.OrdenID IN (SELECT OrdenID FROM OrdenesTrabajo O JOIN Motocicletas M ON O.MotoID = M.MotoID WHERE M.ClienteID = C.ClienteID)
                   ) AS Visitas
            FROM Clientes C 
            ORDER BY Visitas DESC, C.ClienteID DESC
        """)
        clientes = cursor.fetchall()
        top_5_ids = [c[0] for c in clientes[:5]] if clientes else []
        
        cursor.execute("SELECT CajaID FROM ControlCaja WHERE Estado = 'Abierta'")
        caja_abierta = cursor.fetchone()
        
        conn.close()
        return render_template('caja/emision_factura.html', productos=productos, clientes=clientes, top_5_ids=top_5_ids, caja_abierta=caja_abierta)

@cashier_bp.route('/factura_digital/<int:factura_id>', methods=['GET'])
def factura_digital(factura_id):
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('cashier.index'))
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT F.FacturaID, F.NumeroFactura, F.FechaEmision, F.SubTotal, F.TotalIVA, F.TotalNeto, F.MetodoPago, F.DescuentoAplicado,
               COALESCE(C.NombreCompleto, CM.NombreCompleto) AS ClienteFijo, 
               F.NombreClienteDePaso,
               O.OrdenID,
               COALESCE(C.Identificacion, CM.Identificacion, F.RUCCliente) AS ClienteIdentificacion,
               ISNULL(F.RUC_Emisor, ?) AS RUCEmisor,
               COALESCE(C.Telefono, CM.Telefono) AS ClienteTelefono
        FROM Facturas F
        LEFT JOIN Clientes C ON F.ClienteID = C.ClienteID
        LEFT JOIN OrdenesTrabajo O ON F.OrdenID = O.OrdenID
        LEFT JOIN Motocicletas M ON O.MotoID = M.MotoID
        LEFT JOIN Clientes CM ON M.ClienteID = CM.ClienteID
        WHERE F.FacturaID = ?
    """, (Config.COMPANY_RUC, factura_id))
    factura = cursor.fetchone()
    
    if not factura:
        conn.close()
        flash('Factura no encontrada', 'error')
        return redirect(url_for('cashier.index'))
        
    cursor.execute("""
        SELECT Descripcion, Cantidad, PrecioVentaAplicado, ProductoID
        FROM DetalleFactura
        WHERE FacturaID = ?
    """, (factura_id,))
    detalles = cursor.fetchall()
    
    # If it is a workshop order, only fetch from OrdenManoObra if labor is NOT already in DetalleFactura
    mano_obra = []
    if factura.OrdenID:
        tiene_mo_en_detalle = any(d[3] is None for d in detalles)
        if not tiene_mo_en_detalle:
            cursor.execute("SELECT DescripcionServicio, CostoSugerido FROM OrdenManoObra WHERE OrdenID = ?", (factura.OrdenID,))
            mano_obra = cursor.fetchall()
        
    conn.close()
    
    return render_template('caja/factura_digital.html', factura=factura, detalles=detalles, mano_obra=mano_obra)

@cashier_bp.route('/registro_ventas', methods=['GET'])
def registro_ventas():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5]:
        return redirect(url_for('auth.login'))
        
    tipo = request.args.get('tipo', 'pos')
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la BD.', 'error')
        return redirect(url_for('cashier.index'))
        
    cursor = conn.cursor()
    
    where_clause = "WHERE F.OrdenID IS NOT NULL" if tipo == 'taller' else "WHERE F.OrdenID IS NULL"
    titulo_pagina = "Registro de Órdenes del Taller" if tipo == 'taller' else "Registro de Ventas"
    
    cursor.execute(f"""
        SELECT F.FacturaID, F.NumeroFactura, F.FechaEmision, F.TotalNeto, F.MetodoPago,
               C.NombreCompleto AS ClienteFijo, F.NombreClienteDePaso, F.OrdenID,
               (SELECT STRING_AGG(CONVERT(NVARCHAR(MAX), DF.Cantidad) + 'x ' + DF.Descripcion, ', ') FROM DetalleFactura DF WHERE DF.FacturaID = F.FacturaID) AS Productos
        FROM Facturas F
        LEFT JOIN Clientes C ON F.ClienteID = C.ClienteID
        {where_clause}
        ORDER BY F.FechaEmision DESC
    """)
    facturas = cursor.fetchall()
    conn.close()
    
    return render_template('caja/registro_ventas.html', facturas=facturas, titulo_pagina=titulo_pagina)

@cashier_bp.route('/cerrar_caja', methods=['POST'])
def cerrar_caja():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CajaID, MontoInicial FROM ControlCaja WHERE Estado = 'Abierta'")
            row = cursor.fetchone()
            if row:
                caja_id = row[0]
                monto_inicial = row[1]
                
                efectivo_fisico_str = request.form.get('efectivo_fisico', 0)
                try:
                    efectivo_fisico = float(efectivo_fisico_str)
                except ValueError:
                    efectivo_fisico = 0.0
                
                cursor.execute("SELECT ISNULL(SUM(TotalNeto), 0) FROM Facturas WHERE CajaID = ? AND Estado = 'Pagada'", (caja_id,))
                total_ventas = cursor.fetchone()[0]
                
                monto_final = float(monto_inicial) + float(total_ventas) # Lo que debería haber (Sistema)
                diferencia = efectivo_fisico - monto_final # Lo que hay - Lo que debería haber
                
                cursor.execute("""
                    UPDATE ControlCaja 
                    SET Estado = 'Cerrada', FechaCierre = GETDATE(), MontoFinal = ?, EfectivoFisico = ?, Diferencia = ? 
                    WHERE CajaID = ?
                """, (monto_final, efectivo_fisico, diferencia, caja_id))
                
                conn.commit()
                flash('Caja cerrada exitosamente del día.', 'success')
            else:
                flash('No hay ninguna caja abierta.', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'Error al cerrar la caja: {e}', 'error')
        finally:
            conn.close()
    return redirect(url_for('cashier.index'))

@cashier_bp.route('/abrir_caja', methods=['POST'])
def abrir_caja():
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Check if it's already open
            cursor.execute("SELECT CajaID FROM ControlCaja WHERE Estado = 'Abierta'")
            if cursor.fetchone():
                flash('La caja ya está abierta.', 'error')
                return redirect(url_for('cashier.index'))
                
            # Check how many times it was opened today
            cursor.execute("SELECT COUNT(*) FROM ControlCaja WHERE CAST(FechaApertura AS DATE) = CAST(GETDATE() AS DATE)")
            count_today = cursor.fetchone()[0]
            
            if count_today >= 10:
                flash('Solo se permite abrir la caja un máximo de 10 veces por día.', 'error')
            else:
                monto_inicial = request.form.get('monto_inicial', 0)
                usuario_id = session.get('usuario_id')
                cursor.execute("""
                    INSERT INTO ControlCaja (UsuarioID, FechaApertura, MontoInicial, Estado)
                    VALUES (?, GETDATE(), ?, 'Abierta')
                """, (usuario_id, monto_inicial))
                conn.commit()
                flash('Caja abierta exitosamente.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al abrir la caja: {e}', 'error')
        finally:
            conn.close()
    return redirect(url_for('cashier.index'))

@cashier_bp.route('/ventas_recibidas')
def ventas_recibidas():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2]:
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT V.VentaID, ISNULL(C.NombreCompleto, V.NombrePaso) AS Cliente, V.MetodoPago, V.Fecha,
               (SELECT ISNULL(SUM(Cantidad * PrecioVenta), 0) FROM DetalleVentasRecibidas WHERE VentaID = V.VentaID) AS Total
        FROM VentasRecibidas V
        LEFT JOIN Clientes C ON V.ClienteID = C.ClienteID
        WHERE V.Estado = 'Pendiente'
        ORDER BY V.Fecha DESC
    """)
    ventas = cursor.fetchall()
    
    cursor.execute("SELECT CajaID, MontoInicial FROM ControlCaja WHERE Estado = 'Abierta'")
    caja_abierta = cursor.fetchone()
    
    cursor.execute("SELECT ClienteID, NombreCompleto FROM Clientes ORDER BY NombreCompleto ASC")
    clientes = cursor.fetchall()
    
    conn.close()
    return render_template('caja/ventas_recibidas.html', ventas=ventas, caja_abierta=caja_abierta, clientes=clientes)

@cashier_bp.route('/facturar_venta/<int:venta_id>', methods=['POST'])
def facturar_venta(venta_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2]:
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CajaID FROM ControlCaja WHERE Estado = 'Abierta'")
        caja = cursor.fetchone()
        if not caja:
            flash('Debes abrir una caja primero.', 'error')
            return redirect(url_for('cashier.ventas_recibidas'))
        caja_id = caja[0]
        
        cursor.execute("SELECT ClienteID, NombrePaso, MetodoPago FROM VentasRecibidas WHERE VentaID = ?", (venta_id,))
        venta = cursor.fetchone()
        if not venta:
            flash('Venta no encontrada.', 'error')
            return redirect(url_for('cashier.ventas_recibidas'))
            
        cliente_id, nombre_paso, metodo_pago = venta
        
        cursor.execute("SELECT ISNULL(SUM(Cantidad * PrecioVenta), 0) FROM DetalleVentasRecibidas WHERE VentaID = ?", (venta_id,))
        total = float(cursor.fetchone()[0] or 0)
        
        subtotal = round(total / 1.15, 2)
        iva = round(total - subtotal, 2)
        
        import uuid
        numero_factura = 'VR-' + str(uuid.uuid4())[:6].upper()
        
        cursor.execute("""
            SET NOCOUNT ON;
            INSERT INTO Facturas (CajaID, NumeroFactura, SubTotal, TotalIVA, ImpuestoDGI, TotalNeto, MetodoPago, ClienteID, NombreClienteDePaso, RUC_Emisor)
            VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?);
            SELECT SCOPE_IDENTITY();
        """, (caja_id, numero_factura, subtotal, iva, total, metodo_pago, cliente_id, nombre_paso, Config.COMPANY_RUC))
        
        factura_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT ProductoID, Cantidad, PrecioVenta FROM DetalleVentasRecibidas WHERE VentaID = ?", (venta_id,))
        detalles = cursor.fetchall()
        for d in detalles:
            cursor.execute("""
                INSERT INTO DetalleFactura (FacturaID, ProductoID, Descripcion, Cantidad, PrecioVentaAplicado)
                VALUES (?, ?, (SELECT Nombre FROM Productos WHERE ProductoID = ?), ?, ?)
            """, (factura_id, d[0], d[0], d[1], d[2]))
            
        cursor.execute("UPDATE VentasRecibidas SET Estado = 'Facturada' WHERE VentaID = ?", (venta_id,))
        
        conn.commit()
        flash(f'Venta recibida facturada exitosamente. Factura: {numero_factura}', 'success')
        return redirect(url_for('cashier.factura_digital', factura_id=factura_id))
    except Exception as e:
        conn.rollback()
        flash(f'Error al facturar la venta: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('cashier.ventas_recibidas'))


@cashier_bp.route('/facturas')
def facturas():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5]:
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    facturas_list = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.FacturaID, f.FechaEmision, 
                   COALESCE(c.NombreCompleto, cm.NombreCompleto, f.NombreClienteDePaso, 'Consumidor Final') as Cliente, 
                   f.SubTotal, f.TotalIVA, f.TotalNeto, f.MetodoPago, f.Estado,
                   ISNULL(f.RUC_Emisor, ?) as RUC_Emisor,
                   f.NumeroFactura
            FROM Facturas f
            LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
            LEFT JOIN OrdenesTrabajo o ON f.OrdenID = o.OrdenID
            LEFT JOIN Motocicletas m ON o.MotoID = m.MotoID
            LEFT JOIN Clientes cm ON m.ClienteID = cm.ClienteID
            ORDER BY f.FechaEmision DESC
        """, (Config.COMPANY_RUC,))
        facturas_list = cursor.fetchall()
        conn.close()
    return render_template('caja/facturas.html', facturas=facturas_list)

@cashier_bp.route('/cierres')
def cierres():
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5]:
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cierres_list = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.CajaID, u.NombreCompleto, c.FechaApertura, c.FechaCierre, c.MontoInicial, c.Estado,
                   c.MontoFinal, c.EfectivoFisico, c.Diferencia
            FROM ControlCaja c
            JOIN Usuarios u ON c.UsuarioID = u.UsuarioID
            ORDER BY c.FechaApertura DESC
        """)
        cierres_list = cursor.fetchall()
        conn.close()
    return render_template('caja/cierres.html', cierres=cierres_list)

@cashier_bp.route('/editar_cierre/<int:caja_id>', methods=['POST'])
def editar_cierre(caja_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5]:
        flash('No tienes permisos para modificar registros de caja.', 'error')
        return redirect(url_for('cashier.cierres'))
    
    monto_inicial = request.form.get('monto_inicial', type=float)
    monto_final = request.form.get('monto_final', type=float)
    efectivo_fisico = request.form.get('efectivo_fisico', type=float)
    estado = request.form.get('estado', 'Cerrada').strip()
    
    if monto_inicial is None:
        monto_inicial = 0.0
    if monto_final is None:
        monto_final = 0.0
    if efectivo_fisico is None:
        efectivo_fisico = 0.0
        
    diferencia = round(efectivo_fisico - monto_final, 2)
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ControlCaja 
                SET MontoInicial = ?, MontoFinal = ?, EfectivoFisico = ?, Diferencia = ?, Estado = ?
                WHERE CajaID = ?
            """, (monto_inicial, monto_final, efectivo_fisico, diferencia, estado, caja_id))
            conn.commit()
            flash(f'Registro de Caja #{caja_id} actualizado con éxito.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al actualizar el registro de caja: {e}', 'error')
        finally:
            conn.close()
            
    return redirect(url_for('cashier.cierres'))


# ====================================================================
# VENTAS RÁPIDAS DE MOSTRADOR (POS PÚBLICO / VENDEDORES)
# ====================================================================

@cashier_bp.route('/pos_publico', methods=['GET'])
@cashier_bp.route('/pos', methods=['GET'])
def pos_publico():
    """Vista de catálogo rápido para ventas de mostrador preliminares."""
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a base de datos."
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ProductoID, CodigoSKU, Nombre, PrecioVenta, StockActual, ImagenURL, Categoria, TipoMoto 
        FROM Productos 
        WHERE StockActual > 0 AND Activo = 1
    """)
    productos = cursor.fetchall()
    
    cursor.execute("""
        SELECT C.ClienteID, C.NombreCompleto, C.Telefono,
               (SELECT COUNT(F.FacturaID) 
                FROM Facturas F 
                WHERE F.ClienteID = C.ClienteID
               ) AS Visitas
        FROM Clientes C 
        ORDER BY Visitas DESC, C.ClienteID DESC
    """)
    clientes = cursor.fetchall()
    top_5_ids = [c[0] for c in clientes[:5]] if clientes else []
    conn.close()
    return render_template('auth/public_pos.html', productos=productos, clientes=clientes, top_5_ids=top_5_ids)


@cashier_bp.route('/pos_enviar', methods=['POST'])
def pos_enviar():
    """Procesa el envío de una venta de mostrador a la bandeja de Caja."""
    cliente_id_str = (request.form.get('cliente_id') or '').strip()
    nombre_paso = (request.form.get('nombre_paso') or '').strip()
    metodo_pago = request.form.get('metodo_pago', 'Efectivo')
    productos_ids = request.form.getlist('producto_id[]')
    cantidades = request.form.getlist('cantidad[]')
    precios = request.form.getlist('precio[]')
    
    if not productos_ids:
        flash("Debes seleccionar al menos un producto del catálogo antes de enviar a caja.", "error")
        return redirect(url_for('cashier.pos_publico'))
        
    if not cliente_id_str and not nombre_paso:
        flash("Debes seleccionar un cliente registrado o ingresar el nombre del cliente de paso.", "error")
        return redirect(url_for('cashier.pos_publico'))
        
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión con la base de datos. Por favor, reintenta en unos instantes.", "error")
        return redirect(url_for('cashier.pos_publico'))
        
    cursor = conn.cursor()
    try:
        cliente_id = int(cliente_id_str) if cliente_id_str else None
        
        cursor.execute("""
            SET NOCOUNT ON;
            INSERT INTO VentasRecibidas (ClienteID, NombrePaso, MetodoPago, Estado)
            VALUES (?, ?, ?, 'Pendiente');
            SELECT SCOPE_IDENTITY();
        """, (cliente_id, nombre_paso if nombre_paso else None, metodo_pago))
        
        venta_id = int(cursor.fetchone()[0])
        
        for pid, cant, prec in zip(productos_ids, cantidades, precios):
            cursor.execute("""
                INSERT INTO DetalleVentasRecibidas (VentaID, ProductoID, Cantidad, PrecioVenta)
                VALUES (?, ?, ?, ?)
            """, (venta_id, int(pid), int(cant), float(prec)))
            
        conn.commit()
        flash(f"Tu pedido fue transferido a la ventanilla de cobranza con el código #VR-{venta_id:04d}. Acércate a Caja para realizar tu pago.", "success")
    except Exception as e:
        conn.rollback()
        print("Error al guardar venta pública:", e)
        flash("Ocurrió un inconveniente al procesar tu venta. Por favor, inténtalo de nuevo.", "error")
    finally:
        conn.close()
        
    return redirect(url_for('cashier.pos_publico'))

# Alias para compatibilidad
pos_publico_view = pos_publico
pos_enviar_view = pos_enviar



@cashier_bp.route('/eliminar_orden/<int:orden_id>', methods=['POST'])
def eliminar_orden(orden_id):
    if 'usuario_id' not in session or session.get('rol_id') not in [1, 2, 5, 8, 1008]:
        flash('No tienes permisos para eliminar órdenes.', 'error')
        return redirect(url_for('cashier.ordenes_taller'))
        
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('cashier.ordenes_taller'))
        
    cursor = conn.cursor()
    try:
        # 1. Desvincular o cancelar CitaWhatsApp si estaba vinculada
        cursor.execute("""
            UPDATE CitasWhatsApp 
            SET Estado = 'Cancelada' 
            WHERE CitaID = (SELECT TOP 1 CitaID FROM OrdenesTrabajo WHERE OrdenID = ?)
        """, (orden_id,))
        
        # 2. Eliminar repuestos y mano de obra asociados
        cursor.execute("DELETE FROM OrdenRepuestos WHERE OrdenID = ?", (orden_id,))
        cursor.execute("DELETE FROM OrdenManoObra WHERE OrdenID = ?", (orden_id,))
        
        # 3. Eliminar la orden de trabajo
        cursor.execute("DELETE FROM OrdenesTrabajo WHERE OrdenID = ?", (orden_id,))
        
        conn.commit()
        flash(f'¡Orden de Trabajo #{orden_id} eliminada exitosamente de Caja!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar la Orden #{orden_id}: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('cashier.ordenes_taller'))
