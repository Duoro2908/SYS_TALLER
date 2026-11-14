from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from functools import wraps
import pyodbc
import os
import re
from werkzeug.utils import secure_filename

import math

EXTENSIONES_IMAGEN_PERMITIDAS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}


def _validar_datos_producto(sku, nombre, categoria, tipo_moto, precio_compra_raw, precio_venta_raw, imagen_file=None, es_edicion=False):
    """Valida estrictamente los campos de producto en alta y edición."""
    errores = []
    sku_clean = (sku or '').strip().upper()
    nombre_clean = ' '.join((nombre or '').split())
    cat_clean = ' '.join((categoria or '').split())
    tipo_clean = ' '.join((tipo_moto or '').split())

    if not es_edicion:
        if not sku_clean or len(sku_clean) < 3 or len(sku_clean) > 40:
            errores.append('El Código SKU debe tener entre 3 y 40 caracteres.')
        elif not re.match(r'^[A-Z0-9][A-Z0-9._-]{2,39}$', sku_clean) or not re.search(r'[A-Z]', sku_clean):
            errores.append('El Código SKU solo permite letras, números y guiones/puntos, e incluir al menos una letra (Ej: LUB-MOT-10W40).')

    if not nombre_clean or len(nombre_clean) < 3 or len(nombre_clean) > 120:
        errores.append('El Nombre del Producto debe tener entre 3 y 120 caracteres.')
    elif not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', nombre_clean):
        errores.append('El Nombre del Producto debe incluir texto descriptivo válido (no solo números o símbolos).')

    if not cat_clean or len(cat_clean) < 3 or len(cat_clean) > 60:
        errores.append('La Categoría debe tener entre 3 y 60 caracteres.')
    elif not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', cat_clean):
        errores.append('La Categoría debe ser un nombre válido con letras (Ej: Lubricantes).')

    if not tipo_clean or len(tipo_clean) < 3 or len(tipo_clean) > 80:
        errores.append('La Compatibilidad (Moto) debe tener entre 3 y 80 caracteres.')
    elif not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}', tipo_clean):
        errores.append('La Compatibilidad (Moto) debe contener texto válido (Ej: Universal o Génesis 150cc).')

    try:
        p_compra = float(precio_compra_raw)
        if not math.isfinite(p_compra) or p_compra <= 0 or p_compra > 500000:
            errores.append('El Precio de Compra (Costo) debe ser mayor a C$ 0.00 y menor a C$ 500,000.00.')
    except (TypeError, ValueError):
        p_compra = None
        errores.append('El Precio de Compra (Costo) debe ser un número válido.')

    try:
        p_venta = float(precio_venta_raw)
        if not math.isfinite(p_venta) or p_venta <= 0 or p_venta > 1000000:
            errores.append('El Precio de Venta debe ser mayor a C$ 0.00 y menor a C$ 1,000,000.00.')
    except (TypeError, ValueError):
        p_venta = None
        errores.append('El Precio de Venta debe ser un número válido.')

    if p_compra is not None and p_venta is not None and p_compra > 0 and p_venta > 0:
        if p_venta < p_compra:
            errores.append('El Precio de Venta no puede ser menor al Precio de Compra (Costo).')

    if imagen_file and imagen_file.filename:
        ext = os.path.splitext(secure_filename(imagen_file.filename))[1].lower()
        if ext not in EXTENSIONES_IMAGEN_PERMITIDAS:
            errores.append('Formato de imagen no válido. Solo se permiten archivos PNG, JPG, JPEG, WEBP o GIF.')

    return errores, {
        'sku': sku_clean,
        'nombre': nombre_clean,
        'categoria': cat_clean,
        'tipo_moto': tipo_clean,
        'precio_compra': round(p_compra, 2) if p_compra is not None else 0.0,
        'precio_venta': round(p_venta, 2) if p_venta is not None else 0.0,
    }


bodega_bp = Blueprint('bodega', __name__, url_prefix='/bodega')

def bodega_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('rol_id') not in (1, 5, 7): # 1: Super, 5: Gerente, 7: Bodega (Assuming RolID 7 was created)
            flash('Acceso denegado. Solo el personal de Abastecimiento puede ver esta sección.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@bodega_bp.route('/inventario')
@bodega_required
def inventario():
    conn = get_db_connection()
    productos = []
    categorias = []
    tipos_moto = []
    
    if conn:
        cursor = conn.cursor()
        
        # Obtener filtros si existen
        categoria_filtro = request.args.get('categoria', '')
        moto_filtro = request.args.get('tipo_moto', '')
        busqueda = request.args.get('q', '')
        
        query = "SELECT ProductoID, CodigoSKU, Nombre, Categoria, TipoMoto, StockActual, PrecioCompra, PrecioVenta, Activo, ImagenURL FROM Productos WHERE 1=1"
        params = []
        
        if categoria_filtro:
            query += " AND Categoria = ?"
            params.append(categoria_filtro)
            
        if moto_filtro:
            query += " AND TipoMoto = ?"
            params.append(moto_filtro)
            
        if busqueda:
            query += " AND (Nombre LIKE ? OR CodigoSKU LIKE ?)"
            params.append(f'%{busqueda}%')
            params.append(f'%{busqueda}%')
            
        query += " ORDER BY Nombre ASC"
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        
        # Obtener listas únicas para los filtros
        cursor.execute("SELECT DISTINCT Categoria FROM Productos WHERE Categoria IS NOT NULL")
        categorias = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT TipoMoto FROM Productos WHERE TipoMoto IS NOT NULL")
        tipos_moto = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
    return render_template('bodega/inventario.html', 
                           productos=productos, 
                           categorias=categorias, 
                           tipos_moto=tipos_moto,
                           current_cat=categoria_filtro,
                           current_moto=moto_filtro,
                           current_q=busqueda)

@bodega_bp.route('/producto/nuevo', methods=['POST'])
@bodega_required
def nuevo_producto():
    sku = request.form.get('sku', '')
    nombre = request.form.get('nombre', '')
    categoria = request.form.get('categoria', '')
    tipo_moto = request.form.get('tipo_moto', '')
    precio_compra_raw = request.form.get('precio_compra')
    precio_venta_raw = request.form.get('precio_venta')
    file = request.files.get('imagen')

    errores, datos = _validar_datos_producto(
        sku, nombre, categoria, tipo_moto, precio_compra_raw, precio_venta_raw, imagen_file=file, es_edicion=False
    )
    if errores:
        flash(' • '.join(errores), 'error')
        return redirect(url_for('bodega.inventario'))

    imagen_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('static', 'img', 'productos')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        imagen_url = f"/static/img/productos/{filename}"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 ProductoID FROM Productos WHERE UPPER(CodigoSKU) = UPPER(?)", (datos['sku'],))
        if cursor.fetchone():
            flash(f"Ya existe un producto registrado con el Código SKU '{datos['sku']}'. Usa uno único.", 'error')
            return redirect(url_for('bodega.inventario'))

        cursor.execute("""
            INSERT INTO Productos (CodigoSKU, Nombre, Categoria, TipoMoto, PrecioCompra, PrecioVenta, StockActual, MostrarEnCatalogo, Activo, ImagenURL)
            VALUES (?, ?, ?, ?, ?, ?, 0, 1, 1, ?)
        """, (datos['sku'], datos['nombre'], datos['categoria'], datos['tipo_moto'], datos['precio_compra'], datos['precio_venta'], imagen_url))
        conn.commit()
        flash(f"Producto '{datos['nombre']}' registrado exitosamente.", 'success')
    except Exception:
        conn.rollback()
        flash('No se pudo registrar el producto. Verifica los datos e inténtalo nuevamente.', 'error')
    finally:
        conn.close()
    return redirect(url_for('bodega.inventario'))


@bodega_bp.route('/producto/editar/<int:id>', methods=['POST'])
@bodega_required
def editar_producto(id):
    nombre = request.form.get('nombre', '')
    categoria = request.form.get('categoria', '')
    tipo_moto = request.form.get('tipo_moto', '')
    precio_compra_raw = request.form.get('precio_compra')
    precio_venta_raw = request.form.get('precio_venta')
    file = request.files.get('imagen')

    errores, datos = _validar_datos_producto(
        None, nombre, categoria, tipo_moto, precio_compra_raw, precio_venta_raw, imagen_file=file, es_edicion=True
    )
    if errores:
        flash(' • '.join(errores), 'error')
        return redirect(url_for('bodega.inventario'))

    imagen_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('static', 'img', 'productos')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        imagen_url = f"/static/img/productos/{filename}"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if imagen_url:
            cursor.execute("""
                UPDATE Productos 
                SET Nombre = ?, Categoria = ?, TipoMoto = ?, PrecioCompra = ?, PrecioVenta = ?, ImagenURL = ?
                WHERE ProductoID = ?
            """, (datos['nombre'], datos['categoria'], datos['tipo_moto'], datos['precio_compra'], datos['precio_venta'], imagen_url, id))
        else:
            cursor.execute("""
                UPDATE Productos 
                SET Nombre = ?, Categoria = ?, TipoMoto = ?, PrecioCompra = ?, PrecioVenta = ?
                WHERE ProductoID = ?
            """, (datos['nombre'], datos['categoria'], datos['tipo_moto'], datos['precio_compra'], datos['precio_venta'], id))
        conn.commit()
        flash('Producto actualizado correctamente.', 'success')
    except Exception:
        conn.rollback()
        flash('No se pudo actualizar el producto. Verifica los datos ingresados.', 'error')
    finally:
        conn.close()
    return redirect(url_for('bodega.inventario'))

@bodega_bp.route('/producto/toggle/<int:id>', methods=['POST'])
@bodega_required
def toggle_producto(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Productos SET Activo = CASE WHEN Activo = 1 THEN 0 ELSE 1 END WHERE ProductoID = ?", (id,))
            conn.commit()
            flash("Estado del producto actualizado.", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            conn.close()
            
    return redirect(url_for('bodega.inventario'))

@bodega_bp.route('/producto/eliminar/<int:id>', methods=['POST'])
@bodega_required
def eliminar_producto(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Nombre FROM Productos WHERE ProductoID = ?", (id,))
            prod = cursor.fetchone()
            nombre = prod[0] if prod else "Producto"

            # Intentar borrado físico si no tiene referencias
            try:
                cursor.execute("DELETE FROM Productos WHERE ProductoID = ?", (id,))
                conn.commit()
                flash(f"Producto '{nombre}' eliminado exitosamente del inventario.", "success")
            except pyodbc.IntegrityError:
                # Si existen compras, ventas u órdenes vinculadas, aplicar borrado lógico seguro
                conn.rollback()
                cursor.execute("UPDATE Productos SET Activo = 0, MostrarEnCatalogo = 0 WHERE ProductoID = ?", (id,))
                conn.commit()
                flash(f"El producto '{nombre}' cuenta con movimientos históricos (compras, ventas u órdenes). Para garantizar la integridad contable, fue desactivado y retirado del catálogo.", "warning")
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f"Error al eliminar el producto: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('bodega.inventario'))


@bodega_bp.route('/compras', methods=['GET', 'POST'])
@bodega_required
def compras():
    conn = get_db_connection()
    
    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor_id')
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        
        if conn and proveedor_id and productos_ids:
            try:
                cursor = conn.cursor()
                # 1. Crear Orden de Compra
                cursor.execute("INSERT INTO Compras (ProveedorID, TotalCompra) VALUES (?, 0)", (proveedor_id,))
                cursor.execute("SELECT @@IDENTITY")
                compra_id = cursor.fetchone()[0]
                
                # 2. Insertar Detalles
                subtotal_calc = 0.0
                for pid, cant, prec in zip(productos_ids, cantidades, precios):
                    if pid and cant and prec:
                        c_val = int(cant)
                        p_val = float(prec)
                        subtotal_calc += (c_val * p_val)
                        cursor.execute("""
                            INSERT INTO DetalleCompra (CompraID, ProductoID, Cantidad, PrecioUnitarioCompra)
                            VALUES (?, ?, ?, ?)
                        """, (compra_id, pid, c_val, p_val))
                
                # 3. Asegurar Subtotal, IVA 15% y TotalCompra
                iva_calc = round(subtotal_calc * 0.15, 2)
                total_con_iva = round(subtotal_calc + iva_calc, 2)
                cursor.execute("""
                    UPDATE Compras
                    SET Subtotal = ?, IVA = ?, TotalCompra = ?
                    WHERE CompraID = ?
                """, (subtotal_calc, iva_calc, total_con_iva, compra_id))
                
                conn.commit()
                flash("Compra registrada exitosamente (+15% IVA aplicado). El stock y precios de costo han sido actualizados.", "success")
                return redirect(url_for('bodega.compras'))
            except Exception as e:
                conn.rollback()
                flash(f"Error al registrar la compra: {e}", "error")
    
    proveedores = []
    productos = []
    historial = []
    
    if conn:
        cursor = conn.cursor()
        
        # Proveedores (Si no hay, insertamos uno genérico por defecto para que funcione)
        cursor.execute("SELECT ProveedorID, NombreEmpresa FROM Proveedores ORDER BY NombreEmpresa ASC")
        proveedores = cursor.fetchall()
        if not proveedores:
            cursor.execute("INSERT INTO Proveedores (RUC, NombreEmpresa) VALUES ('GENERIC-001', 'Proveedor General')")
            conn.commit()
            cursor.execute("SELECT ProveedorID, NombreEmpresa FROM Proveedores")
            proveedores = cursor.fetchall()
            
        # Productos activos para el dropdown
        cursor.execute("SELECT ProductoID, CodigoSKU, Nombre, TipoMoto FROM Productos WHERE Activo = 1 ORDER BY Nombre ASC")
        productos = cursor.fetchall()
        
        # Historial de compras (ultimas 10) con Subtotal e IVA
        cursor.execute("""
            SELECT TOP 10 C.CompraID, P.NombreEmpresa, C.FechaCompra, C.TotalCompra, C.Subtotal, C.IVA
            FROM Compras C
            JOIN Proveedores P ON C.ProveedorID = P.ProveedorID
            ORDER BY C.FechaCompra DESC
        """)
        historial = cursor.fetchall()
        
        conn.close()
        
    prov_form = session.pop('prov_form_data', None)
    prov_error = session.pop('prov_form_error', None)
    return render_template(
        'bodega/compras.html',
        proveedores=proveedores,
        productos=productos,
        historial=historial,
        prov_form=prov_form,
        prov_error=prov_error,
    )


def _validar_datos_proveedor(nombre_raw, ruc_raw, telefono_raw, cursor=None):
    """
    Valida estrictamente Nombre/Razón Social, RUC y Teléfono de un proveedor
    antes de insertar en SQL Server.
    Retorna (nombre_limpio, ruc_limpio, telefono_limpio, error_msg).
    """
    nombre = re.sub(r'\s+', ' ', (nombre_raw or '').strip())
    ruc = re.sub(r'\s+', '', (ruc_raw or '').strip()).upper()
    telefono = re.sub(r'\s+', ' ', (telefono_raw or '').strip())

    # 1. Nombre / Razón Social
    if not nombre or len(nombre) < 3 or len(nombre) > 150:
        return None, None, None, "El nombre o razón social del proveedor es obligatorio y debe tener entre 3 y 150 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,&\-/()'°]+$", nombre):
        return None, None, None, "El nombre del proveedor contiene símbolos no permitidos."
    if len(re.findall(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', nombre)) < 2:
        return None, None, None, "El nombre o razón social debe incluir palabras reales con letras (no solo números o símbolos)."
    if re.search(r'(.)\1{3,}', nombre.lower().replace(' ', '')):
        return None, None, None, "Ingresa un nombre o razón social válido (evita caracteres repetidos sin sentido)."

    # 2. RUC Fiscal obligatorio (Unique NOT NULL en SQL Server)
    genericos_ruc = {'S/N', 'SN', 'NA', 'N/A', 'NONE', 'NINGUNO', 'SINRUC', 'GENERIC', 'GENERIC-001', '0', '00000000'}
    if not ruc or ruc in genericos_ruc:
        return None, None, None, "El número RUC del proveedor es obligatorio y debe ser un identificador real (ej. J0310000045821)."
    if len(ruc) < 8 or len(ruc) > 20 or not re.match(r'^[A-Z0-9\-]+$', ruc):
        return None, None, None, "El RUC debe tener entre 8 y 20 caracteres alfanuméricos válidos sin espacios ni símbolos especiales (ej. J0310000045821)."
    ruc_alnum = ruc.replace('-', '')
    digitos_ruc = re.findall(r'[0-9]', ruc_alnum)
    if len(digitos_ruc) < 6 or len(set(digitos_ruc)) < 2 or len(set(ruc_alnum)) <= 2:
        return None, None, None, "El formato del RUC no es válido; debe contener al menos 6 dígitos no repetitivos (ej. J0310000045821)."
    if ruc_alnum[0].isalpha() and not re.match(r'^[JECN][0-9]{9,19}$', ruc_alnum):
        return None, None, None, "Para RUC jurídico de Nicaragua inicia con J, E, C o N seguido de dígitos reales (ej. J0310000045821)."

    # 3. Teléfono de Contacto obligatorio (solo números, sin letras)
    if not telefono:
        return None, None, None, "El teléfono de contacto del proveedor es obligatorio."
    if re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', telefono):
        return None, None, None, "El teléfono no puede contener letras; ingresa únicamente números (ej. 2255-7800 o 8888-8888)."
    if not re.match(r'^[0-9+\-()\s]{8,20}$', telefono):
        return None, None, None, "El teléfono solo permite dígitos, espacios, guiones o prefijo internacional +."

    tel_digitos = re.sub(r'\D', '', telefono)
    if tel_digitos.startswith('505') and len(tel_digitos) == 11:
        tel_local = tel_digitos[3:]
    else:
        tel_local = tel_digitos

    if len(tel_local) == 8:
        if tel_local[0] not in ('2', '5', '7', '8'):
            return None, None, None, "En Nicaragua el teléfono fijo debe iniciar con 2 o el celular con 5, 7 u 8 (8 dígitos)."
        tel_fmt = f"{tel_local[:4]}-{tel_local[4:]}"
    elif 10 <= len(tel_digitos) <= 15:
        tel_fmt = telefono
    else:
        return None, None, None, "Ingresa un teléfono válido de Nicaragua (8 dígitos) o internacional (10 a 15 dígitos)."

    if len(set(tel_local)) == 1 or tel_local in ('12345678', '87654321', '01234567', '76543210'):
        return None, None, None, "Ingresa un número de teléfono real de la empresa (no dígitos repetidos ni secuencias ficticias)."

    # 4. Verificación de duplicados en base de datos antes del INSERT
    if cursor is not None:
        cursor.execute(
            "SELECT RUC, NombreEmpresa FROM Proveedores WHERE UPPER(REPLACE(RUC, '-', '')) = ? OR LOWER(LTRIM(RTRIM(NombreEmpresa))) = ?",
            (ruc_alnum, nombre.lower())
        )
        dup = cursor.fetchone()
        if dup:
            dup_ruc = re.sub(r'\s+', '', (dup[0] or '')).upper().replace('-', '')
            if dup_ruc == ruc_alnum:
                return None, None, None, f"Ya existe un proveedor registrado con el RUC {dup[0]} ({dup[1]})."
            return None, None, None, f"Ya existe un proveedor registrado con la razón social '{dup[1]}'."

    return nombre, ruc, tel_fmt, None


@bodega_bp.route('/proveedor/nuevo', methods=['POST'])
@bodega_required
def nuevo_proveedor():
    nombre_raw = request.form.get('nombre', '')
    ruc_raw = request.form.get('ruc', '')
    telefono_raw = request.form.get('telefono', '')

    def _fail_prov(msg):
        session['prov_form_data'] = {
            'nombre': nombre_raw.strip(),
            'ruc': ruc_raw.strip(),
            'telefono': telefono_raw.strip(),
        }
        session['prov_form_error'] = msg
        return redirect(url_for('bodega.compras'))

    conn = get_db_connection()
    if not conn:
        return _fail_prov("No se pudo conectar con la base de datos. Inténtalo nuevamente.")

    try:
        cursor = conn.cursor()
        nombre, ruc, telefono, error_msg = _validar_datos_proveedor(
            nombre_raw, ruc_raw, telefono_raw, cursor=cursor
        )
        if error_msg:
            return _fail_prov(error_msg)

        cursor.execute(
            "INSERT INTO Proveedores (RUC, NombreEmpresa, Telefono) VALUES (?, ?, ?)",
            (ruc, nombre, telefono)
        )
        conn.commit()
        flash(f"Proveedor '{nombre}' (RUC: {ruc}) registrado exitosamente.", "success")
    except pyodbc.IntegrityError:
        conn.rollback()
        return _fail_prov("Ya existe un proveedor registrado con ese RUC o razón social en el sistema.")
    except Exception:
        conn.rollback()
        return _fail_prov("No se pudo completar el registro del proveedor. Verifica los datos e inténtalo nuevamente.")
    finally:
        conn.close()

    return redirect(url_for('bodega.compras'))

@bodega_bp.route('/historial', methods=['GET'])
@bodega_required
def historial():
    conn = get_db_connection()
    historial_compras = []
    
    if conn:
        cursor = conn.cursor()
        
        # Obtener las compras ordenadas por fecha descendente con Subtotal e IVA
        cursor.execute("""
            SELECT C.CompraID, P.NombreEmpresa, C.FechaCompra, C.TotalCompra, U.NombreCompleto, C.Subtotal, C.IVA
            FROM Compras C
            JOIN Proveedores P ON C.ProveedorID = P.ProveedorID
            LEFT JOIN Usuarios U ON U.UsuarioID = 1
            ORDER BY C.FechaCompra DESC
        """)
        compras_rows = cursor.fetchall()
        
        for row in compras_rows:
            compra_id = row[0]
            
            # Obtener el detalle (productos) para esta compra
            cursor.execute("""
                SELECT Prod.Nombre, Prod.CodigoSKU, DC.Cantidad, DC.PrecioUnitarioCompra
                FROM DetalleCompra DC
                JOIN Productos Prod ON DC.ProductoID = Prod.ProductoID
                WHERE DC.CompraID = ?
            """, (compra_id,))
            detalles_rows = cursor.fetchall()
            
            detalles = []
            subtotal_detalles = 0.0
            for d in detalles_rows:
                st = float(d[2]) * float(d[3])
                subtotal_detalles += st
                detalles.append({
                    'nombre': d[0],
                    'sku': d[1],
                    'cantidad': d[2],
                    'precio_unitario': float(d[3]),
                    'subtotal': st
                })
                
            sub_val = float(row[5]) if len(row) > 5 and row[5] is not None else subtotal_detalles
            iva_val = float(row[6]) if len(row) > 6 and row[6] is not None else round(sub_val * 0.15, 2)
            tot_val = float(row[3]) if row[3] is not None else round(sub_val + iva_val, 2)
            
            historial_compras.append({
                'compra_id': row[0],
                'proveedor': row[1],
                'fecha': row[2],
                'subtotal': sub_val,
                'iva': iva_val,
                'total': tot_val,
                'detalles': detalles
            })
            
        conn.close()
        
    return render_template('bodega/historial.html', historial_compras=historial_compras)
