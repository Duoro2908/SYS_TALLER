import os
import re
import datetime
from config import Config

_SCHEMA_MIGRATED = False

# Intento de importar pyodbc si está en Windows
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False


class SQLiteRow:
    def __init__(self, desc, values):
        self._values = tuple(values) if values is not None else ()
        self._mapping = {}
        self._fields = []
        if desc:
            for idx, col in enumerate(desc):
                name = col[0]
                self._fields.append(name)
                self._mapping[name] = idx
                self._mapping[name.lower()] = idx

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._values[item]
        if isinstance(item, str):
            idx = self._mapping.get(item)
            if idx is None:
                idx = self._mapping.get(item.lower())
            if idx is not None:
                return self._values[idx]
        raise KeyError(item)

    def __getattr__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)
        idx = self._mapping.get(name)
        if idx is None:
            idx = self._mapping.get(name.lower())
        if idx is not None:
            return self._values[idx]
        raise AttributeError(f"Row has no attribute '{name}'")

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __repr__(self):
        return repr(self._values)

    def keys(self):
        return self._fields

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cur = cursor

    @property
    def description(self):
        return self._cur.description

    @property
    def rowcount(self):
        return self._cur.rowcount

    def _transform_query(self, query):
        if not isinstance(query, str):
            return query
        q = query
        # Reemplazar TOP N
        top_match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', q, re.IGNORECASE)
        if top_match:
            limit_val = top_match.group(1)
            q = re.sub(r'\bSELECT\s+TOP\s+\d+\b', 'SELECT', q, count=1, flags=re.IGNORECASE)
            q = f"{q.rstrip(';')} LIMIT {limit_val}"

        # Reemplazar OUTPUT INSERTED.Columna -> RETURNING Columna
        output_match = re.search(r'\bOUTPUT\s+INSERTED\.(\w+)\b', q, re.IGNORECASE)
        if output_match:
            col_name = output_match.group(1)
            q = re.sub(r'\bOUTPUT\s+INSERTED\.\w+\b', '', q, flags=re.IGNORECASE)
            q = f"{q.rstrip(';')} RETURNING {col_name}"

        return q

    def execute(self, query, params=None):
        transformed = self._transform_query(query)
        try:
            if params is not None:
                if isinstance(params, (list, tuple)):
                    return self._cur.execute(transformed, params)
                else:
                    return self._cur.execute(transformed, (params,))
            return self._cur.execute(transformed)
        except Exception as e:
            return self._cur.execute(query, params or ())

    def executemany(self, query, seq_of_params):
        transformed = self._transform_query(query)
        return self._cur.executemany(transformed, seq_of_params)

    def _wrap(self, row):
        if row is None:
            return None
        return SQLiteRow(self._cur.description, row)

    def fetchone(self):
        r = self._cur.fetchone()
        return self._wrap(r)

    def fetchall(self):
        rows = self._cur.fetchall()
        return [self._wrap(r) for r in rows]

    def fetchmany(self, size=None):
        rows = self._cur.fetchmany(size) if size else self._cur.fetchmany()
        return [self._wrap(r) for r in rows]

    def __iter__(self):
        for r in self._cur:
            yield self._wrap(r)

    def close(self):
        return self._cur.close()


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


def get_sqlite_connection():
    import sqlite3
    db_file = os.path.join(os.path.dirname(__file__), "taller.db")
    if not os.path.exists(db_file):
        return None
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.create_function("GETDATE", 0, lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    conn.create_function("ISNULL", 2, lambda a, b: b if a is None else a)
    conn.create_function("YEAR", 1, lambda d: int(str(d)[:4]) if d else None)
    conn.create_function("MONTH", 1, lambda d: int(str(d)[5:7]) if d else None)
    conn.create_function("DAY", 1, lambda d: int(str(d)[8:10]) if d else None)
    return SQLiteConnectionWrapper(conn)


def get_db_connection():
    """
    Establece conexión con SQL Server si está disponible (Windows local),
    o utiliza SQLite (taller.db) cuando está en Render / Nube.
    """
    global _SCHEMA_MIGRATED
    
    # 1. Si está en Render o Linux, usar SQLite directamente
    if os.environ.get("RENDER") or not HAS_PYODBC:
        return get_sqlite_connection()

    # 2. Intentar SQL Server
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        if not _SCHEMA_MIGRATED:
            ensure_schema_migrations(conn=conn)
        return conn
    except Exception:
        # Fallback a SQLite local si SQL Server no responde
        return get_sqlite_connection()


def ensure_schema_migrations(force=False, conn=None):
    """Aplica migraciones idempotentes de esquema necesarias."""
    global _SCHEMA_MIGRATED
    if _SCHEMA_MIGRATED and not force:
        return True

    should_close = False
    if conn is None:
        if not HAS_PYODBC:
            return True
        try:
            conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
            should_close = True
        except Exception:
            return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CHK_Moto_Marca')
            BEGIN
                ALTER TABLE Motocicletas DROP CONSTRAINT CHK_Moto_Marca;
            END
        """)
        cursor.execute("""
            IF COL_LENGTH('CitasWhatsApp', 'Notas') IS NULL
            BEGIN
                ALTER TABLE CitasWhatsApp ADD Notas NVARCHAR(MAX) NULL;
            END
        """)
        cursor.execute("""
            IF COL_LENGTH('CitasWhatsApp', 'Origen') IS NULL
            BEGIN
                ALTER TABLE CitasWhatsApp ADD Origen NVARCHAR(50) DEFAULT 'WhatsApp';
            END
        """)
        conn.commit()
        _SCHEMA_MIGRATED = True
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()
