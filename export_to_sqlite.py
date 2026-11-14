import pyodbc
import sqlite3
import os
from config import Config

def export_db():
    print("Iniciando exportación de SQL Server a SQLite...")
    conn_sql = pyodbc.connect(Config.DB_CONNECTION_STRING)
    cur_sql = conn_sql.cursor()

    db_path = "taller.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    conn_sq3 = sqlite3.connect(db_path)
    cur_sq3 = conn_sq3.cursor()

    cur_sql.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME != 'sysdiagrams'")
    tables = [r[0] for r in cur_sql.fetchall()]

    for table in tables:
        cur_sql.execute(f"SELECT * FROM [{table}]")
        cols = [col[0] for col in cur_sql.description]
        rows = cur_sql.fetchall()
        
        col_defs = ", ".join([f"[{c}] TEXT" for c in cols])
        cur_sq3.execute(f"CREATE TABLE IF NOT EXISTS [{table}] ({col_defs})")
        
        if rows:
            placeholders = ", ".join(["?" for _ in cols])
            cleaned_rows = []
            for r in rows:
                cleaned_rows.append([str(v) if v is not None else None for v in r])
            cur_sq3.executemany(f"INSERT INTO [{table}] VALUES ({placeholders})", cleaned_rows)
        print(f"  -> Exportada tabla: {table} ({len(rows)} filas)")

    conn_sq3.commit()
    conn_sq3.close()
    conn_sql.close()
    print(f"¡Éxito! Base de datos SQLite creada en '{db_path}' con {len(tables)} tablas.")

if __name__ == "__main__":
    export_db()

