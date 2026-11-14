import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
from database import get_db_connection

mercadotecnia_bp = Blueprint('mercadotecnia', __name__)

def _normalizar_imagen_producto(img_url):
    """Normaliza rutas de imagen de productos; retorna cadena vacía si el producto no tiene imagen."""
    if not img_url:
        return ''
    raw = str(img_url).strip().replace('\\', '/')
    if not raw:
        return ''
    if raw.startswith('http://') or raw.startswith('https://'):
        return raw
    while raw.startswith('/'):
        raw = raw[1:]
    while raw.startswith('static/img/'):
        raw = raw[len('static/img/'):]
    if raw.startswith('static/'):
        rel = raw[len('static/'):]
    elif raw.startswith('img/'):
        rel = raw
    else:
        rel = f"img/{raw}"
    disk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', rel.replace('/', os.sep))
    if not os.path.isfile(disk_path):
        return ''
    return f"/static/{rel}"

def mercadotecnia_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para acceder.", "error")
            return redirect(url_for('auth.login'))
        
        rol_id = session.get('rol_id')
        username = session.get('username', '')
        rol_nombre = session.get('rol_nombre', '')
        
        # Permitir a Superadmin (1), Gerente (5), Carlos Huete (carlos.merca) o Rol Mercadotecnia (1010)
        if rol_id not in (1, 5, 1010) and username != 'carlos.merca' and 'Mercadotecnia' not in rol_nombre:
            flash("Acceso restringido. Solo personal de mercadotecnia o gerencia.", "error")
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

def obtener_clientes_participantes(mes=None, anio=None, umbral=1000.0):
    """
    Obtiene todos los clientes cuyas compras acumuladas en el mes sumen >= umbral (por defecto C$ 1,000).
    Suma automáticamente todas las facturas pagadas del cliente en el mes (ej: 500 + 500 = 1000).
    """
    now = datetime.now()
    if not mes:
        mes = now.month
    if not anio:
        anio = now.year

    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    participantes = []
    
    try:
        # Consulta que agrupa compras del cliente por mes (Taller + Tienda)
        cursor.execute("""
            SELECT 
                COALESCE(f.ClienteID, m.ClienteID, 0) as ClienteID,
                COALESCE(c.NombreCompleto, c_moto.NombreCompleto, f.NombreClienteDePaso, 'Cliente Mostrador') as NombreCliente,
                COALESCE(c.Telefono, c_moto.Telefono, 'N/A') as Telefono,
                COALESCE(c.Identificacion, c_moto.Identificacion, 'N/A') as Identificacion,
                COALESCE(c.Email, c_moto.Email, 'N/A') as Email,
                COUNT(f.FacturaID) as CantidadCompras,
                SUM(f.TotalNeto) as TotalAcumulado,
                SUM(CASE WHEN f.OrdenID IS NOT NULL THEN 1 ELSE 0 END) as CantidadOrdenesTaller,
                SUM(CASE WHEN f.OrdenID IS NULL THEN 1 ELSE 0 END) as CantidadVentasTienda
            FROM Facturas f
            LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
            LEFT JOIN OrdenesTrabajo ot ON f.OrdenID = ot.OrdenID
            LEFT JOIN Motocicletas m ON ot.MotoID = m.MotoID
            LEFT JOIN Clientes c_moto ON m.ClienteID = c_moto.ClienteID
            WHERE f.Estado = 'Pagada' 
              AND MONTH(f.FechaEmision) = ? 
              AND YEAR(f.FechaEmision) = ?
            GROUP BY 
                COALESCE(f.ClienteID, m.ClienteID, 0),
                COALESCE(c.NombreCompleto, c_moto.NombreCompleto, f.NombreClienteDePaso, 'Cliente Mostrador'),
                COALESCE(c.Telefono, c_moto.Telefono, 'N/A'),
                COALESCE(c.Identificacion, c_moto.Identificacion, 'N/A'),
                COALESCE(c.Email, c_moto.Email, 'N/A')
            HAVING SUM(f.TotalNeto) >= ?
            ORDER BY TotalAcumulado DESC
        """, (mes, anio, umbral))
        
        filas = cursor.fetchall()
        for row in filas:
            cid = row[0]
            nombre = row[1]
            telefono = row[2]
            identificacion = row[3]
            email = row[4]
            cantidad = int(row[5])
            total = float(row[6])
            cant_taller = int(row[7])
            cant_tienda = int(row[8])
            boletos = int(total // umbral) # 1 boleto por cada C$ 1,000

            # Obtener el detalle de facturas (Taller y Tienda) de este cliente
            cursor.execute("""
                SELECT 
                    f.NumeroFactura, 
                    f.TotalNeto, 
                    f.FechaEmision, 
                    f.MetodoPago,
                    f.OrdenID,
                    ot.TipoServicio,
                    m.Placa,
                    m.Modelo
                FROM Facturas f
                LEFT JOIN OrdenesTrabajo ot ON f.OrdenID = ot.OrdenID
                LEFT JOIN Motocicletas m ON ot.MotoID = m.MotoID
                WHERE f.Estado = 'Pagada'
                  AND MONTH(f.FechaEmision) = ?
                  AND YEAR(f.FechaEmision) = ?
                  AND (
                      (COALESCE(f.ClienteID, m.ClienteID) = ? AND ? > 0)
                      OR (COALESCE(f.ClienteID, m.ClienteID) IS NULL AND f.NombreClienteDePaso = ? AND ? = 0)
                  )
                ORDER BY f.FechaEmision ASC
            """, (mes, anio, cid, cid, nombre, cid))
            
            facturas_detalle = []
            for fac in cursor.fetchall():
                num_fac, monto_fac, fecha_fac, metodo_fac, ord_id, tipo_serv, placa, modelo = fac
                if ord_id:
                    descripcion_origen = f"Orden Taller #{ord_id} • {tipo_serv or 'Servicio'}"
                    if modelo or placa:
                        moto_desc = f"{modelo or ''} ({placa or 'S/P'})".strip()
                        descripcion_origen += f" [{moto_desc}]"
                    es_taller = True
                else:
                    descripcion_origen = "Venta en Tienda / Mostrador"
                    es_taller = False
                    
                facturas_detalle.append({
                    'numero': num_fac,
                    'monto': float(monto_fac),
                    'fecha': fecha_fac.strftime('%d/%m/%Y %H:%M') if fecha_fac else 'N/A',
                    'metodo': metodo_fac or 'Efectivo',
                    'orden_id': ord_id,
                    'es_taller': es_taller,
                    'descripcion_origen': descripcion_origen
                })

            participantes.append({
                'cliente_id': cid,
                'nombre': nombre,
                'telefono': telefono,
                'identificacion': identificacion,
                'email': email,
                'cantidad_compras': cantidad,
                'cantidad_ordenes': cant_taller,
                'cantidad_tienda': cant_tienda,
                'total_acumulado': total,
                'boletos': boletos,
                'facturas': facturas_detalle
            })

    except Exception as e:
        print(f"Error consultando clientes participantes: {e}")
    finally:
        conn.close()

    return participantes

@mercadotecnia_bp.route('/mercadotecnia/')
@mercadotecnia_bp.route('/mercadotecnia/resumen')
@mercadotecnia_required
def resumen():
    now = datetime.now()
    mes_actual = now.month
    anio_actual = now.year
    nombre_mes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes_actual - 1]
    mes_periodo = f"{nombre_mes} {anio_actual}"

    participantes = obtener_clientes_participantes(mes_actual, anio_actual, 1000.0)
    total_participantes = len(participantes)
    total_boletos = sum(p['boletos'] for p in participantes)
    total_ventas_participantes = sum(p['total_acumulado'] for p in participantes)

    conn = get_db_connection()
    premio_activo = None
    historial_premios = []

    if conn:
        cursor = conn.cursor()
        try:
            # Premio activo del mes
            cursor.execute("""
                SELECT r.RifaID, r.ProductoID, p.Nombre, p.CodigoSKU, p.PrecioVenta, p.ImagenURL, 
                       r.MesPeriodo, r.FechaAsignacion, r.Estado, r.GanadorNombre, r.GanadorTelefono, r.FechaSorteo
                FROM RifaPremios r
                JOIN Productos p ON r.ProductoID = p.ProductoID
                WHERE r.MesPeriodo = ? OR r.Estado = 'Activa'
                ORDER BY r.RifaID DESC
            """, (mes_periodo,))
            row = cursor.fetchone()
            if row:
                premio_activo = {
                    'rifa_id': row[0],
                    'producto_id': row[1],
                    'nombre': row[2],
                    'sku': row[3],
                    'precio': float(row[4] or 0),
                    'imagen': _normalizar_imagen_producto(row[5]),
                    'mes': row[6],
                    'fecha_asignacion': row[7].strftime('%d/%m/%Y') if row[7] else '',
                    'estado': row[8],
                    'ganador_nombre': row[9],
                    'ganador_telefono': row[10],
                    'fecha_sorteo': row[11].strftime('%d/%m/%Y %H:%M') if row[11] else ''
                }

            # Últimos sorteos realizados
            cursor.execute("""
                SELECT TOP 5 r.RifaID, p.Nombre, p.PrecioVenta, r.MesPeriodo, r.Estado, r.GanadorNombre, r.FechaSorteo
                FROM RifaPremios r
                JOIN Productos p ON r.ProductoID = p.ProductoID
                ORDER BY r.RifaID DESC
            """)
            for h in cursor.fetchall():
                historial_premios.append({
                    'rifa_id': h[0],
                    'producto': h[1],
                    'precio': float(h[2] or 0),
                    'mes': h[3],
                    'estado': h[4],
                    'ganador': h[5] or 'Pendiente de Sorteo',
                    'fecha_sorteo': h[6].strftime('%d/%m/%Y') if h[6] else 'No realizado'
                })
        except Exception as e:
            print(f"Error consultando premios de rifa: {e}")
        finally:
            conn.close()

    return render_template(
        'mercadotecnia/resumen.html',
        mes_periodo=mes_periodo,
        participantes=participantes,
        total_participantes=total_participantes,
        total_boletos=total_boletos,
        total_ventas_participantes=total_ventas_participantes,
        premio_activo=premio_activo,
        historial_premios=historial_premios
    )

@mercadotecnia_bp.route('/mercadotecnia/participantes')
@mercadotecnia_required
def participantes():
    now = datetime.now()
    mes_sel = request.args.get('mes', now.month, type=int)
    anio_sel = request.args.get('anio', now.year, type=int)
    umbral = request.args.get('umbral', 1000.0, type=float)

    nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_nombre = nombres_meses[mes_sel - 1] if 1 <= mes_sel <= 12 else ''

    lista = obtener_clientes_participantes(mes_sel, anio_sel, umbral)
    total_ventas = sum(p['total_acumulado'] for p in lista)
    total_boletos = sum(p['boletos'] for p in lista)

    # Obtener el premio activo para el sorteo
    conn = get_db_connection()
    premio = None
    if conn:
        cursor = conn.cursor()
        mes_str = f"{mes_nombre} {anio_sel}"
        cursor.execute("""
            SELECT TOP 1 r.RifaID, p.Nombre, p.PrecioVenta, p.ImagenURL, r.Estado, r.GanadorNombre
            FROM RifaPremios r
            JOIN Productos p ON r.ProductoID = p.ProductoID
            WHERE (r.MesPeriodo = ? OR r.Estado = 'Activa')
            ORDER BY r.RifaID DESC
        """, (mes_str,))
        row = cursor.fetchone()
        if row:
            premio = {
                'rifa_id': row[0],
                'nombre': row[1],
                'precio': float(row[2] or 0),
                'imagen': _normalizar_imagen_producto(row[3]),
                'estado': row[4],
                'ganador': row[5]
            }
        conn.close()

    return render_template(
        'mercadotecnia/participantes.html',
        participantes=lista,
        mes_sel=mes_sel,
        anio_sel=anio_sel,
        mes_nombre=mes_nombre,
        umbral=umbral,
        total_ventas=total_ventas,
        total_boletos=total_boletos,
        premio=premio
    )

@mercadotecnia_bp.route('/mercadotecnia/premios', methods=['GET', 'POST'])
@mercadotecnia_required
def premios():
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos.", "error")
        return redirect(url_for('mercadotecnia.resumen'))

    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        # 1. Asignar nuevo producto del inventario para la rifa del mes (DESCUENTA DEL STOCK)
        if action == 'asignar_premio':
            producto_id = request.form.get('producto_id', type=int)
            mes_periodo = request.form.get('mes_periodo')
            observaciones = request.form.get('observaciones', '')
            usuario_id = session.get('usuario_id')

            if not producto_id or not mes_periodo:
                flash("Debes seleccionar un producto del inventario y especificar el mes.", "error")
                return redirect(url_for('mercadotecnia.premios'))

            try:
                # Verificar stock disponible en inventario
                cursor.execute("SELECT Nombre, StockActual, PrecioVenta FROM Productos WHERE ProductoID = ?", (producto_id,))
                prod = cursor.fetchone()
                if not prod:
                    flash("El producto seleccionado no existe.", "error")
                    return redirect(url_for('mercadotecnia.premios'))
                
                nombre_prod = prod[0]
                stock_actual = int(prod[1] or 0)
                if stock_actual <= 0:
                    flash(f"No hay stock disponible para '{nombre_prod}' (Stock actual: {stock_actual}).", "error")
                    return redirect(url_for('mercadotecnia.premios'))

                # Descontar 1 unidad del stock de inventario
                nuevo_stock = stock_actual - 1
                cursor.execute("""
                    UPDATE Productos 
                    SET StockActual = StockActual - 1 
                    WHERE ProductoID = ?
                """, (producto_id,))

                # Registrar el premio en la tabla de rifas
                cursor.execute("""
                    INSERT INTO RifaPremios (ProductoID, MesPeriodo, Cantidad, FechaAsignacion, Estado, Observaciones, UsuarioID)
                    VALUES (?, ?, 1, GETDATE(), 'Activa', ?, ?)
                """, (producto_id, mes_periodo, observaciones, usuario_id))

                conn.commit()
                flash(f"¡Éxito! El producto '{nombre_prod}' se asignó como premio para la rifa de {mes_periodo}. Se descontó 1 unidad del stock de inventario (Stock restante: {nuevo_stock}).", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error al asignar premio: {e}", "error")

        # 2. Registrar ganador del sorteo
        elif action == 'registrar_ganador':
            rifa_id = request.form.get('rifa_id', type=int)
            ganador_nombre = request.form.get('ganador_nombre')
            ganador_telefono = request.form.get('ganador_telefono', '')
            ganador_id = request.form.get('ganador_cliente_id', type=int)

            if rifa_id and ganador_nombre:
                try:
                    cursor.execute("""
                        UPDATE RifaPremios
                        SET GanadorNombre = ?,
                            GanadorTelefono = ?,
                            GanadorClienteID = ?,
                            Estado = 'Sorteada',
                            FechaSorteo = GETDATE()
                        WHERE RifaID = ?
                    """, (ganador_nombre, ganador_telefono, ganador_id, rifa_id))
                    conn.commit()
                    flash(f"¡Sorteo guardado! El ganador oficial de la rifa es: {ganador_nombre}.", "success")
                except Exception as e:
                    conn.rollback()
                    flash(f"Error al registrar ganador: {e}", "error")

        # 3. Marcar premio como entregado
        elif action == 'entregar_premio':
            rifa_id = request.form.get('rifa_id', type=int)
            if rifa_id:
                try:
                    cursor.execute("UPDATE RifaPremios SET Estado = 'Entregado' WHERE RifaID = ?", (rifa_id,))
                    conn.commit()
                    flash("¡Premio marcado como entregado al cliente!", "success")
                except Exception as e:
                    conn.rollback()
                    flash(f"Error: {e}", "error")

        return redirect(url_for('mercadotecnia.premios'))

    # Obtener catálogo de productos disponibles en el inventario con stock > 0
    cursor.execute("""
        SELECT ProductoID, CodigoSKU, Categoria, Nombre, Descripcion, PrecioVenta, StockActual, ImagenURL
        FROM Productos
        WHERE Activo = 1 AND StockActual > 0
        ORDER BY Categoria, Nombre
    """)
    productos_disponibles = [
        {
            'producto_id': p[0],
            'sku': p[1],
            'categoria': p[2],
            'nombre': p[3],
            'descripcion': p[4],
            'precio': float(p[5] or 0),
            'stock': int(p[6] or 0),
            'imagen': _normalizar_imagen_producto(p[7])
        }
        for p in cursor.fetchall()
    ]

    # Obtener listado de premios registrados
    cursor.execute("""
        SELECT r.RifaID, r.ProductoID, p.Nombre, p.CodigoSKU, p.PrecioVenta, p.ImagenURL,
               r.MesPeriodo, r.FechaAsignacion, r.Estado, r.GanadorNombre, r.GanadorTelefono, r.FechaSorteo, r.Observaciones
        FROM RifaPremios r
        JOIN Productos p ON r.ProductoID = p.ProductoID
        ORDER BY r.RifaID DESC
    """)
    rifas_registradas = [
        {
            'rifa_id': r[0],
            'producto_id': r[1],
            'nombre': r[2],
            'sku': r[3],
            'precio': float(r[4] or 0),
            'imagen': _normalizar_imagen_producto(r[5]),
            'mes': r[6],
            'fecha_asignacion': r[7].strftime('%d/%m/%Y') if r[7] else '',
            'estado': r[8],
            'ganador_nombre': r[9] or 'Pendiente de Sorteo',
            'ganador_telefono': r[10] or '',
            'fecha_sorteo': r[11].strftime('%d/%m/%Y %H:%M') if r[11] else 'No sorteado',
            'observaciones': r[12] or ''
        }
        for r in cursor.fetchall()
    ]

    conn.close()

    now = datetime.now()
    nombre_mes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][now.month - 1]
    mes_sugerido = f"{nombre_mes} {now.year}"

    return render_template(
        'mercadotecnia/premios.html',
        productos=productos_disponibles,
        rifas=rifas_registradas,
        mes_sugerido=mes_sugerido
    )

@mercadotecnia_bp.route('/mercadotecnia/api/participantes_sorteo')
@mercadotecnia_required
def api_participantes_sorteo():
    """API JSON para la ruleta de sorteo interactivo"""
    now = datetime.now()
    mes = request.args.get('mes', now.month, type=int)
    anio = request.args.get('anio', now.year, type=int)
    participantes = obtener_clientes_participantes(mes, anio, 1000.0)
    
    # Expandir boletos para sorteo con probabilidad proporcional
    boletos_sorteo = []
    for p in participantes:
        for b in range(p['boletos']):
            boletos_sorteo.append({
                'cliente_id': p['cliente_id'],
                'nombre': p['nombre'],
                'telefono': p['telefono'],
                'boleto_num': b + 1,
                'total_compras': p['total_acumulado']
            })

    return jsonify({
        'total_clientes': len(participantes),
        'total_boletos': len(boletos_sorteo),
        'boletos': boletos_sorteo
    })


# ====================================================================
# SPOT PUBLICITARIO CINEMATOGRÁFICO (PANTALLA COMPLETA)
# ====================================================================
@mercadotecnia_bp.route('/mercadotecnia/spot')
@mercadotecnia_bp.route('/spot_publicitario')
def spot_publicitario():
    """Spot publicitario comercial en pantalla completa de Taller y Lubricantes CR."""
    return render_template('mercadotecnia/spot_publicitario.html')

