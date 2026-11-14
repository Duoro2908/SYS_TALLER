import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-tallerpro'
    
    # Configuración de base de datos SQL Server
    # Asegúrate de ajustar SERVER y DATABASE a tu entorno local
    DB_SERVER = os.environ.get('DB_SERVER') or r'XAN\SQLSERVER'
    DB_NAME = os.environ.get('DB_NAME') or 'taller_y_lubricantes_cr'
    DB_DRIVER = os.environ.get('DB_DRIVER') or '{ODBC Driver 17 for SQL Server}'
    
    # Usando Windows Authentication (Trusted Connection)
    DB_CONNECTION_STRING = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"

    # Configuración de Empresa y Fiscal DGI Nicaragua
    COMPANY_NAME = "Taller y Lubricantes CR"
    COMPANY_RUC = os.environ.get('COMPANY_RUC') or 'J0310000123456'
    COMPANY_ADDRESS = "Managua, Nicaragua"
    COMPANY_PHONE = "Canal Virtual Taller CR"
    COMPANY_DGI_AUTORIZACION = "No. 0401-2024-CR • Régimen General"
