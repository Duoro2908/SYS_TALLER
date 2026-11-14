with open('templates/dashboard/superadmin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'Auto-Sync' in l or 'autosync' in l or 'autoSync' in l or 'EN VIVO' in l or 'Actualizar' in l:
        print(f"{i+1}: {l.strip()}")

