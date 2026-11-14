import pyodbc
from config import Config

def update_catalogo():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Primero vaciamos o eliminamos los anteriores (si es que no están vinculados)
        try:
            cursor.execute("DELETE FROM CatalogoMantenimientos")
        except Exception:
            print("No se pudo vaciar la tabla por constraints, vamos a hacer UPDATE o INSERT uno por uno")
        
        # Mantenimiento Preventivo 100-250cc
        cursor.execute("""
            IF EXISTS(SELECT 1 FROM CatalogoMantenimientos WHERE Tipo = 'Preventivo')
                UPDATE CatalogoMantenimientos SET PrecioBase = 900, DescripcionDetallada = 'Limpieza, engrasado, cambio de aceite, revisión filtro.' WHERE Tipo = 'Preventivo'
            ELSE
                INSERT INTO CatalogoMantenimientos (Tipo, DescripcionDetallada, PrecioBase) VALUES ('Preventivo', 'Limpieza, engrasado, cambio de aceite, revisión filtro.', 900)
        """)
        
        # Mantenimiento General / Full
        cursor.execute("""
            IF EXISTS(SELECT 1 FROM CatalogoMantenimientos WHERE Tipo = 'General')
                UPDATE CatalogoMantenimientos SET PrecioBase = 1800, DescripcionDetallada = 'Incluye barras y poste.' WHERE Tipo = 'General'
            ELSE
                INSERT INTO CatalogoMantenimientos (Tipo, DescripcionDetallada, PrecioBase) VALUES ('General', 'Incluye barras y poste.', 1800)
        """)
        
        # Express (Precio Variable / 0 inicial)
        cursor.execute("""
            IF EXISTS(SELECT 1 FROM CatalogoMantenimientos WHERE Tipo = 'Express')
                UPDATE CatalogoMantenimientos SET PrecioBase = 0, DescripcionDetallada = 'Servicio rápido, cambio específico.' WHERE Tipo = 'Express'
            ELSE
                INSERT INTO CatalogoMantenimientos (Tipo, DescripcionDetallada, PrecioBase) VALUES ('Express', 'Servicio rápido, cambio específico.', 0)
        """)

        conn.commit()
        print("Catálogo de mantenimientos actualizado.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_catalogo()
