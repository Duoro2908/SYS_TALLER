import os

files_to_remove = [
    'scratch/search_items.py',
    'scratch/search_all.py',
    'scratch/check_dashboards.py',
    'scratch/patch_auth.py',
    'scratch/find_modal_prod.py',
    'scratch/find_img_tags.py',
    'scratch/check_products_db.py',
    'scratch/find_inserts_prod.py',
    'scratch/patch_modals.py',
    'scratch/patch_base_alert.py',
]

for f in files_to_remove:
    if os.path.exists(f):
        try:
            os.remove(f)
            print("Removed:", f)
        except Exception as e:
            print("Error removing", f, e)
