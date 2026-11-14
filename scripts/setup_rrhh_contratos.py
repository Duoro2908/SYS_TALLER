import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
from decimal import Decimal
from database import get_db_connection

def setup_rrhh_contratos():
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()
    print("[INFO] Conectado a la base de datos. Creando tabla ContratosLaborales...")

    # 1. Crear tabla ContratosLaborales si no existe
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ContratosLaborales')
        BEGIN
            CREATE TABLE ContratosLaborales (
                ContratoID INT IDENTITY(1,1) PRIMARY KEY,
                UsuarioID INT NOT NULL FOREIGN KEY REFERENCES Usuarios(UsuarioID),
                NumeroContrato NVARCHAR(50) NOT NULL UNIQUE,
                TipoContrato NVARCHAR(50) NOT NULL DEFAULT 'Tiempo Indeterminado',
                FechaInicio DATE NOT NULL,
                FechaFin DATE NULL,
                Cargo NVARCHAR(120) NOT NULL,
                Departamento NVARCHAR(100) NOT NULL,
                Jornada NVARCHAR(100) NOT NULL DEFAULT 'Diurna Ordinaria (48 hrs semanales)',
                Horario NVARCHAR(150) NOT NULL DEFAULT 'Lunes a Viernes: 8:00 AM - 5:00 PM, Sábado: 8:00 AM - 12:00 MD',
                SalarioPactado DECIMAL(18,2) NOT NULL,
                PeriodoPruebaDias INT NOT NULL DEFAULT 30,
                LugarTrabajo NVARCHAR(200) NOT NULL DEFAULT 'Instalaciones de Taller y Lubricantes CR, Managua',
                CedulaIdentidad NVARCHAR(50) NOT NULL,
                DireccionDomicilio NVARCHAR(250) NULL,
                TelefonoContacto NVARCHAR(50) NULL,
                EstadoContrato NVARCHAR(50) NOT NULL DEFAULT 'Vigente',
                ClausulasAdicionales NVARCHAR(MAX) NULL,
                FechaRegistro DATETIME DEFAULT GETDATE()
            );
            PRINT '[OK] Tabla ContratosLaborales creada con éxito.';
        END
        ELSE
        BEGIN
            PRINT '[INFO] Tabla ContratosLaborales ya existe.';
        END
    """)
    conn.commit()

    # 2. Configurar Salarios Coherentes y Meses de Servicio (Ley 185 / Mercado Nicaragua)
    # Lista de empleados de Taller CR con salarios realistas y profesionales
    empleados_config = [
        {
            'email': 'elvin.admin',
            'salario': 28000.00,
            'meses': 24,
            'cargo': 'Director General de Operaciones',
            'depto': 'Dirección Ejecutiva',
            'cedula': '001-150885-0004X',
            'telefono': '+505 8899-1122',
            'domicilio': 'Bello Horizonte, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2024-10-01'
        },
        {
            'email': 'jhosep.gerente',
            'salario': 22000.00,
            'meses': 18,
            'cargo': 'Gerente General',
            'depto': 'Gerencia y Administración',
            'cedula': '001-200490-0012B',
            'telefono': '+505 8744-3321',
            'domicilio': 'Colonia Nicarao, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-04-15'
        },
        {
            'email': 'martha.estadistica',
            'salario': 18000.00,
            'meses': 14,
            'cargo': 'Especialista en Estadística y Control de Gestión',
            'depto': 'Control y Calidad',
            'cedula': '001-090493-0027Q',
            'telefono': '+505 8622-4411',
            'domicilio': 'Villa Fontana, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-08-01'
        },
        {
            'email': 'carlos.finanzas',
            'salario': 16500.00,
            'meses': 12,
            'cargo': 'Responsable de Finanzas y Contabilidad',
            'depto': 'Contabilidad y Finanzas',
            'cedula': '001-300189-0018W',
            'telefono': '+505 8455-6677',
            'domicilio': 'Altamira D’Este, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-10-15'
        },
        {
            'email': 'brisa.rrhh',
            'salario': 15500.00,
            'meses': 15,
            'cargo': 'Responsable de Recursos Humanos y Nómina',
            'depto': 'Recursos Humanos',
            'cedula': '001-140297-0030E',
            'telefono': '+505 8311-2244',
            'domicilio': 'Ciudad Jardín, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-07-01'
        },
        {
            'email': 'carlos.merca',
            'salario': 14500.00,
            'meses': 10,
            'cargo': 'Especialista en Mercadotecnia y Publicidad',
            'depto': 'Comercial y Mercadeo',
            'cedula': '001-170595-0042R',
            'telefono': '+505 8577-9900',
            'domicilio': 'Linda Vista, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-12-01'
        },
        {
            'email': 'jose.mecanico',
            'salario': 13500.00,
            'meses': 14,
            'cargo': 'Mecánico Maestro de Diagnóstico y Motores',
            'depto': 'Operaciones / Taller Mecánico',
            'cedula': '001-050392-0033K',
            'telefono': '+505 8822-1133',
            'domicilio': 'Barrio San Judas, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-08-15'
        },
        {
            'email': 'elmerson.mecanico',
            'salario': 13500.00,
            'meses': 12,
            'cargo': 'Mecánico de Mantenimiento Preventivo y Frenos',
            'depto': 'Operaciones / Taller Mecánico',
            'cedula': '001-120794-0019T',
            'telefono': '+505 8244-7788',
            'domicilio': 'Monseñor Lezcano, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-10-15'
        },
        {
            'email': 'roxana.caja',
            'salario': 13000.00,
            'meses': 12,
            'cargo': 'Cajera Principal y Facturación',
            'depto': 'Caja y Ventas',
            'cedula': '001-100295-0021A',
            'telefono': '+505 8699-0011',
            'domicilio': 'Colonia Primero de Mayo, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-10-01'
        },
        {
            'email': 'cley.bodega',
            'salario': 13000.00,
            'meses': 10,
            'cargo': 'Responsable de Bodega e Inventario de Repuestos',
            'depto': 'Logística y Abastecimiento',
            'cedula': '001-250696-0008M',
            'telefono': '+505 8133-4455',
            'domicilio': 'Barrio Santa Ana, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2025-12-15'
        },
        {
            'email': 'fanny.atencion',
            'salario': 12500.00,
            'meses': 8,
            'cargo': 'Ejecutiva de Atención al Cliente y Citas WhatsApp',
            'depto': 'Atención al Cliente',
            'cedula': '001-281198-0015L',
            'telefono': '+505 8922-3344',
            'domicilio': 'Rubenia, Managua',
            'tipo': 'Tiempo Indeterminado',
            'fecha_inicio': '2026-02-15'
        }
    ]

    print("[INFO] Actualizando salarios de empleados e insertando contratos...")
    idx = 1
    for emp in empleados_config:
        cursor.execute("SELECT UsuarioID, NombreCompleto FROM Usuarios WHERE Email = ?", (emp['email'],))
        row = cursor.fetchone()
        if not row:
            print(f"[WARN] No se encontró usuario con email '{emp['email']}'")
            continue

        usuario_id, nombre = row[0], row[1]

        # 1. Actualizar SalarioBase y MesesAcumulados en Usuarios
        cursor.execute("""
            UPDATE Usuarios 
            SET SalarioBase = ?, MesesAcumulados = ? 
            WHERE UsuarioID = ?
        """, (emp['salario'], emp['meses'], usuario_id))

        # 2. Verificar o Insertar Contrato en ContratosLaborales
        cursor.execute("SELECT ContratoID FROM ContratosLaborales WHERE UsuarioID = ?", (usuario_id,))
        cont_row = cursor.fetchone()

        num_contrato = f"CTR-TCR-2026-{idx:03d}"
        idx += 1

        if not cont_row:
            cursor.execute("""
                INSERT INTO ContratosLaborales (
                    UsuarioID, NumeroContrato, TipoContrato, FechaInicio, Cargo, 
                    Departamento, Jornada, Horario, SalarioPactado, PeriodoPruebaDias, 
                    LugarTrabajo, CedulaIdentidad, DireccionDomicilio, TelefonoContacto, 
                    EstadoContrato, ClausulasAdicionales
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 30, ?, ?, ?, ?, 'Vigente', ?)
            """, (
                usuario_id, num_contrato, emp['tipo'], emp['fecha_inicio'], emp['cargo'],
                emp['depto'], 'Diurna Ordinaria (48 hrs semanales)', 
                'Lunes a Viernes: 8:00 AM - 5:00 PM, Sábado: 8:00 AM - 12:00 MD',
                emp['salario'], 'Instalaciones de Taller y Lubricantes CR, Managua',
                emp['cedula'], emp['domicilio'], emp['telefono'],
                'Conforme a la Ley 185 (Código del Trabajo de Nicaragua), el trabajador goza de prestaciones de ley: Décimo Tercer Mes (Aguinaldo), Vacaciones anuales remuneradas de 30 días e Indemnización por antigüedad según el Art. 45. Se aplican las deducciones legales obligatorias de INSS Laboral (7%) y Retención en la Fuente del Impuesto sobre la Renta (IR) de conformidad con la Ley N° 822 de Concertación Tributaria de la DGI.'
            ))
            print(f"[OK] Contrato creado para {nombre} (#{num_contrato}): C$ {emp['salario']:,.2f}")
        else:
            cursor.execute("""
                UPDATE ContratosLaborales
                SET Cargo = ?, Departamento = ?, SalarioPactado = ?, CedulaIdentidad = ?, 
                    DireccionDomicilio = ?, TelefonoContacto = ?
                WHERE UsuarioID = ?
            """, (emp['cargo'], emp['depto'], emp['salario'], emp['cedula'], emp['domicilio'], emp['telefono'], usuario_id))
            print(f"[OK] Contrato actualizado para {nombre}: C$ {emp['salario']:,.2f}")

    conn.commit()
    conn.close()
    print("[FINALIZADO] Configuración de Recursos Humanos, Planilla y Contratos completada exitosamente.")

if __name__ == '__main__':
    setup_rrhh_contratos()
