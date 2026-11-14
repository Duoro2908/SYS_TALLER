import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def setup_config_whatsapp():
    conn = get_db_connection()
    if not conn:
        print("Error al conectar a la base de datos.")
        return
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ConfiguracionWhatsApp'")
    exists = cursor.fetchone()[0]
    
    if exists == 0:
        cursor.execute("""
            CREATE TABLE ConfiguracionWhatsApp (
                ConfigID INT IDENTITY(1,1) PRIMARY KEY,
                BotActivo BIT DEFAULT 1,
                TelefonoNumero NVARCHAR(50) DEFAULT '+505 77326738',
                MetaAccessToken NVARCHAR(MAX) NULL,
                MetaPhoneNumberID NVARCHAR(100) NULL,
                VerifyToken NVARCHAR(100) DEFAULT 'taller_cr_whatsapp_token_2026',
                MensajeBienvenida NVARCHAR(MAX) NULL,
                FechaActualizacion DATETIME DEFAULT GETDATE()
            )
        """)
        conn.commit()
        print("Tabla ConfiguracionWhatsApp creada con éxito.")
        
        # Insertar registro inicial
        cursor.execute("""
            INSERT INTO ConfiguracionWhatsApp (BotActivo, TelefonoNumero, VerifyToken, MensajeBienvenida)
            VALUES (1, '+505 77326738', 'taller_cr_whatsapp_token_2026', '¡Hola! Bienvenido a Taller y Lubricantes CR. ¿En qué podemos ayudarte hoy?')
        """)
        conn.commit()
        print("Fila de configuración por defecto insertada.")
    else:
        print("Tabla ConfiguracionWhatsApp ya existe.")
        
    cursor.execute("SELECT * FROM ConfiguracionWhatsApp")
    row = cursor.fetchone()
    print("Configuración actual:", row)
    conn.close()

if __name__ == '__main__':
    setup_config_whatsapp()
