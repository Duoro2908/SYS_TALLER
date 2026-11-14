import pyodbc
import sqlite3
import os
from decimal import Decimal
from datetime import datetime, date
from config import Config

def export_db():
    print("Iniciando exportación precisa de SQL Server a SQLite...")
    conn_sql = pyodbc.connect(Config.DB_CONNECTION_STRING)
    cur_sql = conn_sql.cursor()

    db_path = "taller.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception as e:
            print("No se pudo borrar db anterior:", e)

    conn_sq3 = sqlite3.connect(db_path)
    cur_sq3 = conn_sq3.cursor()

    cur_sql.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME != 'sysdiagrams'")
    tables = [r[0] for r in cur_sql.fetchall()]

    for table in tables:
        # Obtener columnas y tipos de datos de SQL Server
        cur_sql.execute("""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table,))
        col_info = cur_sql.fetchall()
        
        col_defs = []
        col_names = []
        col_types = {}
        for col_name, data_type in col_info:
            col_names.append(col_name)
            dt = data_type.lower()
            if dt in ('bit', 'int', 'bigint', 'smallint', 'tinyint'):
                sqlite_type = 'INTEGER'
            elif dt in ('decimal', 'numeric', 'money', 'smallmoney', 'float', 'real'):
                sqlite_type = 'REAL'
            else:
                sqlite_type = 'TEXT'
            col_types[col_name] = sqlite_type
            col_defs.append(f"[{col_name}] {sqlite_type}")

        # Crear tabla con tipos correctos
        cur_sq3.execute(f"CREATE TABLE IF NOT EXISTS [{table}] ({', '.join(col_defs)})")

        # Leer datos de SQL Server
        cur_sql.execute(f"SELECT * FROM [{table}]")
        rows = cur_sql.fetchall()

        if rows:
            placeholders = ", ".join(["?" for _ in col_names])
            cleaned_rows = []
            for r in rows:
                cleaned_row = []
                for val, col_name in zip(r, col_names):
                    st = col_types[col_name]
                    if val is None:
                        cleaned_row.append(None)
                    elif st == 'INTEGER':
                        if isinstance(val, bool):
                            cleaned_row.append(1 if val else 0)
                        else:
                            try:
                                cleaned_row.append(int(val))
                            except Exception:
                                cleaned_row.append(1 if str(val).lower() in ('true', '1') else 0)
                    elif st == 'REAL':
                        try:
                            cleaned_row.append(float(val))
                        except Exception:
                            cleaned_row.append(0.0)
                    else:
                        cleaned_row.append(str(val))
                cleaned_rows.append(cleaned_row)

            cur_sq3.executemany(f"INSERT INTO [{table}] VALUES ({placeholders})", cleaned_rows)
        print(f"  -> Exportada tabla {table}: {len(rows)} filas con tipos nativos.")

    conn_sq3.commit()
    conn_sq3.close()
    conn_sql.close()
    print("¡Exportación completada exitosamente!")

if __name__ == '__main__':
    export_db()
