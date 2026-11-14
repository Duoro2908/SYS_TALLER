import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

def reiniciar_datos_prueba():
    conn = get_db_connection()
    if not conn:
        print("ERROR: No se pudo conectar a la Base de Datos.")
        return False
    
    cursor = conn.cursor()
    print("Iniciando depuración completa y reinicio de registros de prueba...\n")
    
    triggers = [
        ("DetalleFactura", "TRG_DetalleFactura_Inmutable"),
        ("DetalleFactura", "TRG_DetalleFactura_Operaciones"),
        ("Facturas", "TRG_Facturas_Actualizacion"),
        ("CitasWhatsApp", "TRG_Citas_PenalizarAusencia"),
        ("DetalleCompra", "TRG_Compras_AumentarStock"),
        ("OrdenRepuestos", "TRG_OrdenRepuestos_Stock")
    ]
    
    try:
        # 1. Desactivar triggers
        for table, trg in triggers:
            cursor.execute(f"DISABLE TRIGGER [{trg}] ON [{table}]")
            print(f"[TRIGGER] Desactivado: {trg} en {table}")
            
        # 2. Desactivar Foreign Keys temporalmente
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
        print("[CONSTRAINTS] Restricciones FK desactivadas temporalmente.")
        
        # 3. Vaciar tablas de prueba en orden
        tablas = [
            "DetalleFactura",
            "Facturas",
            "DetalleVentasRecibidas",
            "VentasRecibidas",
            "OrdenManoObra",
            "OrdenRepuestos",
            "OrdenesTrabajo",
            "MensajesWhatsApp",
            "CitasWhatsApp",
            "Motocicletas",
            "Clientes",
            "DetalleCompra",
            "Compras",
            "GastosOperativos",
            "ControlCaja",
            "AtencionTickets",
            "NovedadesNomina",
            "CierresMensualesNomina",
            "CuentasContablesAjustes",
            "ReportesContables",
            "RifaPremios"
        ]
        
        for table in tablas:
            cursor.execute(f"DELETE FROM [{table}]")
            print(f"[DELETE] Vaciada tabla: {table}")
            
        # 4. Reseed de Identity
        reseed_tables = [
            "DetalleFactura", "Facturas", "DetalleVentasRecibidas", "VentasRecibidas",
            "OrdenManoObra", "OrdenRepuestos", "OrdenesTrabajo", "CitasWhatsApp",
            "Motocicletas", "Clientes", "DetalleCompra", "Compras", "GastosOperativos",
            "ControlCaja", "AtencionTickets", "NovedadesNomina"
        ]
        for table in reseed_tables:
            try:
                cursor.execute(f"DBCC CHECKIDENT ('{table}', RESEED, 0)")
            except Exception:
                pass
                
        # 5. Reactivar Foreign Keys con verificación
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'")
        print("[CONSTRAINTS] Restricciones FK reactivadas con integridad completa.")
        
        # 6. Reactivar triggers
        for table, trg in triggers:
            cursor.execute(f"ENABLE TRIGGER [{trg}] ON [{table}]")
            print(f"[TRIGGER] Reactivado: {trg} en {table}")
            
        conn.commit()
        print("\n=== ÉXITO TOTAL: Base de Datos reiniciada y lista para operación formal ===")
        
        # Resumen final
        print("\n--- RESUMEN DE TABLAS EMPRESARIALES (CONSERVADAS) ---")
        conservadas = ["Productos", "Proveedores", "CatalogoMantenimientos", "Roles", "Usuarios", "ContratosLaborales", "ConfiguracionWhatsApp"]
        for t in conservadas:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cursor.fetchone()[0]
            print(f"  * {t}: {cnt} registros (CONSERVADO)")
            
        print("\n--- RESUMEN DE REGISTROS DE PRUEBA (LIMPIOS) ---")
        for t in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cursor.fetchone()[0]
            print(f"  * {t}: {cnt} registros")
            
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        # Intentar reactivar triggers si falló
        for table, trg in triggers:
            try:
                cursor.execute(f"ENABLE TRIGGER [{trg}] ON [{table}]")
            except Exception:
                pass
        return False
    finally:
        conn.close()
        
    return True

if __name__ == '__main__':
    reiniciar_datos_prueba()
