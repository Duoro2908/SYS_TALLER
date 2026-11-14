import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_connection

def add_spark_plugs():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
        
    cursor = conn.cursor()
    
    plugs = [
        {
            'sku': 'SP-DENSO-01',
            'categoria': 'Repuestos',
            'nombre': 'Chispero Denso Iridium Racing',
            'descripcion': 'Chispero de alta durabilidad y rendimiento, marca Denso Iridium Racing para motocicletas.',
            'precio_compra': 5000,
            'precio_venta': 8500,
            'stock': 20,
            'imagen': '/static/img/chispero_denso.png'
        },
        {
            'sku': 'SP-NGK-02',
            'categoria': 'Repuestos',
            'nombre': 'Chispero NGK C7HSA',
            'descripcion': 'Chispero estándar de buena calidad y durabilidad, marca NGK para motos.',
            'precio_compra': 2500,
            'precio_venta': 4500,
            'stock': 35,
            'imagen': '/static/img/chispero_ngk.png'
        },
        {
            'sku': 'SP-CHAMPION-03',
            'categoria': 'Repuestos',
            'nombre': 'Chispero Champion Power Sport',
            'descripcion': 'Chispero confiable para motos, marca Champion Power Sport. Más potencia, menos empastamiento.',
            'precio_compra': 3000,
            'precio_venta': 5500,
            'stock': 30,
            'imagen': '/static/img/chispero_champion.png'
        }
    ]
    
    for p in plugs:
        # Check if exists
        cursor.execute("SELECT ProductoID FROM Productos WHERE CodigoSKU = ?", (p['sku'],))
        if cursor.fetchone():
            print(f"Producto {p['sku']} ya existe. Actualizando...")
            cursor.execute("""
                UPDATE Productos
                SET Nombre = ?, Descripcion = ?, ImagenURL = ?
                WHERE CodigoSKU = ?
            """, (p['nombre'], p['descripcion'], p['imagen'], p['sku']))
        else:
            print(f"Insertando {p['sku']}...")
            cursor.execute("""
                INSERT INTO Productos (CodigoSKU, Categoria, Nombre, Descripcion, PrecioCompra, PrecioVenta, StockActual, ImagenURL, MostrarEnCatalogo, Activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
            """, (p['sku'], p['categoria'], p['nombre'], p['descripcion'], p['precio_compra'], p['precio_venta'], p['stock'], p['imagen']))
            
    conn.commit()
    conn.close()
    print("Motos spark plugs added/updated successfully.")

if __name__ == '__main__':
    add_spark_plugs()
