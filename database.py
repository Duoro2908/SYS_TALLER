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


class SmartStr(str):
    def _parse(self):
        s = str(self).strip()
        for f in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S', '%H:%M'):
            try:
                return datetime.datetime.strptime(s, f)
            except ValueError:
                pass
        try:
            return datetime.datetime.fromisoformat(s)
        except Exception:
            return None

    def strftime(self, fmt):
        dt = self._parse()
        if dt:
            return dt.strftime(fmt)
        return str(self)

    @property
    def year(self):
        dt = self._parse()
        return dt.year if dt else None

    @property
    def month(self):
        dt = self._parse()
        return dt.month if dt else None

    @property
    def day(self):
        dt = self._parse()
        return dt.day if dt else None


def _wrap_val(v):
    if v is None:
        return None
    if isinstance(v, str):
        return SmartStr(v)
    return v


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
            if isinstance(item, slice):
                return tuple(_wrap_val(x) for x in self._values[item])
            return _wrap_val(self._values[item])
        if isinstance(item, str):
            idx = self._mapping.get(item)
            if idx is None:
                idx = self._mapping.get(item.lower())
            if idx is not None:
                return _wrap_val(self._values[idx])
        raise KeyError(item)

    def __getattr__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)
        idx = self._mapping.get(name)
        if idx is None:
            idx = self._mapping.get(name.lower())
        if idx is not None:
            return _wrap_val(self._values[idx])
        raise AttributeError(f"Row has no attribute '{name}'")

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        for v in self._values:
            yield _wrap_val(v)

    def __repr__(self):
        return repr(self._values)

    def keys(self):
        return self._fields

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default


class StringAgg:
    def __init__(self):
        self.parts = []
        self.sep = ", "
    def step(self, val, sep=", "):
        if val is not None:
            self.parts.append(str(val))
            self.sep = sep
    def finalize(self):
        return self.sep.join(self.parts)


def transform_query_sqlite(query):
    if not isinstance(query, str):
        return query
    q = query

    # 1. ISNULL -> COALESCE
    q = re.sub(r'\bISNULL\s*\(', 'COALESCE(', q, flags=re.IGNORECASE)

    # 2. GETDATE() con o sin offset
    q = re.sub(r'\bGETDATE\(\)\s*-\s*(\d+)', r"DATETIME('now', '-\1 day')", q, flags=re.IGNORECASE)
    q = re.sub(r'\bGETDATE\(\)', r"DATETIME('now')", q, flags=re.IGNORECASE)

    # 3. CAST(expr AS DATE) -> DATE(expr)
    q = re.sub(r'\bCAST\s*\(\s*(.*?)\s+AS\s+DATE\s*\)', r'DATE(\1)', q, flags=re.IGNORECASE)

    # 4. CONVERT de tipos comunes de SQL Server
    q = re.sub(r'\bCONVERT\s*\(\s*VARCHAR\(16\)\s*,\s*(.*?)\s*,\s*120\s*\)', r'SUBSTR(\1, 1, 16)', q, flags=re.IGNORECASE)
    q = re.sub(r'\bCONVERT\s*\(\s*[N]?VARCHAR\s*\(\s*MAX\s*\)\s*,\s*(.*?)\s*\)', r'CAST(\1 AS TEXT)', q, flags=re.IGNORECASE)
    q = re.sub(r'\bCONVERT\s*\(\s*[N]?VARCHAR(?:\([^)]*\))?\s*,\s*(.*?)(?:,\s*\d+)?\s*\)', r'CAST(\1 AS TEXT)', q, flags=re.IGNORECASE)

    # 5. Quote datepart en DATENAME y DATEADD
    q = re.sub(r'\bDATENAME\s*\(\s*month\s*,', "DATENAME('month',", q, flags=re.IGNORECASE)
    q = re.sub(r'\bDATEADD\s*\(\s*month\s*,', "DATEADD('month',", q, flags=re.IGNORECASE)
    q = re.sub(r'\bDATEADD\s*\(\s*day\s*,', "DATEADD('day',", q, flags=re.IGNORECASE)
    q = re.sub(r'\bDATEADD\s*\(\s*year\s*,', "DATEADD('year',", q, flags=re.IGNORECASE)

    # 6. Handle SELECT TOP N (both in subqueries and top-level)
    while True:
        match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', q, re.IGNORECASE)
        if not match:
            break
        limit_val = match.group(1)
        depth = 0
        end_idx = len(q)
        
        for i in range(match.end(), len(q)):
            if q[i] == '(':
                depth += 1
            elif q[i] == ')':
                if depth == 0:
                    end_idx = i
                    break
                else:
                    depth -= 1
            elif q[i] == ';' and depth == 0:
                end_idx = i
                break

        before = q[:match.start()] + "SELECT "
        middle = q[match.end():end_idx]
        after = q[end_idx:]
        q = f"{before}{middle} LIMIT {limit_val} {after}"

    # 7. OUTPUT INSERTED.Columna -> RETURNING Columna
    q = re.sub(r'\bOUTPUT\s+INSERTED\.(\w+)\b', r'RETURNING \1', q, flags=re.IGNORECASE)

    # 8. Eliminar comandos exclusivos de SQL Server
    q = re.sub(r'\bSET\s+NOCOUNT\s+ON\s*;?', '', q, flags=re.IGNORECASE)
    q = re.sub(r'\bSELECT\s+SCOPE_IDENTITY\(\)\s*;?', '', q, flags=re.IGNORECASE)

    return q


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
        return transform_query_sqlite(query)

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
    conn.create_aggregate("STRING_AGG", 2, StringAgg)
    conn.create_function("CONCAT", -1, lambda *args: "".join(str(a) if a is not None else "" for a in args))
    conn.create_function("LEFT", 2, lambda s, n: str(s)[:int(n)] if s else "")
    conn.create_function("DATENAME", 2, lambda part, d: (['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'][int(str(d)[5:7])] if d and len(str(d)) >= 7 else ""))
    conn.create_function("DATEADD", 3, lambda part, n, d: (datetime.datetime.strptime(str(d)[:10], '%Y-%m-%d') + datetime.timedelta(days=int(n)*30)).strftime('%Y-%m-%d') if d else "")
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
