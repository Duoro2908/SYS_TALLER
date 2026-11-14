"""
====================================================================
MÓDULO DE ESTADÍSTICAS DEL TALLER Y GERENCIA (routes/estadisticas.py)
Taller y Lubricantes CR
Controlador analítico, métricas operacionales, KPIs ejecutivos
y panel estadístico para Martha Jovana (Administradora de Estadísticas)
y Gerencia General.
====================================================================
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from database import get_db_connection

estadisticas_bp = Blueprint('gerencia', __name__)
gerencia_bp = estadisticas_bp


def obtener_estadisticas_taller():
    """Calcula todas las métricas operativas, financieras y de rendimiento del taller."""
    conn = get_db_connection()
    stats = {
        'ingresos_mes': 0.0,
        'gastos_mes': 0.0,
        'compras_mes': 0.0,
        'utilidad_neta': 0.0,
        'margen_beneficio': 0.0,
        'ordenes_activas': 0,
        'ordenes_facturadas_mes': 0,
        'total_ordenes_historico': 0,
        'ticket_promedio': 0.0,
        'total_mano_obra': 0.0,
        'total_repuestos': 0.0,
        'pct_mano_obra': 50.0,
        'pct_repuestos': 50.0,
        'valor_inventario': 0.0,
        'alertas_stock': 0,
        'total_clientes': 0,
        'citas_no_asistidas': 0,
        'citas_programadas_mes': 0,
        'empleados_activos': 0,
        'labels_grafico': [],
        'datos_grafico': [],
        'ordenes_grafico': [],
        'servicios_labels': [],
        'servicios_counts': [],
        'servicios_montos': [],
        'mecanicos_labels': [],
        'mecanicos_ordenes': [],
        'mecanicos_montos': [],
        'mecanicos_cards': [],
        'marcas_labels': [],
        'marcas_counts': [],
        'top_repuestos': [],
        'producto_estrella': 'N/A',
        'top_servicios': [],
        'estados_pipeline': {
            'En Diagnostico': 0,
            'Cotizado': 0,
            'Aprobado': 0,
            'En Proceso': 0,
            'Finalizado': 0,
            'Facturada': 0
        },
        'ordenes_recientes': []
    }
    
    if not conn:
        return stats
        
    try:
        c = conn.cursor()
        
        # 1. Resumen Financiero del Mes Actual
        c.execute("""
            SELECT ISNULL(SUM(TotalNeto), 0) FROM Facturas 
            WHERE Estado = 'Pagada' AND MONTH(FechaEmision) = MONTH(GETDATE()) AND YEAR(FechaEmision) = YEAR(GETDATE())
        """)
        stats['ingresos_mes'] = float(c.fetchone()[0] or 0.0)

        c.execute("""
            SELECT ISNULL(SUM(Monto), 0) FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = MONTH(GETDATE()) AND YEAR(FechaGasto) = YEAR(GETDATE())
        """)
        stats['gastos_mes'] = float(c.fetchone()[0] or 0.0)

        c.execute("""
            SELECT ISNULL(SUM(TotalCompra), 0) FROM Compras 
            WHERE MONTH(FechaCompra) = MONTH(GETDATE()) AND YEAR(FechaCompra) = YEAR(GETDATE())
        """)
        stats['compras_mes'] = float(c.fetchone()[0] or 0.0)

        stats['utilidad_neta'] = stats['ingresos_mes'] - stats['gastos_mes'] - stats['compras_mes']
        if stats['ingresos_mes'] > 0:
            stats['margen_beneficio'] = round((stats['utilidad_neta'] / stats['ingresos_mes']) * 100, 2)

        # 2. Operaciones del Taller
        c.execute("""
            SELECT COUNT(OrdenID) FROM OrdenesTrabajo 
            WHERE Estado IN ('En Diagnostico', 'Cotizado', 'Aprobado', 'En Proceso')
        """)
        stats['ordenes_activas'] = c.fetchone()[0] or 0

        c.execute("""
            SELECT COUNT(OrdenID) FROM OrdenesTrabajo 
            WHERE Estado = 'Facturada' AND MONTH(FechaIngreso) = MONTH(GETDATE()) AND YEAR(FechaIngreso) = YEAR(GETDATE())
        """)
        stats['ordenes_facturadas_mes'] = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(OrdenID) FROM OrdenesTrabajo")
        stats['total_ordenes_historico'] = c.fetchone()[0] or 0

        if stats['ordenes_facturadas_mes'] > 0:
            stats['ticket_promedio'] = round(stats['ingresos_mes'] / stats['ordenes_facturadas_mes'], 2)

        # 3. Mano de Obra vs Repuestos
        c.execute("""
            SELECT ISNULL(SUM(mo.CostoSugerido), 0)
            FROM OrdenManoObra mo
            JOIN OrdenesTrabajo ot ON mo.OrdenID = ot.OrdenID
            WHERE ot.Estado = 'Facturada'
        """)
        stats['total_mano_obra'] = float(c.fetchone()[0] or 0.0)

        c.execute("""
            SELECT ISNULL(SUM(p.PrecioVenta * or_rep.Cantidad), 0)
            FROM OrdenRepuestos or_rep
            JOIN Productos p ON or_rep.ProductoID = p.ProductoID
            JOIN OrdenesTrabajo ot ON or_rep.OrdenID = ot.OrdenID
            WHERE ot.Estado = 'Facturada'
        """)
        stats['total_repuestos'] = float(c.fetchone()[0] or 0.0)

        total_comp = stats['total_mano_obra'] + stats['total_repuestos']
        if total_comp > 0:
            stats['pct_mano_obra'] = round((stats['total_mano_obra'] / total_comp) * 100, 1)
            stats['pct_repuestos'] = round((stats['total_repuestos'] / total_comp) * 100, 1)

        # 4. Inventario y Alertas
        c.execute("SELECT ISNULL(SUM(PrecioCompra * StockActual), 0) FROM Productos WHERE Activo = 1")
        stats['valor_inventario'] = float(c.fetchone()[0] or 0.0)

        c.execute("SELECT COUNT(ProductoID) FROM Productos WHERE StockActual < 5 AND Activo = 1")
        stats['alertas_stock'] = c.fetchone()[0] or 0

        # 5. Clientes y Citas WhatsApp
        c.execute("SELECT COUNT(ClienteID) FROM Clientes")
        stats['total_clientes'] = c.fetchone()[0] or 0

        c.execute("""
            SELECT COUNT(CitaID) FROM CitasWhatsApp 
            WHERE Estado = 'No Asistio' AND MONTH(FechaProgramada) = MONTH(GETDATE()) AND YEAR(FechaProgramada) = YEAR(GETDATE())
        """)
        stats['citas_no_asistidas'] = c.fetchone()[0] or 0

        c.execute("""
            SELECT COUNT(CitaID) FROM CitasWhatsApp 
            WHERE MONTH(FechaProgramada) = MONTH(GETDATE()) AND YEAR(FechaProgramada) = YEAR(GETDATE())
        """)
        stats['citas_programadas_mes'] = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(UsuarioID) FROM Usuarios WHERE Activo = 1 AND RolID != 1")
        stats['empleados_activos'] = c.fetchone()[0] or 0

        # 6. Gráfico de Ingresos y Volumen de Órdenes (Últimos 6 meses)
        c.execute("""
            SELECT 
                CONCAT(LEFT(DATENAME(month, FechaEmision), 3), ' ', YEAR(FechaEmision)) as Mes,
                SUM(TotalNeto) as Total,
                COUNT(FacturaID) as NumFacturas,
                MONTH(FechaEmision) as NumMes,
                YEAR(FechaEmision) as NumAnio
            FROM Facturas
            WHERE Estado = 'Pagada' AND FechaEmision >= DATEADD(month, -5, GETDATE())
            GROUP BY DATENAME(month, FechaEmision), MONTH(FechaEmision), YEAR(FechaEmision)
            ORDER BY NumAnio ASC, NumMes ASC
        """)
        ingresos_hist = c.fetchall()
        if ingresos_hist:
            stats['labels_grafico'] = [r[0] for r in ingresos_hist]
            stats['datos_grafico'] = [float(r[1]) for r in ingresos_hist]
            stats['ordenes_grafico'] = [int(r[2]) for r in ingresos_hist]

        # 7. Servicios agrupados (Gráfico Dona)
        c.execute("""
            SELECT ot.TipoServicio, COUNT(ot.OrdenID) as Conteo,
                   ISNULL(SUM(mo.CostoSugerido), 0) as TotalMonto
            FROM OrdenesTrabajo ot
            LEFT JOIN OrdenManoObra mo ON ot.OrdenID = mo.OrdenID
            GROUP BY ot.TipoServicio
            ORDER BY Conteo DESC
        """)
        servicios = c.fetchall()
        if servicios:
            stats['servicios_labels'] = [r[0] for r in servicios]
            stats['servicios_counts'] = [int(r[1]) for r in servicios]
            stats['servicios_montos'] = [float(r[2]) for r in servicios]

        # 8. Rendimiento Mecánicos (Gráfico Barras)
        c.execute("""
            SELECT u.NombreCompleto, 
                   COUNT(DISTINCT ot.OrdenID) as TotalOrdenes,
                   ISNULL(SUM(mo.CostoSugerido), 0) as TotalManoObra
            FROM Usuarios u
            LEFT JOIN OrdenesTrabajo ot ON u.UsuarioID = ot.MecanicoID
            LEFT JOIN OrdenManoObra mo ON ot.OrdenID = mo.OrdenID
            WHERE u.RolID = 3 AND u.Activo = 1
            GROUP BY u.NombreCompleto
            ORDER BY TotalOrdenes DESC
        """)
        mecanicos = c.fetchall()
        if mecanicos:
            stats['mecanicos_labels'] = [r[0] for r in mecanicos]
            stats['mecanicos_ordenes'] = [int(r[1]) for r in mecanicos]
            stats['mecanicos_montos'] = [float(r[2]) for r in mecanicos]
            stats['mecanicos_cards'] = [{'nombre': r[0], 'ordenes': int(r[1]), 'monto': float(r[2])} for r in mecanicos]

        # 9. Top Marcas Motocicletas
        c.execute("""
            SELECT TOP 6 m.Marca, COUNT(ot.OrdenID) as Total
            FROM OrdenesTrabajo ot
            JOIN Motocicletas m ON ot.MotoID = m.MotoID
            GROUP BY m.Marca
            ORDER BY Total DESC
        """)
        marcas = c.fetchall()
        if marcas:
            stats['marcas_labels'] = [r[0] for r in marcas]
            stats['marcas_counts'] = [int(r[1]) for r in marcas]

        # 10. Top Repuestos instalados en taller
        c.execute("""
            SELECT TOP 6 p.Nombre, ISNULL(SUM(or_rep.Cantidad), 0) as CantidadUsada, p.StockActual, p.PrecioVenta
            FROM OrdenRepuestos or_rep
            JOIN Productos p ON or_rep.ProductoID = p.ProductoID
            JOIN OrdenesTrabajo ot ON or_rep.OrdenID = ot.OrdenID
            GROUP BY p.Nombre, p.StockActual, p.PrecioVenta
            ORDER BY CantidadUsada DESC
        """)
        top_rep = c.fetchall()
        if top_rep:
            stats['top_repuestos'] = [
                {'nombre': r[0], 'cantidad': int(r[1]), 'stock': int(r[2]), 'precio': float(r[3]), 'total': int(r[1]) * float(r[3])}
                for r in top_rep
            ]
            stats['producto_estrella'] = stats['top_repuestos'][0]['nombre']

        # 11. Top Servicios Mano de Obra
        c.execute("""
            SELECT TOP 6 DescripcionServicio, COUNT(*) as Frecuencia, AVG(CostoSugerido) as CostoPromedio, SUM(CostoSugerido) as TotalGenerado
            FROM OrdenManoObra
            GROUP BY DescripcionServicio
            ORDER BY Frecuencia DESC
        """)
        top_serv = c.fetchall()
        if top_serv:
            stats['top_servicios'] = [
                {'descripcion': r[0], 'frecuencia': int(r[1]), 'promedio': float(r[2]), 'total': float(r[3])}
                for r in top_serv
            ]

        # 12. Pipeline de Estados
        c.execute("SELECT Estado, COUNT(*) as Total FROM OrdenesTrabajo GROUP BY Estado")
        for estado, total in c.fetchall():
            if estado in stats['estados_pipeline']:
                stats['estados_pipeline'][estado] = total

        # 13. Órdenes Recientes
        c.execute("""
            SELECT TOP 8 ot.OrdenID, c.NombreCompleto as Cliente, m.Marca, m.Modelo, m.Placa,
                         ISNULL(u.NombreCompleto, 'Sin Asignar') as Mecanico, ot.TipoServicio, ot.Estado,
                         FORMAT(ot.FechaIngreso, 'dd/MM/yyyy HH:mm') as FechaIngreso
            FROM OrdenesTrabajo ot
            JOIN Motocicletas m ON ot.MotoID = m.MotoID
            JOIN Clientes c ON m.ClienteID = c.ClienteID
            LEFT JOIN Usuarios u ON ot.MecanicoID = u.UsuarioID
            ORDER BY ot.OrdenID DESC
        """)
        stats['ordenes_recientes'] = [
            {
                'orden_id': r[0],
                'cliente': r[1],
                'moto': f"{r[2]} {r[3]} ({r[4]})",
                'mecanico': r[5],
                'servicio': r[6],
                'estado': r[7],
                'fecha': r[8]
            }
            for r in c.fetchall()
        ]
        
    except Exception as e:
        print(f"Error calculando estadísticas del taller: {e}")
    finally:
        conn.close()

    return stats


@estadisticas_bp.route('/estadisticas_taller')
@estadisticas_bp.route('/gerencia')
def estadisticas():
    """Vista ejecutiva del Dashboard de Estadísticas del Taller."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    rol_id = session.get('rol_id')
    rol_nombre = session.get('rol_nombre', '')
    if rol_id not in [1, 5, 1009] and 'Estadística' not in rol_nombre and 'Estadistica' not in rol_nombre:
        flash("Acceso denegado a las estadísticas del taller.", "error")
        return redirect(url_for('auth.login'))
        
    stats = obtener_estadisticas_taller()
    return render_template('dashboard/estadisticas_taller.html', stats=stats)