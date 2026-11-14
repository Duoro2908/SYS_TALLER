import pyodbc
from config import Config

def fix_data():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # 1. Fix NS 200
        cursor.execute("UPDATE Motocicletas SET Modelo = 'SX2 200' WHERE Modelo = 'Pulsar NS 200'")
        
        # 2. Fix Female names to have exactly 3
        # I will fetch all clients.
        cursor.execute("SELECT ClienteID, NombreCompleto FROM Clientes")
        clientes = cursor.fetchall()
        
        # Lista exhaustiva de nombres de mujer nicaragüenses/latinos que podrían estar en la tabla
        nombres_mujer = [
            'Carmen', 'Rosa', 'Digna', 'Reyna', 'Esperanza', 'Yolanda', 'Melba', 'Heydi', 
            'Karla', 'Jenny', 'Suyapa', 'Elena', 'Flor', 'Indiana', 'Zeneyda', 'Verónica', 
            'Ana', 'Yesenia', 'Alba', 'Francis', 'Marlene', 'Isabel', 'Wendy', 'Lissette', 
            'Ximena', 'Urania', 'Gioconda'
        ]
        
        nombres_hombre_reemplazo = [
            'Carlos', 'Miguel', 'José', 'Luis', 'Juan', 'Jorge', 'Pedro', 'Roberto', 
            'Ricardo', 'Fernando', 'Mario', 'Sergio', 'Alejandro', 'Gabriel', 'Daniel'
        ]
        
        mujeres_encontradas = 0
        hombres_index = 0
        
        for c in clientes:
            cliente_id = c[0]
            nombre_completo = c[1]
            
            # Chequear si empieza con un nombre de mujer
            es_mujer = False
            for nm in nombres_mujer:
                if nombre_completo.startswith(nm):
                    es_mujer = True
                    break
            
            if es_mujer:
                mujeres_encontradas += 1
                if mujeres_encontradas > 3:
                    # Cambiar a nombre de hombre
                    partes = nombre_completo.split(' ', 1)
                    if len(partes) > 1:
                        nuevo_nombre = nombres_hombre_reemplazo[hombres_index % len(nombres_hombre_reemplazo)] + ' ' + partes[1]
                    else:
                        nuevo_nombre = nombres_hombre_reemplazo[hombres_index % len(nombres_hombre_reemplazo)] + ' Perez'
                    
                    cursor.execute("UPDATE Clientes SET NombreCompleto = ? WHERE ClienteID = ?", (nuevo_nombre, cliente_id))
                    hombres_index += 1

        conn.commit()
        print("Datos corregidos. Pulsar NS 200 eliminada y dejadas solo 3 mujeres.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_data()
