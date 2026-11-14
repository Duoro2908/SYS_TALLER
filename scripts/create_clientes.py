import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

conn = database.get_db_connection()
cursor = conn.cursor()

clientes_data = [
    {
        "Identificacion": "001-120590-0023K",
        "NombreCompleto": "Roberto José Gómez Rivas",
        "Telefono": "+505 8845 1234",
        "Email": "roberto.gomez@gmail.com",
        "Moto": {
            "Placa": "M 145-892",
            "Marca": "Genesis",
            "Modelo": "KA 150",
            "Anio": 2023,
            "Cilindraje": 150
        }
    },
    {
        "Identificacion": "001-240885-0045B",
        "NombreCompleto": "María Auxiliadora López Martínez",
        "Telefono": "+505 8976 5432",
        "Email": "maria.lopez@yahoo.com",
        "Moto": {
            "Placa": "M 230-514",
            "Marca": "Genesis",
            "Modelo": "CR4 162",
            "Anio": 2024,
            "Cilindraje": 162
        }
    },
    {
        "Identificacion": "001-150993-0012P",
        "NombreCompleto": "Javier Antonio Blandón Cruz",
        "Telefono": "+505 8654 7890",
        "Email": "javier.blandon@gmail.com",
        "Moto": {
            "Placa": "M 089-331",
            "Marca": "Genesis",
            "Modelo": "SX2 250",
            "Anio": 2022,
            "Cilindraje": 250
        }
    },
    {
        "Identificacion": "001-080391-0034M",
        "NombreCompleto": "Ernesto Carlos Mendoza Solís",
        "Telefono": "+505 8432 1100",
        "Email": "ernesto.mendoza@outlook.com",
        "Moto": {
            "Placa": "M 177-640",
            "Marca": "Genesis",
            "Modelo": "SX3 250",
            "Anio": 2024,
            "Cilindraje": 250
        }
    },
    {
        "Identificacion": "001-301195-0067X",
        "NombreCompleto": "Silvia Elena Narváez Calero",
        "Telefono": "+505 8567 9922",
        "Email": "silvia.narvaez@gmail.com",
        "Moto": {
            "Placa": "M 312-708",
            "Marca": "Genesis",
            "Modelo": "GXT 200",
            "Anio": 2021,
            "Cilindraje": 200
        }
    }
]

print("--- Insertando / Actualizando 5 Clientes Fijos ---")
for c in clientes_data:
    cursor.execute("SELECT ClienteID FROM Clientes WHERE Identificacion = ? OR Telefono = ?", (c["Identificacion"], c["Telefono"]))
    row = cursor.fetchone()
    if row:
        cid = row[0]
        cursor.execute("""
            UPDATE Clientes 
            SET Identificacion = ?, NombreCompleto = ?, Telefono = ?, Email = ?
            WHERE ClienteID = ?
        """, (c["Identificacion"], c["NombreCompleto"], c["Telefono"], c["Email"], cid))
        print(f"Cliente actualizado ID {cid}: {c['NombreCompleto']}")
    else:
        cursor.execute("""
            INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email, CitasNoAsistidas)
            VALUES (?, ?, ?, ?, 0)
        """, (c["Identificacion"], c["NombreCompleto"], c["Telefono"], c["Email"]))
        cursor.execute("SELECT @@IDENTITY")
        cid = int(cursor.fetchone()[0])
        print(f"Cliente insertado ID {cid}: {c['NombreCompleto']}")
    
    # Insert or update Moto
    m = c["Moto"]
    cursor.execute("SELECT MotoID FROM Motocicletas WHERE ClienteID = ? AND Placa = ?", (cid, m["Placa"]))
    m_row = cursor.fetchone()
    if not m_row:
        cursor.execute("""
            INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cid, m["Placa"], m["Marca"], m["Modelo"], m["Anio"], m["Cilindraje"]))
        cursor.execute("SELECT @@IDENTITY")
        mid = int(cursor.fetchone()[0])
        print(f"  Moto registrada ID {mid}: {m['Marca']} {m['Modelo']} ({m['Placa']})")
    else:
        mid = m_row[0]
        print(f"  Moto ya existente ID {mid}: {m['Marca']} {m['Modelo']}")

conn.commit()

# Verificación
cursor.execute("""
    SELECT c.ClienteID, c.Identificacion, c.NombreCompleto, c.Telefono, m.Marca, m.Modelo, m.Placa
    FROM Clientes c
    LEFT JOIN Motocicletas m ON c.ClienteID = m.ClienteID
""")
print("\n--- Clientes en la Base de Datos ---")
for r in cursor.fetchall():
    print(r)

conn.close()
