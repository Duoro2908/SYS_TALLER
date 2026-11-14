import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from datetime import datetime

conn = database.get_db_connection()
cursor = conn.cursor()

print("--- 1. Verificando o Registrando Proveedores Oficiales ---")
# Proveedor Génesis
cursor.execute("SELECT ProveedorID FROM Proveedores WHERE NombreEmpresa LIKE '%Genesis%' OR NombreEmpresa LIKE '%Génesis%'")
row_gen = cursor.fetchone()
if not row_gen:
    cursor.execute("""
        INSERT INTO Proveedores (RUC, NombreEmpresa, Telefono, DiasCredito)
        VALUES ('J0310000045821', 'Distribuidora Génesis de Nicaragua S.A.', '2255-7800', 30)
    """)
    cursor.execute("SELECT @@IDENTITY")
    prov_genesis_id = int(cursor.fetchone()[0])
    print(f"Creado Proveedor Génesis ID: {prov_genesis_id}")
else:
    prov_genesis_id = int(row_gen[0])
    print(f"Proveedor Génesis existente ID: {prov_genesis_id}")

# Proveedor Imgesa
cursor.execute("SELECT ProveedorID FROM Proveedores WHERE NombreEmpresa LIKE '%Imgesa%'")
row_img = cursor.fetchone()
if not row_img:
    cursor.execute("""
        INSERT INTO Proveedores (RUC, NombreEmpresa, Telefono, DiasCredito)
        VALUES ('J0310000000000', 'Imgesa / Lubricantes Internacionales S.A.', '2222-2222', 30)
    """)
    cursor.execute("SELECT @@IDENTITY")
    prov_imgesa_id = int(cursor.fetchone()[0])
    print(f"Creado Proveedor Imgesa ID: {prov_imgesa_id}")
else:
    prov_imgesa_id = int(row_img[0])
    print(f"Proveedor Imgesa existente ID: {prov_imgesa_id}")

print("\n--- 2. Obteniendo Productos ---")
cursor.execute("SELECT ProductoID, CodigoSKU, Nombre, PrecioCompra, PrecioVenta FROM Productos WHERE Activo = 1")
all_products = cursor.fetchall()

genesis_filters = [p for p in all_products if p[1].startswith('FLT-AIR-')]
lubricants_spark = [p for p in all_products if not p[1].startswith('FLT-AIR-')]

print(f"Filtros Génesis encontrados: {len(genesis_filters)}")
print(f"Lubricantes y Bujías encontrados: {len(lubricants_spark)}")

fecha_compra = datetime(2026, 11, 4, 10, 30, 0)

# 3. Registrar Compra 1: Filtros de Aire Génesis (10 unidades cada uno)
print("\n--- 3. Registrando Factura de Compra Génesis ---")
cursor.execute("""
    INSERT INTO Compras (ProveedorID, FechaCompra, Subtotal, IVA, TotalCompra)
    VALUES (?, ?, 0, 0, 0)
""", (prov_genesis_id, fecha_compra))
cursor.execute("SELECT @@IDENTITY")
compra_gen_id = int(cursor.fetchone()[0])

subtotal_gen = 0.0
for p in genesis_filters:
    pid = p[0]
    p_compra = float(p[3] or 110.0)
    cant = 10
    subtotal_gen += (cant * p_compra)
    cursor.execute("""
        INSERT INTO DetalleCompra (CompraID, ProductoID, Cantidad, PrecioUnitarioCompra)
        VALUES (?, ?, ?, ?)
    """, (compra_gen_id, pid, cant, p_compra))
    cursor.execute("UPDATE Productos SET StockActual = 10 WHERE ProductoID = ?", (pid,))

iva_gen = round(subtotal_gen * 0.15, 2)
total_gen = round(subtotal_gen + iva_gen, 2)
cursor.execute("""
    UPDATE Compras 
    SET Subtotal = ?, IVA = ?, TotalCompra = ?
    WHERE CompraID = ?
""", (subtotal_gen, iva_gen, total_gen, compra_gen_id))
print(f"Compra Génesis ID #{compra_gen_id} registrada: Subtotal C$ {subtotal_gen:.2f}, IVA C$ {iva_gen:.2f}, Total C$ {total_gen:.2f}")

# 4. Registrar Compra 2: Lubricantes y Bujías Imgesa (10 unidades cada uno)
print("\n--- 4. Registrando Factura de Compra Imgesa ---")
fecha_compra_img = datetime(2026, 11, 4, 11, 15, 0)
cursor.execute("""
    INSERT INTO Compras (ProveedorID, FechaCompra, Subtotal, IVA, TotalCompra)
    VALUES (?, ?, 0, 0, 0)
""", (prov_imgesa_id, fecha_compra_img))
cursor.execute("SELECT @@IDENTITY")
compra_img_id = int(cursor.fetchone()[0])

subtotal_img = 0.0
for p in lubricants_spark:
    pid = p[0]
    p_compra = float(p[3] or 200.0)
    # Fix ID 12 if PrecioCompra was 1.00
    if p[1] == 'LUB-HAVOLINE-SYNBLEND-10W40' and p_compra < 50:
        p_compra = 250.0
        cursor.execute("UPDATE Productos SET PrecioCompra = 250.00 WHERE ProductoID = ?", (pid,))
    cant = 10
    subtotal_img += (cant * p_compra)
    cursor.execute("""
        INSERT INTO DetalleCompra (CompraID, ProductoID, Cantidad, PrecioUnitarioCompra)
        VALUES (?, ?, ?, ?)
    """, (compra_img_id, pid, cant, p_compra))
    cursor.execute("UPDATE Productos SET StockActual = 10 WHERE ProductoID = ?", (pid,))

iva_img = round(subtotal_img * 0.15, 2)
total_img = round(subtotal_img + iva_img, 2)
cursor.execute("""
    UPDATE Compras 
    SET Subtotal = ?, IVA = ?, TotalCompra = ?
    WHERE CompraID = ?
""", (subtotal_img, iva_img, total_img, compra_img_id))
print(f"Compra Imgesa ID #{compra_img_id} registrada: Subtotal C$ {subtotal_img:.2f}, IVA C$ {iva_img:.2f}, Total C$ {total_img:.2f}")

conn.commit()

# Verificaciones
print("\n--- 5. Verificación de Stock Actual ---")
cursor.execute("SELECT COUNT(*) FROM Productos WHERE StockActual != 10")
count_diff = cursor.fetchone()[0]
print(f"Productos con stock diferente a 10: {count_diff}")

cursor.execute("SELECT SUM(StockActual * PrecioCompra), COUNT(*) FROM Productos WHERE Activo = 1")
row_inv = cursor.fetchone()
print(f"Total Valor de Inventario al Costo: C$ {row_inv[0]:,.2f} ({row_inv[1]} productos con stock)")

cursor.execute("SELECT CompraID, FechaCompra, Subtotal, IVA, TotalCompra FROM Compras ORDER BY CompraID DESC")
for c in cursor.fetchall():
    print(f"  Factura Compra OC #{c[0]} | Fecha: {c[1]} | Subtotal: C$ {c[2]:,.2f} | IVA: C$ {c[3]:,.2f} | Total: C$ {c[4]:,.2f}")

conn.close()
print("\nProceso de compras completado con éxito.")

