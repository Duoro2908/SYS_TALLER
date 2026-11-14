import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import database
from PIL import Image

brain_dir = r"C:\Users\Alexander\.gemini\antigravity\brain\db715513-025f-49a7-8f5d-de983dda3004"
static_img_dir = r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\static\img"

images_map = {
    "filtro_aire_genesis_cr4.png": os.path.join(brain_dir, "filtro_aire_genesis_cr4_1793943702530.jpg"),
    "filtro_aire_genesis_sx1.png": os.path.join(brain_dir, "filtro_aire_genesis_sx1_1793943724297.jpg"),
    "filtro_aire_genesis_sx2.png": os.path.join(brain_dir, "filtro_aire_genesis_sx2_1793943733165.jpg"),
    "filtro_aire_genesis_sx3.png": os.path.join(brain_dir, "filtro_aire_genesis_sx3_250_1793943748687.jpg"),
    "filtro_aire_genesis_gxt200.png": os.path.join(brain_dir, "filtro_aire_genesis_gxt200_1793943755629.jpg"),
}

print("--- 1. Processing and copying images ---")
for target_name, src_path in images_map.items():
    dest_path = os.path.join(static_img_dir, target_name)
    if os.path.exists(src_path):
        img = Image.open(src_path)
        img.save(dest_path, "PNG", optimize=True)
        print(f"Saved {dest_path} (size: {os.path.getsize(dest_path)} bytes)")
    else:
        print(f"Warning: source {src_path} not found!")

products_to_add = [
    {
        "CodigoSKU": "FLT-AIR-CR4",
        "Nombre": "Filtro de Aire Génesis CR4 / CR4 V (AKT CR4)",
        "Categoria": "Repuestos",
        "TipoMoto": "Génesis CR4 125/150/162",
        "Descripcion": "Elemento filtrante rectangular con marco de polímero y papel microfiltrante de alta eficiencia para Génesis CR4 y CR4 V (equivalente AKT CR4 OEM 10006277).",
        "PrecioCompra": 110.00,
        "PrecioVenta": 180.00,
        "StockActual": 0,
        "ImagenURL": "/static/img/filtro_aire_genesis_cr4.png"
    },
    {
        "CodigoSKU": "FLT-AIR-SX1",
        "Nombre": "Filtro de Aire Génesis SX1 150 / 200",
        "Categoria": "Repuestos",
        "TipoMoto": "Génesis SX1 150/200",
        "Descripcion": "Filtro de aire lavable de espuma de doble densidad para moto todoterreno Génesis SX1 150cc y 200cc con aro de sujeción sellado.",
        "PrecioCompra": 120.00,
        "PrecioVenta": 190.00,
        "StockActual": 0,
        "ImagenURL": "/static/img/filtro_aire_genesis_sx1.png"
    },
    {
        "CodigoSKU": "FLT-AIR-SX2",
        "Nombre": "Filtro de Aire Génesis SX2 250 (Loncin LX250GY-3)",
        "Categoria": "Repuestos",
        "TipoMoto": "Génesis SX2 250",
        "Descripcion": "Cartucho cilíndrico de papel plisado microporoso con malla de protección metálica para Génesis SX2 250 (Loncin LX250GY-3).",
        "PrecioCompra": 140.00,
        "PrecioVenta": 220.00,
        "StockActual": 0,
        "ImagenURL": "/static/img/filtro_aire_genesis_sx2.png"
    },
    {
        "CodigoSKU": "FLT-AIR-SX3",
        "Nombre": "Filtro de Aire Génesis SX3 250 Enduro Pro",
        "Categoria": "Repuestos",
        "TipoMoto": "Génesis SX3 250",
        "Descripcion": "Filtro de aire de alto flujo tipo cartucho reforzado para Génesis SX3 250 Enduro con empaque perimetral de sellado hermético contra polvo y arena.",
        "PrecioCompra": 160.00,
        "PrecioVenta": 250.00,
        "StockActual": 0,
        "ImagenURL": "/static/img/filtro_aire_genesis_sx3.png"
    },
    {
        "CodigoSKU": "FLT-AIR-GXT200",
        "Nombre": "Filtro de Aire Génesis GXT 200 / QMR200 (Suzuki DR200)",
        "Categoria": "Repuestos",
        "TipoMoto": "Génesis GXT 200",
        "Descripcion": "Filtro de aire esponja bi-capa para motocicleta Génesis GXT 200 y Qingqi QMR200 (compatible plataforma Suzuki DR200). Lavable y reutilizable.",
        "PrecioCompra": 130.00,
        "PrecioVenta": 210.00,
        "StockActual": 0,
        "ImagenURL": "/static/img/filtro_aire_genesis_gxt200.png"
    }
]

print("\n--- 2. Database Insertion ---")
conn = database.get_db_connection()
cursor = conn.cursor()

# Ensure all current products have 0 stock
cursor.execute("UPDATE Productos SET StockActual = 0 WHERE StockActual != 0")
print(f"Updated existing products stock to 0: {cursor.rowcount} rows affected.")

for p in products_to_add:
    # Check if already exists
    cursor.execute("SELECT ProductoID FROM Productos WHERE CodigoSKU = ?", (p["CodigoSKU"],))
    row = cursor.fetchone()
    if row:
        prod_id = row[0]
        cursor.execute("""
            UPDATE Productos 
            SET Nombre = ?, Categoria = ?, TipoMoto = ?, Descripcion = ?, 
                PrecioCompra = ?, PrecioVenta = ?, StockActual = ?, ImagenURL = ?, 
                Activo = 1, MostrarEnCatalogo = 1
            WHERE ProductoID = ?
        """, (p["Nombre"], p["Categoria"], p["TipoMoto"], p["Descripcion"], 
              p["PrecioCompra"], p["PrecioVenta"], p["StockActual"], p["ImagenURL"], prod_id))
        print(f"Updated product ID {prod_id}: {p['CodigoSKU']} - {p['Nombre']}")
    else:
        cursor.execute("""
            INSERT INTO Productos 
            (CodigoSKU, Nombre, Categoria, TipoMoto, Descripcion, PrecioCompra, PrecioVenta, StockActual, ImagenURL, Activo, MostrarEnCatalogo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        """, (p["CodigoSKU"], p["Nombre"], p["Categoria"], p["TipoMoto"], p["Descripcion"], 
              p["PrecioCompra"], p["PrecioVenta"], p["StockActual"], p["ImagenURL"]))
        print(f"Inserted new product: {p['CodigoSKU']} - {p['Nombre']}")

conn.commit()

# Final Verification
cursor.execute("SELECT COUNT(*) FROM Productos WHERE StockActual > 0")
count_pos = cursor.fetchone()[0]
print(f"\nVerification: Products with Stock > 0: {count_pos}")

cursor.execute("SELECT ProductoID, CodigoSKU, Nombre, StockActual, PrecioCompra, PrecioVenta, ImagenURL FROM Productos WHERE CodigoSKU LIKE 'FLT-AIR-%'")
flt_rows = cursor.fetchall()
print(f"\nAll Génesis Air Filter Products ({len(flt_rows)}):")
for r in flt_rows:
    print(f"  ID {r[0]} | SKU: {r[1]} | Stock: {r[3]} | P.Compra: C$ {r[4]:.2f} | P.Venta: C$ {r[5]:.2f} | Img: {r[6]} | {r[2]}")

conn.close()
print("\nDone successfully!")
