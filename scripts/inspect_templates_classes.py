import os
import re

files_to_check = [
    'templates/admin/empleados_rrhh.html',
    'templates/admin/planilla.html',
    'templates/admin/contratos.html',
    'templates/admin/contrato_detalle.html',
    'templates/admin/registro_mensual.html',
    'templates/bodega/inventario.html',
    'templates/bodega/compras.html',
    'templates/bodega/historial.html',
]

for fp in files_to_check:
    print('==============================')
    print('FILE:', fp)
    if not os.path.exists(fp):
        print('NOT FOUND')
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # check if <style> tag exists
    style_matches = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)
    print(f'Has <style> blocks: {len(style_matches)}')
    for idx, sm in enumerate(style_matches):
        print(f'-- Style Block {idx+1} (length {len(sm)}):')
        # print first 500 chars and find class definitions
        classes = re.findall(r'\.([a-zA-Z0-9_\-]+)\s*\{', sm)
        print('Classes defined:', sorted(list(set(classes))))

