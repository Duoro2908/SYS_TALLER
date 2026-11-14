import sys
sys.path.append(r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR")
from app import app
from config import Config
from database import get_db_connection

print(f"Config COMPANY_RUC: {Config.COMPANY_RUC}")
assert Config.COMPANY_RUC == 'J0310000123456', "Company RUC mismatch!"

# Test database query directly
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 FacturaID FROM Facturas ORDER BY FacturaID DESC")
row = cursor.fetchone()
if not row:
    print("No invoices found to test.")
    sys.exit(0)

factura_id = row[0]
print(f"Testing with FacturaID: {factura_id}")

cursor.execute("""
    SELECT F.FacturaID, F.NumeroFactura, F.FechaEmision, F.SubTotal, F.TotalIVA, F.TotalNeto, F.MetodoPago, F.DescuentoAplicado,
           COALESCE(C.NombreCompleto, CM.NombreCompleto) AS ClienteFijo, 
           F.NombreClienteDePaso,
           O.OrdenID,
           COALESCE(C.Identificacion, CM.Identificacion, F.RUCCliente) AS ClienteIdentificacion,
           ISNULL(F.RUC_Emisor, ?) AS RUCEmisor,
           COALESCE(C.Telefono, CM.Telefono) AS ClienteTelefono
    FROM Facturas F
    LEFT JOIN Clientes C ON F.ClienteID = C.ClienteID
    LEFT JOIN OrdenesTrabajo O ON F.OrdenID = O.OrdenID
    LEFT JOIN Motocicletas M ON O.MotoID = M.MotoID
    LEFT JOIN Clientes CM ON M.ClienteID = CM.ClienteID
    WHERE F.FacturaID = ?
""", (Config.COMPANY_RUC, factura_id))
factura_data = cursor.fetchone()
conn.close()

print(f"Fetched factura: {factura_data}")
assert factura_data[12] == 'J0310000123456', f"Expected RUC J0310000123456, got {factura_data[12]}"

# Test with Flask test_client
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['rol_id'] = 1
        sess['username'] = 'admin'

    # Test factura_digital
    resp = client.get(f'/caja/factura_digital/{factura_id}')
    print(f"GET /caja/factura_digital/{factura_id} -> Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    html = resp.get_data(as_text=True)
    assert 'J0310000123456' in html, "RUC J0310000123456 not in factura HTML!"
    assert 'RUC DGI:' in html, "'RUC DGI:' not in factura HTML!"
    assert 'Comprobante Fiscal DGI' in html, "'Comprobante Fiscal DGI' not in HTML!"
    assert 'Dirección General de Ingresos (DGI)' in html, "'Dirección General de Ingresos (DGI)' not in HTML!"
    print("[OK] Factura Digital HTML includes RUC DGI and fiscal legend properly.")

    # Test facturas list
    resp_list = client.get('/caja/facturas')
    print(f"GET /caja/facturas -> Status: {resp_list.status_code}")
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}"
    html_list = resp_list.get_data(as_text=True)
    assert 'RUC DGI' in html_list, "'RUC DGI' column header not in facturas list!"
    assert 'J0310000123456' in html_list, "RUC J0310000123456 not in facturas list!"
    print("[OK] Facturas list includes RUC DGI column and badge properly.")

print("ALL TESTS PASSED SUCCESSFULLY!")
