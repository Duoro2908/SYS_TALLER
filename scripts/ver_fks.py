import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        fk.name AS FK_name,
        tp.name AS ParentTable,
        tr.name AS ReferencedTable
    FROM sys.foreign_keys fk
    INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
    ORDER BY tr.name, tp.name
""")
for r in cursor.fetchall():
    print(f"{r[1]} -> {r[2]} ({r[0]})")
conn.close()

