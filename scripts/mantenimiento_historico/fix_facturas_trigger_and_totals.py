import sys
sys.path.append(r"c:\Users\Alexander\OneDrive\Music\Documents\Taller CR")
from database import get_db_connection

conn = get_db_connection()
c = conn.cursor()

try:
    # 1. Update the trigger to NOT overwrite Facturas totals with bad math
    trigger_sql = """
    CREATE OR ALTER TRIGGER TRG_DetalleFactura_Operaciones 
    ON DetalleFactura AFTER INSERT AS
    BEGIN
        SET NOCOUNT ON;
        
        -- 1. Asignar costo de compra al repuesto vendido
        UPDATE DF
        SET DF.CostoCompraAplicado = P.PrecioCompra
        FROM DetalleFactura DF
        INNER JOIN inserted I ON DF.DetalleID = I.DetalleID
        INNER JOIN Productos P ON I.ProductoID = P.ProductoID
        WHERE I.ProductoID IS NOT NULL;

        -- 2. Descontar stock para ventas directas (donde OrdenID es NULL, ya que para órdenes de taller el stock se descuenta en OrdenRepuestos)
        UPDATE P 
        SET P.StockActual = P.StockActual - X.TotalVendido
        FROM Productos P 
        INNER JOIN (
            SELECT DF.ProductoID, SUM(DF.Cantidad) AS TotalVendido 
            FROM inserted DF
            INNER JOIN Facturas F ON DF.FacturaID = F.FacturaID
            WHERE DF.ProductoID IS NOT NULL AND F.OrdenID IS NULL
            GROUP BY DF.ProductoID
        ) X ON P.ProductoID = X.ProductoID;
        
        UPDATE Productos 
        SET MostrarEnCatalogo = 0 
        WHERE StockActual <= 0;
    END;
    """
    c.execute(trigger_sql)
    conn.commit()
    print("Trigger TRG_DetalleFactura_Operaciones updated successfully.")

    # 2. Fix corrupted workshop invoices (14, 18, 19, 1023, and any others)
    c.execute("SELECT FacturaID, OrdenID FROM Facturas WHERE OrdenID IS NOT NULL")
    workshop_invoices = c.fetchall()
    print(f"Checking {len(workshop_invoices)} workshop invoices...")

    for f_id, o_id in workshop_invoices:
        # Check labor
        c.execute("SELECT ISNULL(SUM(CostoSugerido), 0) FROM OrdenManoObra WHERE OrdenID = ?", (o_id,))
        mo_total = float(c.fetchone()[0] or 0)

        # Check parts
        c.execute("""
            SELECT ISNULL(SUM(r.Cantidad * p.PrecioVenta), 0)
            FROM OrdenRepuestos r JOIN Productos p ON r.ProductoID = p.ProductoID
            WHERE r.OrdenID = ?
        """, (o_id,))
        rep_total = float(c.fetchone()[0] or 0)

        total_neto = mo_total + rep_total
        if total_neto > 0:
            subtotal = total_neto / 1.15
            iva = total_neto - subtotal

            # Update Facturas
            c.execute("""
                UPDATE Facturas 
                SET SubTotal = ?, TotalIVA = ?, TotalNeto = ?
                WHERE FacturaID = ?
            """, (subtotal, iva, total_neto, f_id))

            # Insert missing Mano de Obra lines into DetalleFactura if not already present
            c.execute("SELECT COUNT(*) FROM DetalleFactura WHERE FacturaID = ? AND ProductoID IS NULL", (f_id,))
            has_mo_lines = c.fetchone()[0] > 0
            if not has_mo_lines and mo_total > 0:
                c.execute("SELECT DescripcionServicio, CostoSugerido FROM OrdenManoObra WHERE OrdenID = ?", (o_id,))
                mo_lines = c.fetchall()
                for desc, cost in mo_lines:
                    c.execute("""
                        INSERT INTO DetalleFactura (FacturaID, ProductoID, Descripcion, Cantidad, PrecioVentaAplicado)
                        VALUES (?, NULL, ?, 1, ?)
                    """, (f_id, f"{desc} (Mano de Obra)", cost))

            print(f"Factura {f_id} (Orden {o_id}): Total updated to C$ {total_neto:.2f} (MO: {mo_total:.2f}, Rep: {rep_total:.2f})")

    conn.commit()
    print("All workshop invoices fixed successfully!")

except Exception as e:
    conn.rollback()
    print("Error:", e)
finally:
    conn.close()
