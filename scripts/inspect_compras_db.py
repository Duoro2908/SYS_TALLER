import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cur = conn.cursor()
cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
tables = [r[0] for r in cur.fetchall()]
print('Tables in DB:', tables)

targets = ['Compras', 'DetalleCompra', 'Proveedores', 'Productos', 'Facturas', 'GastosOperativos', 'CuentasContablesAjustes']
for t in targets:
    if t in tables:
        cur.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{t}'")
        cols = [f"{c[0]} ({c[1]})" for c in cur.fetchall()]
        print(f"\n-- {t}:")
        print("  ", ", ".join(cols))

print("\n--- Proveedores actuales ---")
cur.execute("SELECT ProveedorID, NombreEmpresa, RUC, Telefono FROM Proveedores")
for r in cur.fetchall():
    print(r)

print("\n--- Compras actuales ---")
cur.execute("SELECT TOP 5 * FROM Compras")
for r in cur.fetchall():
    print(r)

print("\n--- DetalleCompra actual ---")
cur.execute("SELECT TOP 5 * FROM DetalleCompra")
for r in cur.fetchall():
    print(r)


conn.close()
