import sys, os
sys.path.insert(0, os.path.abspath('.'))
from database import get_db_connection

conn = get_db_connection()
if conn:
    c = conn.cursor()
    c.execute("SELECT ClienteID, NombreCompleto, Telefono FROM Clientes WHERE NombreCompleto LIKE 'Cliente WA%'")
    rows = c.fetchall()
    print(f"Total 'Cliente WA' encontrados: {len(rows)}")
    for r in rows:
        print(f"ID={r[0]}, Nombre={r[1]}, Tel={r[2]}")
    
    # Check dependencies before deleting
    wa_ids = [r[0] for r in rows]
    if wa_ids:
        placeholders = ','.join('?' for _ in wa_ids)
        c.execute(f"DELETE FROM CitasWhatsApp WHERE ClienteID IN ({placeholders})", tuple(wa_ids))
        c.execute(f"DELETE FROM Motocicletas WHERE ClienteID IN ({placeholders})", tuple(wa_ids))
        c.execute(f"DELETE FROM Clientes WHERE ClienteID IN ({placeholders})", tuple(wa_ids))
        conn.commit()
        print("Registros de 'Cliente WA' eliminados de la base de datos.")
    else:
        print("No hay registros que eliminar.")
    conn.close()
