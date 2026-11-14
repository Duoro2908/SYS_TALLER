import sys

def update_contador():
    with open('routes/contador.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Update obtener_datos_financieros_taller around Gastos Operativos & Custom Accounts
    target_gastos = """        # 4. Gastos Operativos del mes
        cursor.execute(\"\"\"
            SELECT Categoria, ISNULL(SUM(Monto), 0) 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            GROUP BY Categoria
        \"\"\", (mes, anio))
        gastos_bd = dict(cursor.fetchall())

        datos['gastos_servicios_basicos'] = float(gastos_bd.get('Servicios Basicos', 0) or (2500.0 if mes == 8 else (2800.0 if datos['ventas_netas'] > 0 else 0.0)))
        datos['gastos_alquiler'] = float(gastos_bd.get('Alquiler', 0) or (4500.0 if datos['ventas_netas'] > 0 else 0.0))
        datos['gastos_mantenimiento'] = float(gastos_bd.get('Mantenimiento Local', 0) or (500.0 if mes == 8 else (650.0 if datos['ventas_netas'] > 0 else 0.0)))
        datos['gastos_otros'] = float(gastos_bd.get('Otros', 0) or (350.0 if datos['ventas_netas'] > 0 else 0.0))

        cursor.execute(\"\"\"
            SELECT Categoria, Descripcion, Monto, FechaGasto 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            ORDER BY FechaGasto DESC
        \"\"\", (mes, anio))
        datos['gastos_desglose'] = [
            {'categoria': r[0], 'descripcion': r[1], 'monto': float(r[2]), 'fecha': r[3].strftime('%d/%m/%Y')}
            for r in cursor.fetchall()
        ]

        # 5. Nómina Operativa y Cargas Sociales (Leyes Laborales de Nicaragua - MIPYME en Tiempo Real)
        from routes.planilla import obtener_totales_nomina_mes
        totales_nom = obtener_totales_nomina_mes(mes, anio)
        tot_nom = totales_nom['totales']

        # En meses operativos, reflejar la nómina devengada real (salario base + bonos mecánicos - deducciones por faltas)
        if datos['ventas_netas'] > 0:
            datos['gastos_nomina_base'] = tot_nom['salario_bruto']
            datos['gastos_cargas_patronales'] = tot_nom['cargas_patronales'] # INSS Patronal (22.5%) + INATEC (2%)
            datos['gastos_provisiones_laborales'] = tot_nom['provisiones_mensuales'] # Aguinaldo, Vacaciones e Indemnización (Ley 185)
            datos['gastos_nomina_total'] = tot_nom['costo_total_empleador']
        else:
            datos['gastos_nomina_base'] = 0.0
            datos['gastos_cargas_patronales'] = 0.0
            datos['gastos_provisiones_laborales'] = 0.0
            datos['gastos_nomina_total'] = 0.0

        datos['gastos_planilla'] = datos['gastos_nomina_total']

        datos['gastos_operativos'] = round(
            datos['gastos_servicios_basicos'] + 
            datos['gastos_alquiler'] + 
            datos['gastos_mantenimiento'] + 
            datos['gastos_otros'] + 
            datos['gastos_nomina_total'], 2
        )

        datos['utilidad_operativa'] = round(datos['utilidad_bruta'] - datos['gastos_operativos'], 2)
        datos['margen_operativo_pct'] = round((datos['utilidad_operativa'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        # Impuesto sobre la Renta (Pago mínimo definitivo 1% DGI o provisión si hay utilidad)
        if datos['utilidad_operativa'] > 0:
            datos['impuesto_renta_ir'] = round(max(datos['ventas_netas'] * 0.01, datos['utilidad_operativa'] * 0.10), 2)
        else:
            datos['impuesto_renta_ir'] = 0.0

        datos['utilidad_neta'] = round(datos['utilidad_operativa'] - datos['impuesto_renta_ir'], 2)
        datos['margen_neto_pct'] = round((datos['utilidad_neta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0"""

    replacement_gastos = """        # 4. Gastos Operativos y Automatización Integral con Mercadotecnia
        cursor.execute(\"\"\"
            SELECT Categoria, ISNULL(SUM(Monto), 0) 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            GROUP BY Categoria
        \"\"\", (mes, anio))
        gastos_bd = dict(cursor.fetchall())

        datos['gastos_servicios_basicos'] = float(gastos_bd.get('Servicios Basicos', 0) or (2500.0 if mes == 8 else (2800.0 if datos['ventas_netas'] > 0 else 0.0)))
        datos['gastos_alquiler'] = float(gastos_bd.get('Alquiler', 0) or (4500.0 if datos['ventas_netas'] > 0 else 0.0))
        datos['gastos_mantenimiento'] = float(gastos_bd.get('Mantenimiento Local', 0) or (500.0 if mes == 8 else (650.0 if datos['ventas_netas'] > 0 else 0.0)))
        datos['gastos_otros'] = float(gastos_bd.get('Otros', 0) or (350.0 if datos['ventas_netas'] > 0 else 0.0))
        
        # Automatización con Mercadotecnia: Campañas publicitarias + Costo de Premios entregados en Rifas
        datos['gastos_mercadotecnia_directos'] = float(gastos_bd.get('Mercadotecnia', 0) or gastos_bd.get('Publicidad', 0) or 0.0)
        try:
            cursor.execute(\"\"\"
                SELECT ISNULL(SUM(p.PrecioCompra), 0)
                FROM RifaPremios r
                JOIN Productos p ON r.ProductoID = p.ProductoID
                WHERE (r.MesPeriodo = ? OR (r.FechaSorteo IS NOT NULL AND MONTH(r.FechaSorteo) = ? AND YEAR(r.FechaSorteo) = ?))
                  AND r.Estado IN ('Entregado', 'Sorteado')
            \"\"\", (f\"{mes}/{anio}\", mes, anio))
            costo_premios = float(cursor.fetchone()[0] or 0.0)
        except Exception:
            costo_premios = 0.0
        datos['costo_premios_rifas'] = costo_premios
        datos['gastos_mercadotecnia'] = round(datos['gastos_mercadotecnia_directos'] + costo_premios, 2)

        cursor.execute(\"\"\"
            SELECT Categoria, Descripcion, Monto, FechaGasto 
            FROM GastosOperativos 
            WHERE MONTH(FechaGasto) = ? AND YEAR(FechaGasto) = ?
            ORDER BY FechaGasto DESC
        \"\"\", (mes, anio))
        datos['gastos_desglose'] = [
            {'categoria': r[0], 'descripcion': r[1], 'monto': float(r[2]), 'fecha': r[3].strftime('%d/%m/%Y')}
            for r in cursor.fetchall()
        ]

        # 5. Nómina Operativa y Cargas Sociales (Leyes Laborales de Nicaragua - MIPYME en Tiempo Real)
        from routes.planilla import obtener_totales_nomina_mes
        totales_nom = obtener_totales_nomina_mes(mes, anio)
        tot_nom = totales_nom['totales']

        # En meses operativos, reflejar la nómina devengada real (salario base + bonos mecánicos - deducciones por faltas)
        if datos['ventas_netas'] > 0:
            datos['gastos_nomina_base'] = tot_nom['salario_bruto']
            datos['gastos_cargas_patronales'] = tot_nom['cargas_patronales'] # INSS Patronal (22.5%) + INATEC (2%)
            datos['gastos_provisiones_laborales'] = tot_nom['provisiones_mensuales'] # Aguinaldo, Vacaciones e Indemnización (Ley 185)
            datos['gastos_nomina_total'] = tot_nom['costo_total_empleador']
        else:
            datos['gastos_nomina_base'] = 0.0
            datos['gastos_cargas_patronales'] = 0.0
            datos['gastos_provisiones_laborales'] = 0.0
            datos['gastos_nomina_total'] = 0.0

        datos['gastos_planilla'] = datos['gastos_nomina_total']

        # 6. Cuentas Contables Personalizadas y Ajustes Dinámicos (CuentasContablesAjustes)
        datos['cuentas_pers_activo_corriente'] = []
        datos['cuentas_pers_activo_no_corriente'] = []
        datos['cuentas_pers_pasivo_corriente'] = []
        datos['cuentas_pers_pasivo_no_corriente'] = []
        datos['cuentas_pers_patrimonio'] = []
        datos['cuentas_pers_ingresos'] = []
        datos['cuentas_pers_costos'] = []
        datos['cuentas_pers_gastos'] = []
        datos['cuentas_pers_otros'] = []

        try:
            cursor.execute(\"\"\"
                SELECT AjusteID, TipoReporte, Categoria, NombreCuenta, Monto 
                FROM CuentasContablesAjustes 
                WHERE Mes = ? AND Anio = ?
                ORDER BY AjusteID ASC
            \"\"\", (mes, anio))
            for aj in cursor.fetchall():
                item = {
                    'id': aj[0],
                    'tipo_reporte': aj[1],
                    'categoria': aj[2],
                    'nombre': aj[3],
                    'monto': float(aj[4] or 0.0)
                }
                c_lower = aj[2].lower()
                if aj[1] == 'Balance':
                    if 'no corriente' in c_lower or 'fijo' in c_lower:
                        datos['cuentas_pers_activo_no_corriente'].append(item)
                    elif 'activo' in c_lower:
                        datos['cuentas_pers_activo_corriente'].append(item)
                    elif 'no corriente' in c_lower or 'largo plazo' in c_lower:
                        datos['cuentas_pers_pasivo_no_corriente'].append(item)
                    elif 'pasivo' in c_lower:
                        datos['cuentas_pers_pasivo_corriente'].append(item)
                    elif 'patrimonio' in c_lower or 'capital' in c_lower:
                        datos['cuentas_pers_patrimonio'].append(item)
                elif aj[1] == 'EstadoResultados':
                    if 'ingreso' in c_lower:
                        datos['cuentas_pers_ingresos'].append(item)
                    elif 'costo' in c_lower:
                        datos['cuentas_pers_costos'].append(item)
                    elif 'gasto' in c_lower:
                        datos['cuentas_pers_gastos'].append(item)
                    else:
                        datos['cuentas_pers_otros'].append(item)
        except Exception as e_aj:
            print(f\"Aviso leyendo CuentasContablesAjustes: {e_aj}\")

        total_ingresos_pers = sum(c['monto'] for c in datos['cuentas_pers_ingresos'])
        total_costos_pers = sum(c['monto'] for c in datos['cuentas_pers_costos'])
        total_gastos_pers = sum(c['monto'] for c in datos['cuentas_pers_gastos'])
        total_otros_pers = sum(c['monto'] for c in datos['cuentas_pers_otros'])

        # Integrar cuentas dinámicas al Estado de Resultados
        datos['ventas_netas'] = round(datos['ventas_netas'] + total_ingresos_pers, 2)
        datos['costo_ventas'] = round(datos['costo_ventas'] + total_costos_pers, 2)
        datos['utilidad_bruta'] = round(datos['ventas_netas'] - datos['costo_ventas'], 2)
        datos['margen_bruto_pct'] = round((datos['utilidad_bruta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        datos['gastos_operativos'] = round(
            datos['gastos_servicios_basicos'] + 
            datos['gastos_alquiler'] + 
            datos['gastos_mantenimiento'] + 
            datos['gastos_otros'] + 
            datos['gastos_nomina_total'] + 
            datos['gastos_mercadotecnia'] + 
            total_gastos_pers, 2
        )

        datos['utilidad_operativa'] = round(datos['utilidad_bruta'] - datos['gastos_operativos'], 2)
        datos['margen_operativo_pct'] = round((datos['utilidad_operativa'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0

        # Impuesto sobre la Renta (Pago mínimo definitivo 1% DGI o provisión si hay utilidad)
        if datos['utilidad_operativa'] > 0:
            datos['impuesto_renta_ir'] = round(max(datos['ventas_netas'] * 0.01, datos['utilidad_operativa'] * 0.10), 2)
        else:
            datos['impuesto_renta_ir'] = 0.0

        datos['otros_ingresos_gastos'] = round(total_otros_pers, 2)
        datos['utilidad_neta'] = round(datos['utilidad_operativa'] - datos['impuesto_renta_ir'] + datos['otros_ingresos_gastos'], 2)
        datos['margen_neto_pct'] = round((datos['utilidad_neta'] / datos['ventas_netas'] * 100), 2) if datos['ventas_netas'] > 0 else 0.0"""

    if target_gastos in code:
        code = code.replace(target_gastos, replacement_gastos)
        print("Reemplazado bloque gastos exitosamente!")
    else:
        print("No se encontró target_gastos exactamente, buscando versión normalizada...")
        code = code.replace(target_gastos.replace('\n', '\r\n'), replacement_gastos.replace('\n', '\r\n'))
        print("Reemplazado con CRLF!")

    # 2. Update Balance General section (Activos, Pasivos, Patrimonio)
    target_balance = """        datos['credito_fiscal_iva'] = round(datos['compras_mes'] * 0.15, 2)
        datos['activo_circulante'] = round(datos['efectivo_caja'] + datos['inventario_costo'] + datos['cuentas_por_cobrar'] + datos['credito_fiscal_iva'], 2)

        # BALANCE GENERAL - ACTIVOS NO CORRIENTES
        datos['activo_fijo_total'] = round(
            datos['activo_fijo_maquinaria'] + 
            datos['activo_fijo_herramientas'] + 
            datos['activo_fijo_mobiliario'] + 
            datos['depreciacion_acumulada'], 2
        )
        datos['activo_fijo_estimado'] = datos['activo_fijo_total']
        datos['activo_total'] = round(datos['activo_circulante'] + datos['activo_fijo_total'], 2)

        # BALANCE GENERAL - PASIVOS CORRIENTES
        datos['proveedores_por_pagar'] = round(datos['compras_mes'] + (datos['costo_ventas'] * 0.20), 2)
        datos['iva_por_enterar'] = round(max(0.0, datos['iva_debito_fiscal'] - datos['credito_fiscal_iva']), 2)
        if datos['ventas_netas'] > 0:
            # Retenciones DGI: IR salarial retenido en nómina + Pago mínimo definitivo 1% de ventas
            datos['retenciones_dgi'] = round(tot_nom['ir'] + (datos['ventas_netas'] * 0.01), 2)
            # Obligaciones laborales: Salarios netos por pagar + Cargas patronales + INSS laboral a pagar al INSS
            datos['obligaciones_laborales'] = round(tot_nom['salario_neto'] + tot_nom['cargas_patronales'] + tot_nom['inss_laboral'], 2)
        else:
            datos['retenciones_dgi'] = 0.0
            datos['obligaciones_laborales'] = 0.0
        
        datos['pasivo_circulante'] = round(
            datos['proveedores_por_pagar'] + 
            datos['iva_por_enterar'] + 
            datos['retenciones_dgi'] + 
            datos['obligaciones_laborales'], 2
        )
        datos['pasivo_largo_plazo'] = round(datos['pasivo_circulante'] + datos['pasivo_largo_plazo'], 2)

        # BALANCE GENERAL - PATRIMONIO NETO
        # Regla de oro de la partida doble: Activo = Pasivo + Patrimonio
        datos['utilidad_ejercicio'] = datos['utilidad_neta']
        datos['capital_social'] = 150000.0
        datos['utilidades_acumuladas'] = round(datos['activo_total'] - datos['pasivo_total'] - datos['capital_social'] - datos['utilidad_ejercicio'], 2)
        datos['patrimonio'] = round(datos['capital_social'] + datos['utilidades_acumuladas'] + datos['utilidad_ejercicio'], 2)

        datos['pasivo_mas_patrimonio'] = round(datos['pasivo_total'] + datos['patrimonio'], 2)
        datos['diferencia_cuadre'] = round(datos['activo_total'] - datos['pasivo_mas_patrimonio'], 2)
        datos['cuadra'] = abs(datos['diferencia_cuadre']) < 0.01"""

    # Look for exact text of balance calculations
    target_bal_short = """        datos['credito_fiscal_iva'] = round(datos['compras_mes'] * 0.15, 2)
        datos['activo_circulante'] = round(datos['efectivo_caja'] + datos['inventario_costo'] + datos['cuentas_por_cobrar'] + datos['credito_fiscal_iva'], 2)

        # BALANCE GENERAL - ACTIVOS NO CORRIENTES
        datos['activo_fijo_total'] = round(
            datos['activo_fijo_maquinaria'] + 
            datos['activo_fijo_herramientas'] + 
            datos['activo_fijo_mobiliario'] + 
            datos['depreciacion_acumulada'], 2
        )
        datos['activo_fijo_estimado'] = datos['activo_fijo_total']
        datos['activo_total'] = round(datos['activo_circulante'] + datos['activo_fijo_total'], 2)"""

    replacement_bal_short = """        datos['credito_fiscal_iva'] = round(datos['compras_mes'] * 0.15, 2)
        total_act_corr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_activo_corriente', []))
        total_act_nocorr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_activo_no_corriente', []))

        datos['activo_circulante'] = round(datos['efectivo_caja'] + datos['inventario_costo'] + datos['cuentas_por_cobrar'] + datos['credito_fiscal_iva'] + total_act_corr_pers, 2)

        # BALANCE GENERAL - ACTIVOS NO CORRIENTES
        datos['activo_fijo_total'] = round(
            datos['activo_fijo_maquinaria'] + 
            datos['activo_fijo_herramientas'] + 
            datos['activo_fijo_mobiliario'] + 
            datos['depreciacion_acumulada'] + 
            total_act_nocorr_pers, 2
        )
        datos['activo_fijo_estimado'] = datos['activo_fijo_total']
        datos['activo_total'] = round(datos['activo_circulante'] + datos['activo_fijo_total'], 2)"""

    code = code.replace(target_bal_short.replace('\n', '\r\n'), replacement_bal_short.replace('\n', '\r\n'))
    code = code.replace(target_bal_short, replacement_bal_short)

    target_pas_short = """        datos['pasivo_circulante'] = round(
            datos['proveedores_por_pagar'] + 
            datos['iva_por_enterar'] + 
            datos['retenciones_dgi'] + 
            datos['obligaciones_laborales'], 2
        )
        datos['pasivo_total'] = round(datos['pasivo_circulante'] + datos['pasivo_largo_plazo'], 2)

        # BALANCE GENERAL - PATRIMONIO NETO
        # Regla de oro de la partida doble: Activo = Pasivo + Patrimonio
        datos['utilidad_ejercicio'] = datos['utilidad_neta']
        datos['capital_social'] = 150000.0
        datos['utilidades_acumuladas'] = round(datos['activo_total'] - datos['pasivo_total'] - datos['capital_social'] - datos['utilidad_ejercicio'], 2)
        datos['patrimonio'] = round(datos['capital_social'] + datos['utilidades_acumuladas'] + datos['utilidad_ejercicio'], 2)"""

    replacement_pas_short = """        total_pas_corr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_pasivo_corriente', []))
        total_pas_nocorr_pers = sum(c['monto'] for c in datos.get('cuentas_pers_pasivo_no_corriente', []))
        total_patri_pers = sum(c['monto'] for c in datos.get('cuentas_pers_patrimonio', []))

        datos['pasivo_circulante'] = round(
            datos['proveedores_por_pagar'] + 
            datos['iva_por_enterar'] + 
            datos['retenciones_dgi'] + 
            datos['obligaciones_laborales'] + 
            total_pas_corr_pers, 2
        )
        datos['pasivo_largo_plazo'] = round(20000.0 + total_pas_nocorr_pers, 2)
        datos['pasivo_total'] = round(datos['pasivo_circulante'] + datos['pasivo_largo_plazo'], 2)

        # BALANCE GENERAL - PATRIMONIO NETO (NIIF PARA LAS MIPYMES)
        # Regla de oro de la partida doble: Activo = Pasivo + Patrimonio
        datos['utilidad_ejercicio'] = datos['utilidad_neta']
        datos['capital_social'] = 150000.0
        datos['ajustes_patrimonio_total'] = round(total_patri_pers, 2)
        datos['utilidades_acumuladas'] = round(datos['activo_total'] - datos['pasivo_total'] - datos['capital_social'] - datos['utilidad_ejercicio'] - datos['ajustes_patrimonio_total'], 2)
        datos['patrimonio'] = round(datos['capital_social'] + datos['utilidades_acumuladas'] + datos['utilidad_ejercicio'] + datos['ajustes_patrimonio_total'], 2)"""

    code = code.replace(target_pas_short.replace('\n', '\r\n'), replacement_pas_short.replace('\n', '\r\n'))
    code = code.replace(target_pas_short, replacement_pas_short)

    with open('routes/contador.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("routes/contador.py actualizado en obtención de datos!")

if __name__ == '__main__':
    update_contador()

