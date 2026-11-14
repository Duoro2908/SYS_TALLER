-- ==============================================================================
-- PROYECTO: taller_y_lubricantes_cr (Sistema Integral Transaccional) — v3 MEJORADA
-- DESCRIPCIÓN: Script maestro de creación de esquema, reglas de negocio 
-- y automatización (Triggers). Análisis delegado a la capa de aplicación (Python/IA).
--
-- MEJORAS AÑADIDAS:
--  - Tabla GastosOperativos para un Estado de Resultados real.
--  - Campo Email añadido a Clientes para envío de facturas/marketing.
--  - Datos de Prueba Profesionales (Marcas populares en Nicaragua, inventario, etc).
-- ==============================================================================

CREATE DATABASE taller_y_lubricantes_cr;
GO
USE taller_y_lubricantes_cr;
GO

-- ==============================================================================
-- FASE 1: SEGURIDAD Y CONFIGURACIÓN BASE
-- ==============================================================================
CREATE TABLE Roles (
    RolID INT IDENTITY(1,1) PRIMARY KEY,
    NombreRol NVARCHAR(50) NOT NULL UNIQUE, 
    PuedeVerFinanzas BIT DEFAULT 0,
    PuedeFacturar BIT DEFAULT 0,
    PuedeComprar BIT DEFAULT 0, 
    PuedeAtenderTaller BIT DEFAULT 0
);

CREATE TABLE Usuarios (
    UsuarioID INT IDENTITY(1,1) PRIMARY KEY,
    NombreCompleto NVARCHAR(150) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(256) NOT NULL, 
    RolID INT FOREIGN KEY REFERENCES Roles(RolID),
    Activo BIT DEFAULT 1
);

-- ==============================================================================
-- FASE 2: DIRECTORIO COMERCIAL
-- ==============================================================================
CREATE TABLE Clientes (
    ClienteID INT IDENTITY(1,1) PRIMARY KEY,
    Identificacion NVARCHAR(50) UNIQUE, 
    NombreCompleto NVARCHAR(150) NOT NULL,
    Telefono NVARCHAR(20) NOT NULL,
    Email NVARCHAR(100) NULL, -- NUEVO: Para envíos digitales
    CitasNoAsistidas INT DEFAULT 0 
);

CREATE TABLE Proveedores (
    ProveedorID INT IDENTITY(1,1) PRIMARY KEY,
    RUC NVARCHAR(50) UNIQUE NOT NULL, 
    NombreEmpresa NVARCHAR(150) NOT NULL,
    Telefono NVARCHAR(20),
    DiasCredito INT DEFAULT 0
);

-- ==============================================================================
-- FASE 3: GESTIÓN DE VEHÍCULOS Y CITAS (WHATSAPP)
-- ==============================================================================
CREATE TABLE Motocicletas (
    MotoID INT IDENTITY(1,1) PRIMARY KEY,
    ClienteID INT FOREIGN KEY REFERENCES Clientes(ClienteID),
    Placa NVARCHAR(20) UNIQUE NOT NULL,
    Marca NVARCHAR(50) NOT NULL,
    Modelo NVARCHAR(50) NOT NULL,
    Anio INT,
    Cilindraje INT NOT NULL,
    CONSTRAINT CHK_Moto_Cilindraje CHECK (Cilindraje >= 49 AND Cilindraje <= 400)
);

CREATE TABLE CitasWhatsApp (
    CitaID INT IDENTITY(1,1) PRIMARY KEY,
    ClienteID INT FOREIGN KEY REFERENCES Clientes(ClienteID),
    MotoID INT FOREIGN KEY REFERENCES Motocicletas(MotoID),
    FechaProgramada DATETIME NOT NULL,
    TipoMantenimiento NVARCHAR(50) CHECK (TipoMantenimiento IN ('Preventivo', 'General', 'Correctivo', 'Express')),
    Estado NVARCHAR(30) DEFAULT 'Pendiente' CHECK (Estado IN ('Pendiente', 'Confirmada', 'Cancelada', 'No Asistio')),
    FechaCreacion DATETIME DEFAULT GETDATE()
);

-- ==============================================================================
-- FASE 4: INVENTARIO CONSOLIDADO 
-- ==============================================================================
CREATE TABLE Productos (
    ProductoID INT IDENTITY(1,1) PRIMARY KEY,
    CodigoSKU NVARCHAR(50) UNIQUE NOT NULL,
    Categoria NVARCHAR(50) NOT NULL,
    Nombre NVARCHAR(100) NOT NULL,
    Descripcion NVARCHAR(MAX),
    PrecioCompra DECIMAL(10,2) NOT NULL CONSTRAINT CHK_Prod_PrecioCompra CHECK (PrecioCompra >= 0), 
    PrecioVenta DECIMAL(10,2) NOT NULL CONSTRAINT CHK_Prod_PrecioVenta CHECK (PrecioVenta >= 0),
    StockActual INT DEFAULT 0 CONSTRAINT CHK_Prod_Stock CHECK (StockActual >= 0),
    ImagenURL NVARCHAR(255),
    MostrarEnCatalogo BIT DEFAULT 1, 
    Activo BIT DEFAULT 1
);

CREATE TABLE AjustesInventario (
    AjusteID INT IDENTITY(1,1) PRIMARY KEY,
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    CantidadAjuste INT NOT NULL, 
    Motivo NVARCHAR(255) NOT NULL,
    FechaAjuste DATETIME DEFAULT GETDATE()
);

-- ==============================================================================
-- FASE 5: COMPRAS Y GASTOS (NUEVO)
-- ==============================================================================
CREATE TABLE Compras (
    CompraID INT IDENTITY(1,1) PRIMARY KEY,
    ProveedorID INT FOREIGN KEY REFERENCES Proveedores(ProveedorID),
    FechaCompra DATETIME DEFAULT GETDATE(),
    Subtotal DECIMAL(10,2) NULL,
    IVA DECIMAL(10,2) NULL,
    TotalCompra DECIMAL(10,2) NOT NULL
);

CREATE TABLE DetalleCompra (
    DetalleID INT IDENTITY(1,1) PRIMARY KEY,
    CompraID INT FOREIGN KEY REFERENCES Compras(CompraID),
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    Cantidad INT NOT NULL CONSTRAINT CHK_DetCom_Cant CHECK (Cantidad > 0),
    PrecioUnitarioCompra DECIMAL(10,2) NOT NULL
);

-- NUEVO: Tabla para registrar gastos del negocio y tener Estados Financieros reales
CREATE TABLE GastosOperativos (
    GastoID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    Categoria NVARCHAR(50) NOT NULL CHECK (Categoria IN ('Nomina', 'Servicios Basicos', 'Alquiler', 'Mantenimiento Local', 'Otros')),
    Descripcion NVARCHAR(255) NOT NULL,
    Monto DECIMAL(10,2) NOT NULL CONSTRAINT CHK_Gasto_Monto CHECK (Monto > 0),
    FechaGasto DATETIME DEFAULT GETDATE()
);

-- ==============================================================================
-- FASE 6: OPERACIONES DE TALLER
-- ==============================================================================
CREATE TABLE CatalogoMantenimientos (
    MantenimientoID INT IDENTITY(1,1) PRIMARY KEY,
    Tipo NVARCHAR(50) NOT NULL UNIQUE CHECK (Tipo IN ('Preventivo', 'General', 'Express')),
    DescripcionDetallada NVARCHAR(MAX) NOT NULL,
    PrecioBase DECIMAL(10,2) NOT NULL
);

CREATE TABLE OrdenesTrabajo (
    OrdenID INT IDENTITY(1,1) PRIMARY KEY,
    MotoID INT FOREIGN KEY REFERENCES Motocicletas(MotoID),
    MecanicoID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    CitaID INT NULL FOREIGN KEY REFERENCES CitasWhatsApp(CitaID), 
    FechaIngreso DATETIME DEFAULT GETDATE(),
    TipoServicio NVARCHAR(50) NOT NULL CONSTRAINT CHK_Orden_Tipo CHECK (TipoServicio IN ('Preventivo', 'General', 'Correctivo', 'Express')),
    KilometrajeIngreso INT NULL,
    NivelCombustible NVARCHAR(20) NULL,
    ProblemaReportado NVARCHAR(MAX),
    Estado NVARCHAR(50) DEFAULT 'En Diagnostico'
    CONSTRAINT CHK_Orden_Estado CHECK (Estado IN (
        'En Diagnostico', 'Cotizado', 'Aprobado', 'En Proceso', 
        'Finalizado', 'Pendiente de Pago', 'Facturada', 'Cancelada'
    ))
);

CREATE TABLE OrdenManoObra (
    ServicioID INT IDENTITY(1,1) PRIMARY KEY,
    OrdenID INT FOREIGN KEY REFERENCES OrdenesTrabajo(OrdenID),
    DescripcionServicio NVARCHAR(150) NOT NULL,
    CostoSugerido DECIMAL(10,2) NOT NULL CONSTRAINT CHK_ManoObra_Costo CHECK (CostoSugerido >= 0)
);

CREATE TABLE OrdenRepuestos (
    ReservaID INT IDENTITY(1,1) PRIMARY KEY,
    OrdenID INT FOREIGN KEY REFERENCES OrdenesTrabajo(OrdenID),
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    Cantidad INT NOT NULL CONSTRAINT CHK_OrdenRep_Cant CHECK (Cantidad > 0)
);

-- ==============================================================================
-- FASE 7: CAJA Y FACTURACIÓN 
-- ==============================================================================
CREATE TABLE ControlCaja (
    CajaID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    FechaApertura DATETIME DEFAULT GETDATE(),
    FechaCierre DATETIME NULL,
    MontoInicial DECIMAL(10,2) NOT NULL,
    Estado NVARCHAR(20) DEFAULT 'Abierta'
    CONSTRAINT CHK_Caja_Estado CHECK (Estado IN ('Abierta', 'Cerrada'))
);

CREATE TABLE Facturas (
    FacturaID INT IDENTITY(1,1) PRIMARY KEY,
    CajaID INT NOT NULL FOREIGN KEY REFERENCES ControlCaja(CajaID), 
    NumeroFactura NVARCHAR(50) UNIQUE NOT NULL,
    OrdenID INT NULL FOREIGN KEY REFERENCES OrdenesTrabajo(OrdenID), 
    FechaEmision DATETIME DEFAULT GETDATE(),
    SubTotal DECIMAL(10,2) NOT NULL,
    TotalIVA DECIMAL(10,2) NOT NULL,       
    ImpuestoDGI DECIMAL(10,2) NOT NULL,    
    TotalNeto DECIMAL(10,2) NOT NULL,      
    MetodoPago NVARCHAR(50) NOT NULL CONSTRAINT CHK_Fact_Pago CHECK (MetodoPago IN ('Efectivo', 'Tarjeta')),
    Estado NVARCHAR(20) DEFAULT 'Pagada' CONSTRAINT CHK_Fact_Estado CHECK (Estado IN ('Pagada', 'Anulada')),
    UsuarioAnulaID INT NULL FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    FechaAnulacion DATETIME NULL,
    RUC_Emisor NVARCHAR(50) DEFAULT 'J0310000123456',
    RUCCliente NVARCHAR(50) NULL
);

CREATE TABLE DetalleFactura (
    DetalleID INT IDENTITY(1,1) PRIMARY KEY,
    FacturaID INT FOREIGN KEY REFERENCES Facturas(FacturaID),
    ProductoID INT NULL FOREIGN KEY REFERENCES Productos(ProductoID), 
    Descripcion NVARCHAR(150) NOT NULL,
    Cantidad INT NOT NULL CONSTRAINT CHK_DetFact_Cant CHECK (Cantidad > 0),
    PrecioVentaAplicado DECIMAL(10,2) NOT NULL,
    CostoCompraAplicado DECIMAL(10,2) NULL 
);

-- ==============================================================================
-- FASE 7B: ÍNDICES SOBRE CLAVES FORÁNEAS
-- ==============================================================================
CREATE INDEX IX_Usuarios_RolID ON Usuarios(RolID);
CREATE INDEX IX_Motocicletas_ClienteID ON Motocicletas(ClienteID);
CREATE INDEX IX_CitasWhatsApp_ClienteID ON CitasWhatsApp(ClienteID);
CREATE INDEX IX_CitasWhatsApp_MotoID ON CitasWhatsApp(MotoID);
CREATE INDEX IX_AjustesInventario_ProductoID ON AjustesInventario(ProductoID);
CREATE INDEX IX_Compras_ProveedorID ON Compras(ProveedorID);
CREATE INDEX IX_DetalleCompra_CompraID ON DetalleCompra(CompraID);
CREATE INDEX IX_DetalleCompra_ProductoID ON DetalleCompra(ProductoID);
CREATE INDEX IX_GastosOperativos_UsuarioID ON GastosOperativos(UsuarioID);
CREATE INDEX IX_OrdenesTrabajo_MotoID ON OrdenesTrabajo(MotoID);
CREATE INDEX IX_OrdenesTrabajo_MecanicoID ON OrdenesTrabajo(MecanicoID);
CREATE INDEX IX_OrdenesTrabajo_CitaID ON OrdenesTrabajo(CitaID);
CREATE INDEX IX_OrdenManoObra_OrdenID ON OrdenManoObra(OrdenID);
CREATE INDEX IX_OrdenRepuestos_OrdenID ON OrdenRepuestos(OrdenID);
CREATE INDEX IX_OrdenRepuestos_ProductoID ON OrdenRepuestos(ProductoID);
CREATE INDEX IX_ControlCaja_UsuarioID ON ControlCaja(UsuarioID);
CREATE INDEX IX_Facturas_CajaID ON Facturas(CajaID);
CREATE INDEX IX_Facturas_OrdenID ON Facturas(OrdenID);
CREATE INDEX IX_Facturas_UsuarioAnulaID ON Facturas(UsuarioAnulaID);
CREATE INDEX IX_DetalleFactura_FacturaID ON DetalleFactura(FacturaID);
CREATE INDEX IX_DetalleFactura_ProductoID ON DetalleFactura(ProductoID);
GO

-- ==============================================================================
-- FASE 8: MOTOR DE AUTOMATIZACIÓN (TRIGGERS MAESTROS)
-- ==============================================================================
GO

-- 1. [TRIGGER]: GESTIÓN DE CITAS WHATSAPP
CREATE TRIGGER TRG_Citas_PenalizarAusencia 
ON CitasWhatsApp AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    IF UPDATE(Estado)
    BEGIN
        UPDATE C 
        SET C.CitasNoAsistidas = C.CitasNoAsistidas + 1 
        FROM Clientes C
        INNER JOIN inserted I ON C.ClienteID = I.ClienteID 
        INNER JOIN deleted D ON I.CitaID = D.CitaID
        WHERE I.Estado = 'No Asistio' AND D.Estado <> 'No Asistio';
    END
END;
GO

-- 2. [TRIGGER UNIFICADO]: INSERCIÓN DE FACTURAS (STOCK + ANTIFRAUDE + TOTALES)
CREATE TRIGGER TRG_DetalleFactura_Operaciones 
ON DetalleFactura AFTER INSERT AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE DF
    SET DF.CostoCompraAplicado = P.PrecioCompra
    FROM DetalleFactura DF
    INNER JOIN inserted I ON DF.DetalleID = I.DetalleID
    INNER JOIN Productos P ON I.ProductoID = P.ProductoID
    WHERE I.ProductoID IS NOT NULL;

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
GO

-- 3. [TRIGGER UNIFICADO]: ACTUALIZACIÓN DE FACTURAS (ANULACIONES Y CIERRE DE TALLER)
CREATE TRIGGER TRG_Facturas_Actualizacion 
ON Facturas AFTER INSERT, UPDATE AS
BEGIN
    SET NOCOUNT ON;

    UPDATE O
    SET O.Estado = 'Facturada'
    FROM OrdenesTrabajo O
    INNER JOIN inserted I ON O.OrdenID = I.OrdenID
    WHERE I.Estado = 'Pagada' AND I.OrdenID IS NOT NULL;

    IF UPDATE(Estado)
    BEGIN
        IF EXISTS (
            SELECT 1 FROM inserted I 
            LEFT JOIN deleted D ON I.FacturaID = D.FacturaID
            WHERE I.Estado = 'Anulada' AND ISNULL(D.Estado, '') <> 'Anulada'
        )
        BEGIN
            UPDATE O
            SET O.Estado = 'Pendiente de Pago'
            FROM OrdenesTrabajo O
            INNER JOIN inserted I ON O.OrdenID = I.OrdenID
            LEFT JOIN deleted D ON I.FacturaID = D.FacturaID
            WHERE I.Estado = 'Anulada' AND ISNULL(D.Estado, '') <> 'Anulada' AND I.OrdenID IS NOT NULL;

            UPDATE F
            SET F.FechaAnulacion = GETDATE()
            FROM Facturas F
            INNER JOIN inserted I ON F.FacturaID = I.FacturaID
            LEFT JOIN deleted D ON I.FacturaID = D.FacturaID
            WHERE I.Estado = 'Anulada' AND ISNULL(D.Estado, '') <> 'Anulada';

            UPDATE P 
            SET P.StockActual = P.StockActual + DF.TotalDevuelto
            FROM Productos P 
            INNER JOIN (
                SELECT D2.ProductoID, SUM(D2.Cantidad) AS TotalDevuelto 
                FROM DetalleFactura D2
                INNER JOIN inserted Ins ON D2.FacturaID = Ins.FacturaID 
                LEFT JOIN deleted Del ON Ins.FacturaID = Del.FacturaID
                WHERE Ins.Estado = 'Anulada' AND ISNULL(Del.Estado, '') <> 'Anulada' 
                  AND D2.ProductoID IS NOT NULL AND Ins.OrdenID IS NULL
                GROUP BY D2.ProductoID
            ) DF ON P.ProductoID = DF.ProductoID;
            
            UPDATE Productos SET MostrarEnCatalogo = 1 WHERE StockActual > 0 AND Activo = 1;
        END
    END
END;
GO

-- 4. [TRIGGER]: ENTRADAS DE COMPRA A PROVEEDOR
CREATE TRIGGER TRG_Compras_AumentarStock 
ON DetalleCompra AFTER INSERT AS
BEGIN
    SET NOCOUNT ON;
    
    ;WITH UltimoPrecioPorProducto AS (
        SELECT ProductoID, PrecioUnitarioCompra,
               ROW_NUMBER() OVER (PARTITION BY ProductoID ORDER BY CompraID DESC, DetalleID DESC) AS rn
        FROM inserted
    ),
    TotalesPorProducto AS (
        SELECT ProductoID, SUM(Cantidad) AS TotalComprado 
        FROM inserted GROUP BY ProductoID
    )
    UPDATE P 
    SET P.StockActual = P.StockActual + T.TotalComprado, 
        P.PrecioCompra = U.PrecioUnitarioCompra
    FROM Productos P 
    INNER JOIN TotalesPorProducto T ON P.ProductoID = T.ProductoID
    INNER JOIN UltimoPrecioPorProducto U ON P.ProductoID = U.ProductoID AND U.rn = 1;
    
    UPDATE Productos SET MostrarEnCatalogo = 1 WHERE StockActual > 0 AND Activo = 1;

    UPDATE C
    SET C.Subtotal = X.Suma,
        C.IVA = ROUND(X.Suma * 0.15, 2),
        C.TotalCompra = ROUND(X.Suma * 1.15, 2)
    FROM Compras C
    INNER JOIN (
        SELECT CompraID, SUM(Cantidad * PrecioUnitarioCompra) AS Suma
        FROM DetalleCompra
        WHERE CompraID IN (SELECT DISTINCT CompraID FROM inserted)
        GROUP BY CompraID
    ) X ON C.CompraID = X.CompraID;
END;
GO

-- 5. [TRIGGER]: AJUSTES DE INVENTARIO (MERMAS)
CREATE TRIGGER TRG_Ajustes_Inventario 
ON AjustesInventario AFTER INSERT AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE P 
    SET P.StockActual = P.StockActual + I.TotalAjustado 
    FROM Productos P 
    INNER JOIN (SELECT ProductoID, SUM(CantidadAjuste) AS TotalAjustado FROM inserted GROUP BY ProductoID) I 
    ON P.ProductoID = I.ProductoID;
    
    UPDATE Productos 
    SET MostrarEnCatalogo = CASE WHEN StockActual > 0 THEN 1 ELSE 0 END 
    WHERE ProductoID IN (SELECT DISTINCT ProductoID FROM inserted) AND Activo = 1;
END;
GO

-- 6. [TRIGGER NUEVO - FIX #3]: RESERVA/LIBERACIÓN DE STOCK EN REPUESTOS DE ORDEN
CREATE TRIGGER TRG_OrdenRepuestos_Stock 
ON OrdenRepuestos AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;

    ;WITH Antes AS (
        SELECT ProductoID, SUM(Cantidad) AS Cant FROM deleted GROUP BY ProductoID
    ),
    Despues AS (
        SELECT ProductoID, SUM(Cantidad) AS Cant FROM inserted GROUP BY ProductoID
    ),
    Productos_Afectados AS (
        SELECT ProductoID FROM Antes
        UNION
        SELECT ProductoID FROM Despues
    )
    UPDATE P
    SET P.StockActual = P.StockActual + ISNULL(A.Cant, 0) - ISNULL(D.Cant, 0)
    FROM Productos P
    INNER JOIN Productos_Afectados X ON P.ProductoID = X.ProductoID
    LEFT JOIN Antes A ON A.ProductoID = X.ProductoID
    LEFT JOIN Despues D ON D.ProductoID = X.ProductoID;

    UPDATE Productos SET MostrarEnCatalogo = 0 WHERE StockActual <= 0;
    UPDATE Productos SET MostrarEnCatalogo = 1 
    WHERE StockActual > 0 AND Activo = 1 
      AND ProductoID IN (SELECT ProductoID FROM inserted UNION SELECT ProductoID FROM deleted);
END;
GO

-- 7. [TRIGGER NUEVO - FIX #7]: LÍNEAS DE FACTURA INMUTABLES
CREATE TRIGGER TRG_DetalleFactura_Inmutable
ON DetalleFactura INSTEAD OF UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    RAISERROR('No se permite modificar ni eliminar lineas de una factura ya emitida. Use el proceso de anulacion de la Factura.', 16, 1);
    ROLLBACK TRANSACTION;
END;
GO

-- =======================================================
-- FASE 9: INSERCIÓN DE DATOS DE PRUEBA PROFESIONALES
-- =======================================================

-- 1. CREACIÓN DE ROLES
INSERT INTO Roles (NombreRol, PuedeVerFinanzas, PuedeFacturar, PuedeComprar, PuedeAtenderTaller)
VALUES 
('Gerente', 1, 1, 1, 1),
('Cajera/Vendedora', 0, 1, 0, 0),
('Mecánico', 0, 0, 0, 1),
('Contador', 1, 0, 0, 0),
('Licenciada en Estadística', 1, 0, 0, 0);

-- 2. CREACIÓN DE USUARIOS
INSERT INTO Usuarios (NombreCompleto, Email, PasswordHash, RolID, Activo) VALUES 
('Elvin Alexander Mendez Cruz', 'elvin.admin', 'scrypt:32768:8:1$FMy9FFP5xZty4Fv2$d340a0a912e50b8c37aca16c4ba37abd8689d47061ffdfa058cd02f90ef9bb5eccfd34dd2a74eba42e2cf53dae521a83d5bac37c3d737c538d9b1b00ea34e496', 1, 1),
('Carlos Rene Gavarrete Calero', 'carlos.finanzas', 'scrypt:32768:8:1$cfQZ4xJ6bvbTjNhp$e251a0edff32030880a0e81cf43e4a6ce6c4abada3d3e012c27e7682c7c8e85629d1ee049f69595bc197a33ea671d1ef8761c970bf1e37eb199e5a39599ba2df', 6, 1),
('Carlos Rene Gavarrete Calero', 'carlos.contabilidad', 'scrypt:32768:8:1$QaXGWx4hyCS4STDn$c0993962f4bfdbe048da09efe166f3958662d824dd585626582dd410d794544caac376ed9d1c7dbab5eaf07b50a5e2255d33cb550ab88a1535129e1fd409988a', 6, 1),
('Martha Jovana Lopez Chavarria', 'martha.estadistica', 'scrypt:32768:8:1$FMy9FFP5xZty4Fv2$d340a0a912e50b8c37aca16c4ba37abd8689d47061ffdfa058cd02f90ef9bb5eccfd34dd2a74eba42e2cf53dae521a83d5bac37c3d737c538d9b1b00ea34e496', 5, 1);

-- 3. MODELOS SOPORTADOS (Nicaragua: 100cc - 250cc)


-- 4. TIPOS DE MANTENIMIENTO
INSERT INTO CatalogoMantenimientos (Tipo, DescripcionDetallada, PrecioBase) VALUES
('Express', 'Mantenimiento rapido: Cambio de aceite, revision de presion de llantas, tension de cadena, revision de luces y frenos. Tiempo estimado: 30 minutos.', 350.00),
('Preventivo', 'Mantenimiento preventivo: Cambio de aceite y filtro, limpieza/cambio de bujia, limpieza de carburador o inyector, ajuste y lubricacion de cadena, revision de liquido de frenos y fricciones, revision electrica general, ajuste de tornilleria.', 800.00),
('General', 'Mantenimiento exhaustivo: Todo lo del preventivo mas: Engrase de cunas de direccion, cambio de aceite de barras (suspension), revision profunda de motor, limpieza de filtro de aire a profundidad, revision de balineras y rodamiento, limpieza de tanque de combustible.', 1500.00);

-- 5. PRODUCTOS PROFESIONALES (Ampliados)
INSERT INTO Productos (CodigoSKU, Categoria, Nombre, Descripcion, PrecioCompra, PrecioVenta, StockActual, MostrarEnCatalogo, ImagenURL) VALUES
('AQU-MOD-SIS-100', 'Sistema', 'Repuesto Marca del Repuesto', 'Le queda a (compatibilidad)', 0.00, 0.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-101', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Solo CT125 (motor propio)', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-102', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Solo CT125 (motor propio)', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-103', 'Motor', 'Cigüeñal Genuino Bajaj', 'Solo CT125 (motor propio)', 1920.00, 3200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-104', 'Motor', 'Bielas Genuino Bajaj', 'Solo CT125 (motor propio)', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-105', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-106', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Solo CT125 (motor propio)', 2280.00, 3800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-107', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-108', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Solo CT125 (motor propio)', 120.00, 200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-109', 'Motor', 'Guías de válvula Genuino Bajaj', 'Solo CT125 (motor propio)', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-110', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Solo CT125 (motor propio)', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-111', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Solo CT125 (motor propio)', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-112', 'Motor', 'Árbol de levas Genuino Bajaj', 'Solo CT125 (motor propio)', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-113', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-114', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Solo CT125 (motor propio)', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-115', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Solo CT125 (motor propio) — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 48.00, 80.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-116', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Solo CT125 (motor propio)', 384.00, 640.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-117', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Solo CT125 (motor propio)', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-118', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 54.00, 90.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-MOT-119', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 66.00, 110.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-120', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Solo CT125 (motor propio)', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-121', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Solo CT125 (motor propio)', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-122', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-123', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Solo CT125 (motor propio)', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-124', 'Transmisión', 'Corona trasera DID, EP Racing', 'Solo CT125 (motor propio)', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-125', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Solo CT125 (motor propio)', 456.00, 760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-126', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Solo CT125 (motor propio)', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-127', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Solo CT125 (motor propio)', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-TRA-128', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Solo CT125 (motor propio)', 432.00, 720.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-129', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-130', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Solo CT125 (motor propio)', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-131', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Solo CT125 (motor propio)', 864.00, 1440.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-132', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Solo CT125 (motor propio)', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-133', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 324.00, 540.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-134', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Solo CT125 (motor propio)', 1128.00, 1880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-135', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Solo CT125 (motor propio)', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-136', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-137', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ELÉ-138', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Solo CT125 (motor propio)', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-FRE-139', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-FRE-140', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 528.00, 880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-FRE-141', 'Frenos', 'Bomba de freno (cilindro maestro) Genuino Bajaj', 'Solo CT125 (motor propio)', 768.00, 1280.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-FRE-142', 'Frenos', 'Manguera de freno Genérico', 'Universal / toda la gama', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-FRE-143', 'Frenos', 'Líquido de frenos DOT4 DOT4 (genérico)', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-SUS-144', 'Suspensión', 'Amortiguadores traseros YSS, Genérico', 'Universal / según chasis del modelo', 1056.00, 1760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-SUS-145', 'Suspensión', 'Horquilla / telescópica delantera Genuino Bajaj', 'Solo CT125 (motor propio)', 1632.00, 2720.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-SUS-146', 'Suspensión', 'Retenedores de telescópica Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-LLA-147', 'Llantas', 'Llanta delantera Vee Rubber, CST', 'Según medida de rin del modelo', 1344.00, 2240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-LLA-148', 'Llantas', 'Llanta trasera Vee Rubber, CST', 'Según medida de rin del modelo', 1488.00, 2480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-LLA-149', 'Llantas', 'Cámara (tubo) Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-LLA-150', 'Llantas', 'Rines (aros) Genuino Bajaj', 'Solo CT125 (motor propio)', 1128.00, 1880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-LLA-151', 'Llantas', 'Rodamientos de rueda Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-152', 'Carburación', 'Carburador completo Genuino Bajaj, Mikuni', 'Solo CT125 (motor propio)', 912.00, 1520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-153', 'Carburación', 'Filtro de aire HiFlo, Genuino Bajaj', 'Solo CT125 (motor propio)', 162.00, 270.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-154', 'Carburación', 'Filtro de gasolina Genérico', 'Universal / toda la gama', 84.00, 140.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-ESC-155', 'Escape', 'Mofle / silenciador completo Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 1272.00, 2120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-156', 'Carrocería', 'Guardabarros del./tras. Genérico', 'Universal / toda la gama', 324.00, 540.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-157', 'Carrocería', 'Tanque de gasolina Genuino Bajaj', 'Solo CT125 (motor propio)', 1920.00, 3200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-158', 'Carrocería', 'Asiento (sillín) Genérico', 'Universal / toda la gama', 912.00, 1520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-159', 'Carrocería', 'Plásticos / carenados Genuino Bajaj, Genérico', 'Solo CT125 (motor propio)', 528.00, 880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-160', 'Carrocería', 'Espejos Genérico', 'Universal / toda la gama', 162.00, 270.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-161', 'Carrocería', 'Manubrio (timón) Genuino Bajaj', 'Solo CT125 (motor propio)', 456.00, 760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-162', 'Carrocería', 'Puños (grips) Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-CAR-163', 'Carrocería', 'Pedales (freno/cambio) Genuino Bajaj', 'Solo CT125 (motor propio)', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-OTR-164', 'Otros', 'Cable de acelerador Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-CT1-OTR-165', 'Otros', 'Soporte central / lateral (pata de cabra) Genuino Bajaj', 'Solo CT125 (motor propio)', 300.00, 500.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-166', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-167', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-168', 'Motor', 'Cigüeñal Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-169', 'Motor', 'Bielas Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-170', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 300.00, 500.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-171', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2850.00, 4750.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-172', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-173', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 150.00, 250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-174', 'Motor', 'Guías de válvula Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 96.00, 160.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-175', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-176', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-177', 'Motor', 'Árbol de levas Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-178', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-179', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-180', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor) — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-181', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-182', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 750.00, 1250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-183', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 72.00, 120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-184', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 84.00, 140.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-185', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-186', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-187', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-188', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-189', 'Transmisión', 'Corona trasera DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-190', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-191', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-192', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-193', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 540.00, 900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-194', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-195', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-196', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1080.00, 1800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-197', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-198', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-199', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-200', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-201', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-202', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-203', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-204', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-205', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-206', 'Frenos', 'Bomba de freno (cilindro maestro) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-207', 'Frenos', 'Manguera de freno Genérico', 'Universal / toda la gama', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-208', 'Frenos', 'Líquido de frenos DOT4 DOT4 (genérico)', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-209', 'Suspensión', 'Amortiguadores traseros YSS, Genérico', 'Universal / según chasis del modelo', 1320.00, 2200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-210', 'Suspensión', 'Horquilla / telescópica delantera Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2040.00, 3400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-211', 'Suspensión', 'Retenedores de telescópica Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-212', 'Llantas', 'Llanta delantera Vee Rubber, CST', 'Según medida de rin del modelo', 1680.00, 2800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-213', 'Llantas', 'Llanta trasera Vee Rubber, CST', 'Según medida de rin del modelo', 1860.00, 3100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-214', 'Llantas', 'Cámara (tubo) Genérico', 'Universal / toda la gama', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-215', 'Llantas', 'Rines (aros) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-216', 'Llantas', 'Rodamientos de rueda Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-217', 'Carburación', 'Carburador completo Genuino Bajaj, Mikuni', 'Boxer 150 y Boxer 150X (mismo motor)', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-218', 'Carburación', 'Filtro de aire HiFlo, Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-219', 'Carburación', 'Filtro de gasolina Genérico', 'Universal / toda la gama', 108.00, 180.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ESC-220', 'Escape', 'Mofle / silenciador completo Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 1590.00, 2650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-221', 'Carrocería', 'Guardabarros del./tras. Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-222', 'Carrocería', 'Tanque de gasolina Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-223', 'Carrocería', 'Asiento (sillín) Genérico', 'Universal / toda la gama', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-224', 'Carrocería', 'Plásticos / carenados Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-225', 'Carrocería', 'Espejos Genérico', 'Universal / toda la gama', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-226', 'Carrocería', 'Manubrio (timón) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-227', 'Carrocería', 'Puños (grips) Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-228', 'Carrocería', 'Pedales (freno/cambio) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-229', 'Otros', 'Cable de acelerador Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-230', 'Otros', 'Soporte central / lateral (pata de cabra) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 372.00, 620.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-231', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-232', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-233', 'Motor', 'Cigüeñal Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-234', 'Motor', 'Bielas Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-235', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 300.00, 500.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-236', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2850.00, 4750.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-237', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-238', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 150.00, 250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-239', 'Motor', 'Guías de válvula Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 96.00, 160.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-240', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-241', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-242', 'Motor', 'Árbol de levas Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-243', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-244', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-245', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor) — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-246', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-247', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 750.00, 1250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-248', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 72.00, 120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-249', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 84.00, 140.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-250', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-251', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-252', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-253', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-254', 'Transmisión', 'Corona trasera DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-255', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-256', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Boxer 150 y Boxer 150X (mismo motor)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-257', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-258', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 540.00, 900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-259', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-260', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-261', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1080.00, 1800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-262', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-263', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-264', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-265', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-266', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-267', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-268', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-269', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-270', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-271', 'Frenos', 'Bomba de freno (cilindro maestro) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-272', 'Frenos', 'Manguera de freno Genérico', 'Universal / toda la gama', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-273', 'Frenos', 'Líquido de frenos DOT4 DOT4 (genérico)', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-274', 'Suspensión', 'Amortiguadores traseros YSS, Genérico', 'Universal / según chasis del modelo', 1320.00, 2200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-275', 'Suspensión', 'Horquilla / telescópica delantera Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2040.00, 3400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-276', 'Suspensión', 'Retenedores de telescópica Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-277', 'Llantas', 'Llanta delantera Vee Rubber, CST', 'Según medida de rin del modelo', 1680.00, 2800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-278', 'Llantas', 'Llanta trasera Vee Rubber, CST', 'Según medida de rin del modelo', 1860.00, 3100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-279', 'Llantas', 'Cámara (tubo) Genérico', 'Universal / toda la gama', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-280', 'Llantas', 'Rines (aros) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-281', 'Llantas', 'Rodamientos de rueda Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-282', 'Carburación', 'Carburador completo Genuino Bajaj, Mikuni', 'Boxer 150 y Boxer 150X (mismo motor)', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-283', 'Carburación', 'Filtro de aire HiFlo, Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-284', 'Carburación', 'Filtro de gasolina Genérico', 'Universal / toda la gama', 108.00, 180.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ESC-285', 'Escape', 'Mofle / silenciador completo Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 1590.00, 2650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-286', 'Carrocería', 'Guardabarros del./tras. Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-287', 'Carrocería', 'Tanque de gasolina Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-288', 'Carrocería', 'Asiento (sillín) Genérico', 'Universal / toda la gama', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-289', 'Carrocería', 'Plásticos / carenados Genuino Bajaj, Genérico', 'Boxer 150 y Boxer 150X (mismo motor)', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-290', 'Carrocería', 'Espejos Genérico', 'Universal / toda la gama', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-291', 'Carrocería', 'Manubrio (timón) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-292', 'Carrocería', 'Puños (grips) Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-293', 'Carrocería', 'Pedales (freno/cambio) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-294', 'Otros', 'Cable de acelerador Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-295', 'Otros', 'Soporte central / lateral (pata de cabra) Genuino Bajaj', 'Boxer 150 y Boxer 150X (mismo motor)', 372.00, 620.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-296', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Boxer CT100 / BM100', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-297', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Boxer CT100 / BM100', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-298', 'Motor', 'Cigüeñal Genuino Bajaj', 'Boxer CT100 / BM100', 1920.00, 3200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-299', 'Motor', 'Bielas Genuino Bajaj', 'Boxer CT100 / BM100', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-300', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-301', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Boxer CT100 / BM100', 2280.00, 3800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-302', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-303', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Boxer CT100 / BM100', 120.00, 200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-304', 'Motor', 'Guías de válvula Genuino Bajaj', 'Boxer CT100 / BM100', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-305', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Boxer CT100 / BM100', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-306', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Boxer CT100 / BM100', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-307', 'Motor', 'Árbol de levas Genuino Bajaj', 'Boxer CT100 / BM100', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-308', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-309', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Boxer CT100 / BM100', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-310', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Boxer CT100 / BM100 — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 48.00, 80.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-311', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Boxer CT100 / BM100', 384.00, 640.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-312', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Boxer CT100 / BM100', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-313', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 54.00, 90.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-314', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 66.00, 110.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-315', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Boxer CT100 / BM100', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-316', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Boxer CT100 / BM100', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-317', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-318', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Boxer CT100 / BM100', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-319', 'Transmisión', 'Corona trasera DID, EP Racing', 'Boxer CT100 / BM100', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-320', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Boxer CT100 / BM100', 456.00, 760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-321', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Boxer CT100 / BM100', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-322', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Boxer CT100 / BM100', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-323', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Boxer CT100 / BM100', 432.00, 720.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-324', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-325', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Boxer CT100 / BM100', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-326', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Boxer CT100 / BM100', 864.00, 1440.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-327', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Boxer CT100 / BM100', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-328', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 324.00, 540.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-329', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Boxer CT100 / BM100', 1128.00, 1880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-330', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Boxer CT100 / BM100', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-331', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-332', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-333', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Boxer CT100 / BM100', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-334', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-335', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 528.00, 880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-336', 'Frenos', 'Bomba de freno (cilindro maestro) Genuino Bajaj', 'Boxer CT100 / BM100', 768.00, 1280.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-337', 'Frenos', 'Manguera de freno Genérico', 'Universal / toda la gama', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-338', 'Frenos', 'Líquido de frenos DOT4 DOT4 (genérico)', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-339', 'Suspensión', 'Amortiguadores traseros YSS, Genérico', 'Universal / según chasis del modelo', 1056.00, 1760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-340', 'Suspensión', 'Horquilla / telescópica delantera Genuino Bajaj', 'Boxer CT100 / BM100', 1632.00, 2720.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-341', 'Suspensión', 'Retenedores de telescópica Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-342', 'Llantas', 'Llanta delantera Vee Rubber, CST', 'Según medida de rin del modelo', 1344.00, 2240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-343', 'Llantas', 'Llanta trasera Vee Rubber, CST', 'Según medida de rin del modelo', 1488.00, 2480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-344', 'Llantas', 'Cámara (tubo) Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-345', 'Llantas', 'Rines (aros) Genuino Bajaj', 'Boxer CT100 / BM100', 1128.00, 1880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-346', 'Llantas', 'Rodamientos de rueda Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-347', 'Carburación', 'Carburador completo Genuino Bajaj, Mikuni', 'Boxer CT100 / BM100', 912.00, 1520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-348', 'Carburación', 'Filtro de aire HiFlo, Genuino Bajaj', 'Boxer CT100 / BM100', 162.00, 270.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-349', 'Carburación', 'Filtro de gasolina Genérico', 'Universal / toda la gama', 84.00, 140.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ESC-350', 'Escape', 'Mofle / silenciador completo Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 1272.00, 2120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-351', 'Carrocería', 'Guardabarros del./tras. Genérico', 'Universal / toda la gama', 324.00, 540.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-352', 'Carrocería', 'Tanque de gasolina Genuino Bajaj', 'Boxer CT100 / BM100', 1920.00, 3200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-353', 'Carrocería', 'Asiento (sillín) Genérico', 'Universal / toda la gama', 912.00, 1520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-354', 'Carrocería', 'Plásticos / carenados Genuino Bajaj, Genérico', 'Boxer CT100 / BM100', 528.00, 880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-355', 'Carrocería', 'Espejos Genérico', 'Universal / toda la gama', 162.00, 270.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-356', 'Carrocería', 'Manubrio (timón) Genuino Bajaj', 'Boxer CT100 / BM100', 456.00, 760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-357', 'Carrocería', 'Puños (grips) Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-358', 'Carrocería', 'Pedales (freno/cambio) Genuino Bajaj', 'Boxer CT100 / BM100', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-359', 'Otros', 'Cable de acelerador Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-360', 'Otros', 'Soporte central / lateral (pata de cabra) Genuino Bajaj', 'Boxer CT100 / BM100', 300.00, 500.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-361', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Solo Boxer BM150 (legado)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-362', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-363', 'Motor', 'Cigüeñal Genuino Bajaj', 'Solo Boxer BM150 (legado)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-364', 'Motor', 'Bielas Genuino Bajaj', 'Solo Boxer BM150 (legado)', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-365', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 300.00, 500.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-366', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 2850.00, 4750.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-367', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-368', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Solo Boxer BM150 (legado)', 150.00, 250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-369', 'Motor', 'Guías de válvula Genuino Bajaj', 'Solo Boxer BM150 (legado)', 96.00, 160.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-370', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Solo Boxer BM150 (legado)', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-371', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-372', 'Motor', 'Árbol de levas Genuino Bajaj', 'Solo Boxer BM150 (legado)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-373', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-374', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Solo Boxer BM150 (legado)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-375', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Solo Boxer BM150 (legado) — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-376', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Solo Boxer BM150 (legado)', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-377', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 750.00, 1250.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-378', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 72.00, 120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-MOT-379', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 84.00, 140.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-380', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Solo Boxer BM150 (legado)', 930.00, 1550.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-381', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Solo Boxer BM150 (legado)', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-382', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-383', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Solo Boxer BM150 (legado)', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-384', 'Transmisión', 'Corona trasera DID, EP Racing', 'Solo Boxer BM150 (legado)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-385', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Solo Boxer BM150 (legado)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-386', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Solo Boxer BM150 (legado)', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-387', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-TRA-388', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Solo Boxer BM150 (legado)', 540.00, 900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-389', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 1200.00, 2000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-390', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Solo Boxer BM150 (legado)', 390.00, 650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-391', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Solo Boxer BM150 (legado)', 1080.00, 1800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-392', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-393', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-394', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Solo Boxer BM150 (legado)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-395', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-396', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-397', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ELÉ-398', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Solo Boxer BM150 (legado)', 840.00, 1400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-399', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-400', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-401', 'Frenos', 'Bomba de freno (cilindro maestro) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-402', 'Frenos', 'Manguera de freno Genérico', 'Universal / toda la gama', 288.00, 480.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-FRE-403', 'Frenos', 'Líquido de frenos DOT4 DOT4 (genérico)', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-404', 'Suspensión', 'Amortiguadores traseros YSS, Genérico', 'Universal / según chasis del modelo', 1320.00, 2200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-405', 'Suspensión', 'Horquilla / telescópica delantera Genuino Bajaj', 'Solo Boxer BM150 (legado)', 2040.00, 3400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-SUS-406', 'Suspensión', 'Retenedores de telescópica Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-407', 'Llantas', 'Llanta delantera Vee Rubber, CST', 'Según medida de rin del modelo', 1680.00, 2800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-408', 'Llantas', 'Llanta trasera Vee Rubber, CST', 'Según medida de rin del modelo', 1860.00, 3100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-409', 'Llantas', 'Cámara (tubo) Genérico', 'Universal / toda la gama', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-410', 'Llantas', 'Rines (aros) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 1410.00, 2350.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-LLA-411', 'Llantas', 'Rodamientos de rueda Genérico', 'Universal / toda la gama', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-412', 'Carburación', 'Carburador completo Genuino Bajaj, Mikuni', 'Solo Boxer BM150 (legado)', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-413', 'Carburación', 'Filtro de aire HiFlo, Genuino Bajaj', 'Solo Boxer BM150 (legado)', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-414', 'Carburación', 'Filtro de gasolina Genérico', 'Universal / toda la gama', 108.00, 180.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-ESC-415', 'Escape', 'Mofle / silenciador completo Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 1590.00, 2650.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-416', 'Carrocería', 'Guardabarros del./tras. Genérico', 'Universal / toda la gama', 408.00, 680.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-417', 'Carrocería', 'Tanque de gasolina Genuino Bajaj', 'Solo Boxer BM150 (legado)', 2400.00, 4000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-418', 'Carrocería', 'Asiento (sillín) Genérico', 'Universal / toda la gama', 1140.00, 1900.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-419', 'Carrocería', 'Plásticos / carenados Genuino Bajaj, Genérico', 'Solo Boxer BM150 (legado)', 660.00, 1100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-420', 'Carrocería', 'Espejos Genérico', 'Universal / toda la gama', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-421', 'Carrocería', 'Manubrio (timón) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 570.00, 950.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-422', 'Carrocería', 'Puños (grips) Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-CAR-423', 'Carrocería', 'Pedales (freno/cambio) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-424', 'Otros', 'Cable de acelerador Genérico', 'Universal / toda la gama', 144.00, 240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-BOX-OTR-425', 'Otros', 'Soporte central / lateral (pata de cabra) Genuino Bajaj', 'Solo Boxer BM150 (legado)', 372.00, 620.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-426', 'Motor', 'Pistón y anillos Genuino Bajaj', 'Solo Discover 125 5G', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-427', 'Motor', 'Cilindro (camisa) Genuino Bajaj', 'Solo Discover 125 5G', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-428', 'Motor', 'Cigüeñal Genuino Bajaj', 'Solo Discover 125 5G', 1920.00, 3200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-429', 'Motor', 'Bielas Genuino Bajaj', 'Solo Discover 125 5G', 480.00, 800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-430', 'Motor', 'Rodamientos de cigüeñal Genuino Bajaj, Genérico', 'Solo Discover 125 5G', 240.00, 400.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-431', 'Motor', 'Culata (cabezote) Genuino Bajaj', 'Solo Discover 125 5G', 2280.00, 3800.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-432', 'Motor', 'Kit de empacaduras/juntas de motor Genuino Bajaj, Genérico', 'Solo Discover 125 5G', 204.00, 340.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-433', 'Motor', 'Válvulas de admisión y escape Genuino Bajaj', 'Solo Discover 125 5G', 120.00, 200.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-434', 'Motor', 'Guías de válvula Genuino Bajaj', 'Solo Discover 125 5G', 78.00, 130.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-435', 'Motor', 'Resortes de válvula Genuino Bajaj', 'Solo Discover 125 5G', 60.00, 100.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-436', 'Motor', 'Balancines (taquetes) Genuino Bajaj', 'Solo Discover 125 5G', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-437', 'Motor', 'Árbol de levas Genuino Bajaj', 'Solo Discover 125 5G', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-438', 'Motor', 'Cadena de tiempo (distribución) Genuino Bajaj, Genérico', 'Solo Discover 125 5G', 192.00, 320.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-439', 'Motor', 'Tensor de cadena de tiempo Advik / Pricol (Genuino Bajaj)', 'Solo Discover 125 5G', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-440', 'Motor', 'Colador / malla de aceite centrífuga (no usa cartucho) Genuino Bajaj', 'Solo Discover 125 5G — se limpia en cada cambio de aceite, no se reemplaza como cartucho', 48.00, 80.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-441', 'Motor', 'Bomba de aceite Genuino Bajaj', 'Solo Discover 125 5G', 384.00, 640.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-442', 'Motor', 'Cárter (tapa de motor) Genuino Bajaj', 'Solo Discover 125 5G', 600.00, 1000.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-443', 'Motor', 'Sellos/retenedores de motor Genuino Bajaj, Genérico', 'Solo Discover 125 5G', 54.00, 90.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-MOT-444', 'Motor', 'Bujía NGK', 'Universal / toda la gama Bajaj', 66.00, 110.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-445', 'Transmisión', 'Kit de embrague (discos y platos) Genuino Bajaj, EP Racing', 'Solo Discover 125 5G', 744.00, 1240.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-446', 'Transmisión', 'Resortes de embrague Genuino Bajaj', 'Solo Discover 125 5G', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-447', 'Transmisión', 'Cable de embrague Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-448', 'Transmisión', 'Piñón delantero DID, EP Racing', 'Solo Discover 125 5G', 156.00, 260.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-449', 'Transmisión', 'Corona trasera DID, EP Racing', 'Solo Discover 125 5G', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-450', 'Transmisión', 'Cadena de transmisión DID, EP Racing', 'Solo Discover 125 5G', 456.00, 760.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-451', 'Transmisión', 'Kit de arrastre completo DID, EP Racing', 'Solo Discover 125 5G', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-452', 'Transmisión', 'Selector de cambios (pedal) Genuino Bajaj', 'Solo Discover 125 5G', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-TRA-453', 'Transmisión', 'Engranajes de caja de cambios Genuino Bajaj', 'Solo Discover 125 5G', 432.00, 720.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-454', 'Eléctrico', 'Batería Yuasa, GS', 'Universal / toda la gama Bajaj', 960.00, 1600.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-455', 'Eléctrico', 'Bobina de encendido Genuino Bajaj', 'Solo Discover 125 5G', 312.00, 520.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-456', 'Eléctrico', 'CDI / ECU Genuino Bajaj', 'Solo Discover 125 5G', 864.00, 1440.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-457', 'Eléctrico', 'Estator (bobina de carga) Genuino Bajaj', 'Solo Discover 125 5G', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-458', 'Eléctrico', 'Regulador / rectificador Genérico', 'Universal / toda la gama', 324.00, 540.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-459', 'Eléctrico', 'Motor de arranque Genuino Bajaj', 'Solo Discover 125 5G', 1128.00, 1880.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-460', 'Eléctrico', 'Switch de encendido (llave) Genuino Bajaj', 'Solo Discover 125 5G', 228.00, 380.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-461', 'Eléctrico', 'Foco delantero / bombillos Osram, Genérico', 'Universal / toda la gama', 114.00, 190.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-462', 'Eléctrico', 'Claxon (bocina) Genérico', 'Universal / toda la gama', 126.00, 210.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-ELÉ-463', 'Eléctrico', 'Cableado / arnés eléctrico Genuino Bajaj', 'Solo Discover 125 5G', 672.00, 1120.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-FRE-464', 'Frenos', 'Pastillas / bandas de freno EBC, Genérico', 'Universal / según sistema de freno del modelo', 252.00, 420.00, 50, 1, 'repuesto_generico.png'),
('BAJ-DIS-FRE-465', 'Frenos', 'Disco de freno Genuino Bajaj, EBC', 'Universal / según sistema de freno del modelo', 52.00, 88.00, 50, 1, 'repuesto_generico.png');



-- 7. CLIENTES DE PRUEBA
INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email) VALUES
('001-120590-0012A', 'Juan Perez', '8888-1111', 'juan.perez@email.com');

-- 8. MOTOCICLETAS DE PRUEBA
INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje) VALUES
(1, 'M-12345', 'Bajaj', 'Pulsar NS 200', 2021, 200);

-- 9. CITAS DE PRUEBA
INSERT INTO CitasWhatsApp (ClienteID, MotoID, FechaProgramada, TipoMantenimiento, Estado) VALUES
(1, 1, DATEADD(DAY, 1, GETDATE()), 'Preventivo', 'Confirmada');

-- 10. CAJA ABIERTA Y GASTOS
INSERT INTO ControlCaja (UsuarioID, MontoInicial, Estado) VALUES (2, 1500.00, 'Abierta');

INSERT INTO GastosOperativos (UsuarioID, Categoria, Descripcion, Monto) VALUES
(1, 'Servicios Basicos', 'Pago Recibo de Energia (DISNORTE)', 2500.00),
(1, 'Mantenimiento Local', 'Compra de articulos de limpieza (Liquidos, trapos)', 500.00);

GO
