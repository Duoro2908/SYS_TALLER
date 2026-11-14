import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        t.name AS TriggerName,
        tb.name AS TableName,
        t.is_disabled
    FROM sys.triggers t
    INNER JOIN sys.tables tb ON t.parent_id = tb.object_id
    ORDER BY tb.name, t.name
""")
for r in cursor.fetchall():
    print(r)
conn.close()

