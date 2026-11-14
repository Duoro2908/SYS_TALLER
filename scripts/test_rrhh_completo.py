import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import get_db_connection
from routes.contador import obtener_datos_financieros_taller

def test_rrhh_completo():
    client = app.test_client()
    print("=== TEST RECURSOS HUMANOS: PLANILLA MIPYME, LEY 185, DGI, BONOS Y CONTRATOS ===")

    # 0. Limpiar cualquier novedad residual del test para partir de la base exacta
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM NovedadesNomina WHERE UsuarioID = 4 AND Mes = 10 AND Anio = 2026")
    conn.commit()
    conn.close()

    # 1. Simular sesión de Administrador / RRHH
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['nombre_completo'] = 'Administrador General'
        sess['rol_id'] = 1
        sess['rol_nombre'] = 'Super Administrador'

    # 2. Probar Planilla de Pago (/admin/planilla)
    resp_plan = client.get('/admin/planilla')
    print(f"GET /admin/planilla -> {resp_plan.status_code}")
    assert resp_plan.status_code == 200, f"Error en planilla: {resp_plan.status_code}"
    html_plan = resp_plan.data.decode('utf-8')

    # Verificaciones Legales y Fiscales
    assert 'Ley 185' in html_plan, "Ley 185 no mencionada en planilla"
    assert 'Ley 822' in html_plan, "Ley 822 DGI no mencionada en planilla"
    assert 'INSS Lab' in html_plan, "Deducción INSS Laboral no encontrada"

    # Verificación de exclusión de Elvin Alexander y Erwind
    assert 'Elvin Alexander' not in html_plan, "Elvin Alexander es el creador del sistema y no debe aparecer en la planilla"
    assert 'Erwind Bismark Cruz Ruiz' not in html_plan, "Erwind no debe estar en la planilla"

    # Verificación de salarios a escala MIPYME
    assert 'C$ 12,000.00' in html_plan or '12,000' in html_plan, "Salario de Gerente (C$ 12,000) no encontrado"
    assert 'C$ 3,500.00' in html_plan or '3,500' in html_plan, "Salario de Martha (C$ 3,500) no encontrado"
    assert 'Carlos Rene Gavarrete Calero' in html_plan, "Carlos debe estar en la planilla de pago"
    assert html_plan.count('Carlos Rene Gavarrete Calero') == html_plan.count('Martha Jovana Lopez Chavarria'), "Carlos debe figurar como un único asesor en la planilla"
    assert 'C$ 4,500.00' in html_plan or '4,500' in html_plan, "Salario de Carlos como asesor (C$ 4,500) no encontrado"

    # Verificación de bonos de mecánicos (Elmerson Cruz 6 vehículos = 1 bono de C$ 500)
    assert 'Bono' in html_plan, "Sección de bonos no encontrada"
    assert 'C$ 76,300.00' in html_plan or '76,300' in html_plan, "Salario base consolidado MIPYME (C$ 76,300) debe estar presente"
    assert 'C$ 76,800.00' in html_plan or '76,800' in html_plan, "Salario bruto total devengado (C$ 76,800) debe estar presente"
    print("[OK] Planilla de Pago MIPYME con salarios reales, bonos de mecánicos y Elvin excluido: 100% FUNCIONANDO")

    # 3. Probar API de información de ajuste (/admin/planilla/ajuste_info/<id>)
    resp_info = client.get('/admin/planilla/ajuste_info/5')
    assert resp_info.status_code == 200, f"Error en ajuste_info: {resp_info.status_code}"
    info_json = resp_info.get_json()
    assert info_json['usuario_id'] == 5
    assert info_json['es_mecanico'] is True
    assert info_json['vehiculos_atendidos'] >= 5, "Mecánico Elmerson debe tener vehículos atendidos"
    assert info_json['bono_vehiculos'] >= 500.0, "Mecánico debe tener bono calculado por cada 5 vehículos"
    print(f"[OK] API ajuste_info para mecánico Elmerson: {info_json['vehiculos_atendidos']} veh. atendidos -> Bono C$ {info_json['bono_vehiculos']:,.2f}")

    # Probar que Elvin Alexander (ID: 1) no permite ajuste en nómina
    resp_info_elvin = client.get('/admin/planilla/ajuste_info/1')
    assert resp_info_elvin.status_code == 400, "Elvin Alexander (ID: 1) debe retornar error 400 en ajuste de nómina"
    print("[OK] Validación estricta de exclusión para Elvin Alexander: 100% PROTEGIDO")

    # 4. Probar Guardar Ajuste en Nómina (/admin/planilla/guardar_ajuste)
    # Simular que el mecánico José Cooper (ID: 4) tuvo 5 vehículos y 1 día faltado
    resp_post = client.post('/admin/planilla/guardar_ajuste', json={
        'usuario_id': 4,
        'mes': 10,
        'anio': 2026,
        'salario_base': 8500.00,
        'dias_faltados': 1,
        'otras_deducciones': 0.0,
        'motivo_deduccion': '',
        'bonos_extras': 0.0,
        'motivo_bono': '',
        'vehiculos_atendidos': 5,
        'tasa_bono_vehiculo': 500.0
    })
    assert resp_post.status_code == 200, f"Error al guardar ajuste: {resp_post.status_code}"
    res_data = resp_post.get_json()
    assert res_data['success'] is True, "El guardado de novedades debió ser exitoso"

    # Verificar que el ajuste impacta directamente en los Estados Financieros en tiempo real
    fin = obtener_datos_financieros_taller(10, 2026)
    assert fin['cuadra'] is True, "El balance general debe cuadrar perfectamente en tiempo real (Activo = Pasivo + Patrimonio)"
    print(f"[OK] Estados Financieros recalculados en tiempo real: Nómina Base C$ {fin['gastos_nomina_base']:,.2f} | Cargas C$ {fin['gastos_cargas_patronales']:,.2f} | Balance Cuadra: {fin['cuadra']}")

    # 5. Probar Colilla de Pago (/admin/planilla/colilla/5)
    resp_col = client.get('/admin/planilla/colilla/5')
    print(f"GET /admin/planilla/colilla/5 -> {resp_col.status_code}")
    assert resp_col.status_code == 200, f"Error en colilla: {resp_col.status_code}"
    html_col = resp_col.data.decode('utf-8')
    assert 'Elmerson Daniel Cruz Ruiz' in html_col
    assert 'Bono de Productividad Taller' in html_col
    assert 'J0310000123456' in html_col
    print("[OK] Colilla de Pago de mecánico con desglose de bonos y deducciones: FUNCIONA AL 100%")

    # 6. Probar que Elvin Alexander (ID: 1) no emite colilla
    resp_col_elvin = client.get('/admin/planilla/colilla/1')
    assert resp_col_elvin.status_code == 302, "ID 1 no debe emitir colilla (redirección esperada)"
    print("[OK] Bloqueo de colilla para Elvin Alexander: FUNCIONA AL 100%")

    # 7. Probar Submódulo de Contratos Laborales (/admin/contratos)
    resp_cont = client.get('/admin/contratos')
    assert resp_cont.status_code == 200
    html_cont = resp_cont.data.decode('utf-8')
    assert 'Elvin Alexander' not in html_cont, "Elvin no debe figurar en el directorio de contratos laborales"
    assert 'CTR-TCR-2026-002' in html_cont
    print("[OK] Submódulo de Contratos Laborales (Elvin excluido): FUNCIONA AL 100%")

    # 8. Probar Ver Contrato Formal
    resp_ver = client.get('/admin/contratos/ver/2')
    assert resp_ver.status_code == 200
    html_ver = resp_ver.data.decode('utf-8')
    assert 'CLÁUSULA PRIMERA' in html_ver
    assert 'J0310000123456' in html_ver
    print("[OK] Vista de Contrato Formal Ley 185: FUNCIONA AL 100%")

    # 9. Probar Imprimir Contrato Formal
    resp_imp = client.get('/admin/contratos/imprimir/2')
    assert resp_imp.status_code == 200
    html_imp = resp_imp.data.decode('utf-8')
    assert 'REPÚBLICA DE NICARAGUA' in html_imp
    # Limpieza final
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM NovedadesNomina WHERE UsuarioID = 4 AND Mes = 10 AND Anio = 2026")
    conn.commit()
    conn.close()

    print("\n>>> ¡TODOS LOS TESTS DE RECURSOS HUMANOS, PLANILLA MIPYME Y ESTADOS FINANCIEROS PASARON CON ÉXITO TOTAL! <<<")

if __name__ == '__main__':
    test_rrhh_completo()
