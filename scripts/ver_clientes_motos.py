import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT ClienteID, NombreCompleto, Telefono FROM Clientes")
print("CLIENTES:")
for r in cursor.fetchall():
    print(r)

cursor.execute("SELECT MotoID, ClienteID, Marca, Modelo, Placa FROM Motocicletas")
print("\nMOTOCICLETAS:")
for r in cursor.fetchall():
    print(r)

cursor.execute("SELECT GastoID, Concepto, Monto, FechaGasto FROM GastosOperativos")
print("\nGASTOS OPERATIVOS:")
for r in cursor.fetchall():
    print(r)

cursor.execute("SELECT TicketID, NombreCliente, Telefono, Asunto FROM AtencionTickets")
print("\nATENCION TICKETS:")
for r in cursor.fetchall():
    print(r)

conn.close()

