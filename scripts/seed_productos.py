import pyodbc
from config import Config

def seed_genesis_products():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        print("Obteniendo ProveedorID de Imgesa...")
        cursor.execute("SELECT ProveedorID FROM Proveedores WHERE NombreEmpresa = 'Imgesa'")
        imgesa = cursor.fetchone()
        proveedor_id = imgesa[0] if imgesa else None

        if not proveedor_id:
            print("No se encontró Imgesa. Abortando seed.")
            return

        productos = [
            (
                'GEN-GXT-001', 'Filtros', 'Filtro de Aire Genesis GXT 200', 
                'Filtro de aire original de esponja para GXT 200 / GXT 250.',
                12.50, 18.00, 15, 
                'https://m.media-amazon.com/images/I/71u9sW4jUeL._AC_SL1500_.jpg', proveedor_id
            ),
            (
                'GEN-HJ-002', 'Fricciones', 'Fricciones de Freno Delantero HJ125', 
                'Pastillas de freno originales para Genesis HJ125 Sport.',
                8.00, 15.00, 30, 
                'https://m.media-amazon.com/images/I/61r598H0wFL._AC_SL1500_.jpg', proveedor_id
            ),
            (
                'NGK-D8EA', 'Bujías', 'Bujía NGK D8EA', 
                'Bujía estándar NGK recomendada para motores 200cc y 250cc de Genesis.',
                3.50, 6.00, 50, 
                'https://m.media-amazon.com/images/I/61O0vYF1f9L._AC_SL1500_.jpg', proveedor_id
            ),
            (
                'MOT-20W50', 'Lubricantes', 'Aceite Motul 3000 20W50 4T (1L)', 
                'Aceite mineral para motor de 4 tiempos. Ideal para motos Genesis de trabajo y doble propósito.',
                7.00, 12.00, 40, 
                'https://m.media-amazon.com/images/I/61Sj2oZ93TL._AC_SL1500_.jpg', proveedor_id
            ),
            (
                'GEN-GXT-005', 'Kits de Arrastre', 'Kit de Arrastre GXT 200 (Cadena, Sprocket)', 
                'Kit completo original de transmisión para Genesis GXT 200.',
                25.00, 40.00, 10, 
                'https://m.media-amazon.com/images/I/71N-d5PibqL._AC_SL1500_.jpg', proveedor_id
            )
        ]

        print("Insertando productos Genesis...")
        for p in productos:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM Productos WHERE CodigoSKU = ?)
                BEGIN
                    INSERT INTO Productos (CodigoSKU, Categoria, Nombre, Descripcion, PrecioCompra, PrecioVenta, StockActual, ImagenURL, ProveedorID, MostrarEnCatalogo, Activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                END
            """, (p[0],) + p)

        conn.commit()
        print("Productos insertados correctamente sin borrar nada.")
        conn.close()
    except pyodbc.Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    seed_genesis_products()
