import os

path = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\routes\contador.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix IVA credito calculation to use ISNULL(IVA, TotalCompra * 0.15)
old_iva = 'cursor.execute("SELECT ISNULL(SUM(TotalCompra * 0.15), 0) FROM Compras WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?", (mes, anio))'
new_iva = 'cursor.execute("SELECT ISNULL(SUM(ISNULL(IVA, TotalCompra * 0.15)), 0) FROM Compras WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?", (mes, anio))'

# 2. Fix prov_val to read from Compras
old_prov = """        # BALANCE GENERAL - PASIVOS CORRIENTES
        prov_val = 0.0"""
new_prov = """        # BALANCE GENERAL - PASIVOS CORRIENTES
        cursor.execute("SELECT ISNULL(SUM(TotalCompra), 0) FROM Compras WHERE MONTH(FechaCompra) = ? AND YEAR(FechaCompra) = ?", (mes, anio))
        prov_compras_row = cursor.fetchone()
        prov_val = float(prov_compras_row[0] or 0.0) if prov_compras_row else 0.0"""

if old_iva in content:
    content = content.replace(old_iva, new_iva, 1)
    print("Replaced old_iva")
else:
    print("old_iva not found")

# Normalize newlines for prov replacement
if "prov_val = 0.0" in content:
    content = content.replace(
        "        # BALANCE GENERAL - PASIVOS CORRIENTES\n        prov_val = 0.0",
        new_prov
    )
    if new_prov not in content:
        content = content.replace(
            "        # BALANCE GENERAL - PASIVOS CORRIENTES\r\n        prov_val = 0.0",
            new_prov.replace("\n", "\r\n")
        )
    print("Replaced prov_val")
else:
    print("prov_val = 0.0 not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated routes/contador.py successfully.")

