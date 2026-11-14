import os

files = [
    'scratch/patch_auth_log.py',
    'scratch/find_wa_login.py',
    'scratch/apply_wa_fix.py',
    'scratch/find_sidebar_css.py',
    'scratch/test_dt_fix.py',
    'scratch/test_schema.py',
    'scratch/test_wa_chat.py',
    'scratch/cleanup_test_cita.py',
    'scratch/patch_sidebar_scroll.py'
]

for f in files:
    if os.path.exists(f):
        try:
            os.remove(f)
            print("Removed:", f)
        except Exception as e:
            print("Error:", e)

