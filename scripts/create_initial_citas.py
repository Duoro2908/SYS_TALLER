import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from datetime import datetime

conn = database.get_db_connection()
cursor = conn.cursor()

# Get the clients and their motos
cursor.execute("""
    SELECT c.ClienteID, c.NombreCompleto, c.Telefono, m.MotoID, m.Modelo
    FROM Clientes c
    JOIN Motocicletas m ON c.ClienteID = m.ClienteID
    ORDER BY c.ClienteID ASC
""")
rows = cursor.fetchall()

sample_citas = [
    {
        "fecha": datetime(2026, 11, 6, 10, 0, 0),
        "tipo": "Preventivo",
        "estado": "Confirmada",
        "notas": "Cliente solicitó Aceite Motul 5100 y Filtro de Aire KA 150 original vía WhatsApp."
    },
    {
        "fecha": datetime(2026, 11, 6, 14, 30, 0),
        "tipo": "General",
        "estado": "Confirmada",
        "notas": "Revisión de pastillas de freno, carburación y ajuste de cadena."
    },
    {
        "fecha": datetime(2026, 11, 7, 9, 0, 0),
        "tipo": "Correctivo",
        "estado": "Pendiente",
        "notas": "Instalación de bujía Iridium, limpieza ultrasónica y filtro SX2."
    }
]

print("--- Insertando Citas Iniciales de WhatsApp ---")
for r, cita in zip(rows[:3], sample_citas):
    cid, nombre, tel, mid, mod = r[0], r[1], r[2], r[3], r[4]
    cursor.execute("""
        SELECT CitaID FROM CitasWhatsApp WHERE ClienteID = ? AND MotoID = ?
    """, (cid, mid))
    exist = cursor.fetchone()
    if not exist:
        cursor.execute("""
            INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado, Notas, Origen, FechaCreacion)
            VALUES (?, ?, ?, ?, ?, ?, 'WhatsApp', GETDATE())
        """, (cid, mid, cita["fecha"], cita["tipo"], cita["estado"], cita["notas"]))
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        print(f"Cita #{new_id} creada para {nombre} ({mod}) - {cita['estado']}")
    else:
        print(f"Cita ya existente para {nombre} (#{exist[0]})")

conn.commit()

cursor.execute("""
    SELECT cw.CitaID, c.NombreCompleto, m.Modelo, cw.FechaProgramada, cw.TipoMantenimiento, cw.Estado
    FROM CitasWhatsApp cw
    JOIN Clientes c ON cw.ClienteID = c.ClienteID
    JOIN Motocicletas m ON cw.MotoID = m.MotoID
""")
print("\n--- Citas WhatsApp en BD ---")
for r in cursor.fetchall():
    print(r)

conn.close()
