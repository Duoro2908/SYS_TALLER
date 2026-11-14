import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def setup_whatsapp_tables():
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos SQL Server.")
        return False
        
    try:
        cursor = conn.cursor()
        print("[OK] Conectado a la base de datos SQL Server.")
        
        # 1. Verificar/Crear CitasWhatsApp
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CitasWhatsApp'")
        citas_exists = cursor.fetchone()[0]
        
        if citas_exists == 0:
            print("[INFO] Creando tabla CitasWhatsApp...")
            cursor.execute("""
                CREATE TABLE CitasWhatsApp (
                    CitaID INT IDENTITY(1,1) PRIMARY KEY,
                    ClienteID INT FOREIGN KEY REFERENCES Clientes(ClienteID),
                    MotoID INT NULL FOREIGN KEY REFERENCES Motocicletas(MotoID),
                    FechaProgramada DATETIME NOT NULL,
                    TipoMantenimiento NVARCHAR(50) DEFAULT 'Preventivo',
                    Estado NVARCHAR(30) DEFAULT 'Pendiente',
                    Notas NVARCHAR(MAX) NULL,
                    FechaCreacion DATETIME DEFAULT GETDATE()
                )
            """)
            conn.commit()
            print("[OK] Tabla CitasWhatsApp creada.")
        else:
            print("[INFO] Tabla CitasWhatsApp ya existe.")
            # Verify if 'Notas' column exists
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CitasWhatsApp' AND COLUMN_NAME = 'Notas'")
            notas_exists = cursor.fetchone()[0]
            if notas_exists == 0:
                cursor.execute("ALTER TABLE CitasWhatsApp ADD Notas NVARCHAR(MAX) NULL")
                conn.commit()
                print("[OK] Columna Notas agregada a CitasWhatsApp.")
                
        # 2. Verificar/Crear MensajesWhatsApp
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'MensajesWhatsApp'")
        mensajes_exists = cursor.fetchone()[0]
        
        if mensajes_exists == 0:
            print("[INFO] Creando tabla MensajesWhatsApp...")
            cursor.execute("""
                CREATE TABLE MensajesWhatsApp (
                    MensajeID INT IDENTITY(1,1) PRIMARY KEY,
                    TelefonoCliente NVARCHAR(30) NOT NULL,
                    ClienteID INT NULL FOREIGN KEY REFERENCES Clientes(ClienteID),
                    Direccion NVARCHAR(10) NOT NULL, -- 'Entrante' o 'Saliente'
                    Contenido NVARCHAR(MAX) NOT NULL,
                    EsAutoRespuesta BIT DEFAULT 0,
                    FechaHora DATETIME DEFAULT GETDATE(),
                    CitaID INT NULL FOREIGN KEY REFERENCES CitasWhatsApp(CitaID)
                )
            """)
            conn.commit()
            print("[OK] Tabla MensajesWhatsApp creada.")
        else:
            print("[INFO] Tabla MensajesWhatsApp ya existe.")
            
        print("[SUCCESS] Configuracion de base de datos de WhatsApp completada con exito.")
        return True
    except Exception as e:
        print(f"[ERROR] Error configurando tablas de WhatsApp: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    setup_whatsapp_tables()
