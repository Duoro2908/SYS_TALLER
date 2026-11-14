import pyodbc
from database import get_db_connection

def cleanup_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tables that represent an "action" by a client:
    # 1. Facturas (ClienteID)
    # 2. VentasRecibidas (ClienteID)
    # 3. CitasWhatsApp (ClienteID)
    # 4. MensajesWhatsApp (ClienteID)
    # 5. AtencionTickets (ClienteID)
    # 6. Motocicletas (ClienteID) -> but we only care if the motorcycle has an OrdenTrabajo? 
    # Let's say if they have a motorcycle, that's an action. Or better: if they have an OrdenTrabajo, that's an action.
    # OrdenTrabajo doesn't have ClienteID directly, it's linked through Motocicletas.
    
    query = """
    SELECT ClienteID FROM Clientes
    WHERE ClienteID NOT IN (
        SELECT DISTINCT ClienteID FROM Facturas WHERE ClienteID IS NOT NULL
        UNION
        SELECT DISTINCT ClienteID FROM VentasRecibidas WHERE ClienteID IS NOT NULL
        UNION
        SELECT DISTINCT ClienteID FROM CitasWhatsApp WHERE ClienteID IS NOT NULL
        UNION
        SELECT DISTINCT ClienteID FROM MensajesWhatsApp WHERE ClienteID IS NOT NULL
        UNION
        SELECT DISTINCT ClienteID FROM AtencionTickets WHERE ClienteID IS NOT NULL
        UNION
        SELECT DISTINCT M.ClienteID FROM Motocicletas M 
        JOIN OrdenesTrabajo O ON M.MotoID = O.MotoID
        WHERE M.ClienteID IS NOT NULL
    )
    """
    
    cursor.execute(query)
    clients_to_delete = cursor.fetchall()
    
    print(f"Encontrados {len(clients_to_delete)} clientes sin actividad (sin facturas, ventas, citas, mensajes, tickets, ni órdenes de trabajo).")
    
    if clients_to_delete:
        ids = [str(c[0]) for c in clients_to_delete]
        print("IDs a borrar:", ids)
        
        # We need to delete their motorcycles first if they have any without orders
        # (Though if they are in the list, their motorcycles have no orders, so they are safe to delete)
        cursor.execute(f"DELETE FROM Motocicletas WHERE ClienteID IN ({','.join(ids)})")
        
        # Now delete the clients
        cursor.execute(f"DELETE FROM Clientes WHERE ClienteID IN ({','.join(ids)})")
        conn.commit()
        print("Clientes eliminados con éxito.")
    
    conn.close()

if __name__ == '__main__':
    cleanup_clients()
