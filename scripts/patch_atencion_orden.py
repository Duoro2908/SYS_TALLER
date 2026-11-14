with open('routes/atencion.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        cursor.execute("""
            INSERT INTO OrdenesTrabajo (MotoID, TipoServicio, Estado, FechaIngreso, KilometrajeIngreso, ProblemaReportado, CitaID)
            OUTPUT INSERTED.OrdenID
            VALUES (?, ?, 'Pendiente de Pago', GETDATE(), 0, ?, ?)
        """, (moto_id, tipo_servicio or 'Preventivo', f"Ingreso automático por Cita WhatsApp #{cita_id}. {notas or ''}", cita_id))
        
        orden_id = cursor.fetchone()[0]
        
        cursor.execute("UPDATE CitasWhatsApp SET Estado = 'Confirmada' WHERE CitaID = ?", (cita_id,))
        
        conn.commit()
        flash(f'¡Éxito! Se ha creado la Orden de Trabajo #{orden_id} a partir de la Cita #{cita_id}.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al generar Orden de Trabajo: {e}', 'error')
    finally:
        conn.close()
        
    return _safe_atencion_redirect('atencion.citas_whatsapp')'''

replacement = '''        # Obtener mecánico activo para asignación de la orden en Taller
        mecanico_id = session.get('usuario_id') if session.get('rol_id') in [1, 3] else None
        if not mecanico_id:
            cursor.execute("SELECT TOP 1 UsuarioID FROM Usuarios WHERE RolID = 3 AND Activo = 1")
            mec_row = cursor.fetchone()
            mecanico_id = mec_row[0] if mec_row else 1

        tipo_srv = tipo_servicio or 'Preventivo'
        cursor.execute("SELECT TOP 1 PrecioBase, DescripcionDetallada FROM CatalogoMantenimientos WHERE Tipo = ?", (tipo_srv,))
        cat_row = cursor.fetchone()
        costo_mano_obra = float(cat_row[0]) if cat_row and cat_row[0] else 350.0
        desc_detallada = cat_row[1] if cat_row and cat_row[1] else f"Mantenimiento {tipo_srv}"

        # 1. Crear Orden de Trabajo en estado 'En Proceso' (inicia formalmente el mantenimiento en Taller)
        cursor.execute("""
            INSERT INTO OrdenesTrabajo (MotoID, MecanicoID, TipoServicio, Estado, FechaIngreso, KilometrajeIngreso, ProblemaReportado, CitaID)
            OUTPUT INSERTED.OrdenID
            VALUES (?, ?, ?, 'En Proceso', GETDATE(), 0, ?, ?)
        """, (moto_id, mecanico_id, tipo_srv, f"Mantenimiento iniciado desde Cita WhatsApp #{cita_id}. {notas or ''}", cita_id))
        
        orden_id = cursor.fetchone()[0]
        
        # 2. Registrar Mano de Obra inicial
        cursor.execute("""
            INSERT INTO OrdenManoObra (OrdenID, DescripcionServicio, CostoSugerido)
            VALUES (?, ?, ?)
        """, (orden_id, f"Mantenimiento {tipo_srv} - {desc_detallada}", costo_mano_obra))

        # 3. Marcar cita WhatsApp como Confirmada
        cursor.execute("UPDATE CitasWhatsApp SET Estado = 'Confirmada' WHERE CitaID = ?", (cita_id,))
        
        conn.commit()
        flash(f'¡Éxito! Orden de Trabajo #{orden_id} generada y enviada al Taller. El mantenimiento ha iniciado en estado "En Proceso".', 'success')
        conn.close()

        if session.get('rol_id') in [1, 3]:
            return redirect(url_for('mechanic.ordenes_list'))
        return redirect(url_for('atencion.citas_whatsapp'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Error al generar Orden de Trabajo para el Taller: {e}', 'error')
        return _safe_atencion_redirect('atencion.citas_whatsapp')'''

norm_content = content.replace('\r\n', '\n')
norm_target = target.replace('\r\n', '\n')
norm_replacement = replacement.replace('\r\n', '\n')

if norm_target in norm_content:
    norm_content = norm_content.replace(norm_target, norm_replacement, 1)
    with open('routes/atencion.py', 'w', encoding='utf-8') as f:
        f.write(norm_content)
    print("SUCCESS")
else:
    print("FAIL: Target not found")

