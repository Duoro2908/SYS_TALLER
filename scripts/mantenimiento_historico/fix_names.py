import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_db_connection

first_names = ["José", "Juan", "Carlos", "Luis", "Francisco", "Pedro", "Manuel", "Antonio", "Miguel", "Jorge", "Eduardo", "Mario", "Roberto", "Ricardo", "Julio", "César", "Víctor", "Daniel", "Rubén", "Ernesto", "Alejandro", "Javier", "Óscar", "Sergio", "Marcos", "Mauricio", "Guillermo"]

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute('SELECT ClienteID, NombreCompleto FROM Clientes')
clientes = cursor.fetchall()

for cliente in clientes:
    cliente_id = cliente[0]
    nombre_actual = cliente[1]
    
    parts = nombre_actual.strip().split()
    
    if len(parts) >= 3:
        # Assume first two are names, rest are surnames
        name1 = random.choice(first_names)
        name2 = random.choice([n for n in first_names if n != name1])
        surnames = " ".join(parts[2:])
        nuevo_nombre = f"{name1} {name2} {surnames}"
    elif len(parts) == 2:
        name1 = random.choice(first_names)
        name2 = random.choice([n for n in first_names if n != name1])
        nuevo_nombre = f"{name1} {name2} {parts[1]}"
    else:
        name1 = random.choice(first_names)
        name2 = random.choice([n for n in first_names if n != name1])
        nuevo_nombre = f"{name1} {name2} {nombre_actual}"
        
    print(f"Actualizando: '{nombre_actual}' -> '{nuevo_nombre}'")
    cursor.execute('UPDATE Clientes SET NombreCompleto = ? WHERE ClienteID = ?', (nuevo_nombre, cliente_id))

conn.commit()
conn.close()
print("Actualización completada.")
