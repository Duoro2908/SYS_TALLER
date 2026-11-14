import pyodbc
from config import Config

def delete_all_inventory():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        print("Borrando dependencias de productos...")
        cursor.execute("DISABLE TRIGGER TRG_DetalleFactura_Inmutable ON DetalleFactura")
        cursor.execute("DELETE FROM DetalleFactura")
        cursor.execute("ENABLE TRIGGER TRG_DetalleFactura_Inmutable ON DetalleFactura")
        
        cursor.execute("DELETE FROM OrdenRepuestos")
        cursor.execute("DELETE FROM DetallePedidosInventario")
        cursor.execute("DELETE FROM AjustesInventario")
        
        print("Borrando todos los productos del inventario...")
        cursor.execute("DELETE FROM Productos")
        
        # Resetear el contador de Identity para que los nuevos productos empiecen en 1
        print("Reseteando el identificador (ProductoID)...")
        cursor.execute("DBCC CHECKIDENT ('Productos', RESEED, 0)")
        
        conn.commit()
        print("¡El inventario ha sido eliminado completamente de la base de datos!")
        conn.close()
    except pyodbc.Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    delete_all_inventory()
