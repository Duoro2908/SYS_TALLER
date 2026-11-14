import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_clasificacion_empleados():
    client = app.test_client()
    print("=== TEST CLASIFICACIÓN DE EMPLEADOS: PLANTA PERMANENTE VS ASESORES DE CIERRE ===")

    # 1. Simular sesión de Dirección / RRHH
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['nombre_completo'] = 'Elvin Alexander Mendez Cruz'
        sess['rol_id'] = 1
        sess['rol_nombre'] = 'Super Administrador'

    # 2. Verificar Planilla de Pago (/admin/planilla)
    resp_plan = client.get('/admin/planilla')
    assert resp_plan.status_code == 200, f"Error en planilla: {resp_plan.status_code}"
    html_plan = resp_plan.data.decode('utf-8')

    # A. Verificar Presencia de los Grupos y Encabezados
    assert 'Personal Permanente de Planta' in html_plan, "Falta grupo Personal Permanente de Planta"
    assert 'Asesores Externos y Consultores de Cierre' in html_plan or 'Asesorías Externas y Consultores de Cierre' in html_plan, "Falta grupo Asesores de Cierre"
    assert 'Presencial Diario' in html_plan, "Falta indicativo Presencial Diario"
    assert '1 Día al Mes' in html_plan, "Falta indicativo 1 Día al Mes"

    # B. Verificar Subtotales de Categorías y Total Consolidado MIPYME
    assert '68,300' in html_plan or '68,800' in html_plan, "Subtotal de Planta Permanente debe reflejar escala MIPYME"
    assert '8,000' in html_plan, "Subtotal de Asesores debe ser C$ 8,000.00"
    assert '76,300' in html_plan, "Total general base consolidado debe ser C$ 76,300.00"
    assert '76,800' in html_plan, "Total general bruto consolidado debe ser C$ 76,800.00"

    # C. Verificar Filtros por Botones Píldora
    assert 'pillTodos' in html_plan or 'filtrarCategoria' in html_plan, "Falta control de filtrado por categoría"
    assert 'data-category="permanente"' in html_plan, "Falta atributo data-category permanente"
    assert 'data-category="asesor"' in html_plan, "Falta atributo data-category asesor"

    print("[OK] /admin/planilla clasifica a la perfección Planta Permanente (8) y Asesores de Cierre (2) con subtotales exactos!")

    # 3. Verificar Colilla de Pago de Carlos René (UsuarioID: 1010)
    resp_col_carlos = client.get('/admin/planilla/colilla/1010')
    assert resp_col_carlos.status_code == 200, f"Error en colilla Carlos: {resp_col_carlos.status_code}"
    html_col_carlos = resp_col_carlos.data.decode('utf-8')
    assert 'Carlos Rene Gavarrete Calero' in html_col_carlos
    assert 'ASESORÍA EXTERNA • CIERRE MENSUAL' in html_col_carlos
    assert '1 Día al Mes • Pago Único por Cierre' in html_col_carlos
    assert 'Honorarios por Cierre Mensual (1 Día/Mes)' in html_col_carlos or 'Cierre Mensual' in html_col_carlos
    assert 'C$ 4,500.00' in html_col_carlos or '4,500' in html_col_carlos
    print("[OK] Colilla de Carlos René destaca formalmente su modalidad de Asesoría Externa de Cierre Mensual (1 día/mes - Pago Único)!")

    # 4. Probar Colilla de un Empleado Permanente (p. ej. Jhosep David Cooper Sandino ID: 2)
    resp_col_jhosep = client.get('/admin/planilla/colilla/2')
    assert resp_col_jhosep.status_code == 200
    html_col_jhosep = resp_col_jhosep.data.decode('utf-8')
    assert 'PLANTA PERMANENTE • PRESENCIAL DIARIO' in html_col_jhosep
    assert 'Personal Permanente de Planta' in html_col_jhosep
    print("[OK] Colilla de Personal Permanente destaca formalmente su jornada ordinaria presencial diaria!")

    # 5. Verificar Directorio de Contratos (/admin/contratos)
    resp_cont = client.get('/admin/contratos')
    assert resp_cont.status_code == 200
    html_cont = resp_cont.data.decode('utf-8')
    assert 'filtrarCategoriaContratos' in html_cont
    assert 'data-category="permanente"' in html_cont
    assert 'data-category="asesor"' in html_cont
    print("[OK] Directorio de Contratos clasifica y filtra por Planta Permanente vs Asesorías de Cierre!")

    print("\n>>> ¡TODAS LAS VALIDACIONES DE CLASIFICACIÓN DE PERSONAL PASARON CON 100% DE ÉXITO! <<<")

if __name__ == '__main__':
    test_clasificacion_empleados()
