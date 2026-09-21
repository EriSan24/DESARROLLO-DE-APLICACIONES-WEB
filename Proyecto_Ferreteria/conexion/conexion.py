import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

try:
    import mysql.connector
except ImportError:  # pragma: no cover - optional dependency
    mysql = None

try:
    import psycopg2
except ImportError:  # pragma: no cover - optional dependency
    psycopg2 = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "ferreteria.db"
SCHEMA_PATH = BASE_DIR / "sql" / "esquema.sql"

PRODUCTOS_INICIALES = [
    {"codigo": "P001", "nombre": "Martillo", "categoria": "Herramientas", "precio": 12.50, "stock": 25, "id_proveedor": 1},
    {"codigo": "P003", "nombre": "Taladro", "categoria": "Eléctricas", "precio": 85.00, "stock": 5, "id_proveedor": 3},
    {"codigo": "P004", "nombre": "Sierra", "categoria": "Herramientas", "precio": 45.00, "stock": 0, "id_proveedor": 1},
    {"codigo": "P005", "nombre": "Moladora", "categoria": "Herramientas", "precio": 120.00, "stock": 8, "id_proveedor": 1},
    {"codigo": "P006", "nombre": "Metro", "categoria": "Medición", "precio": 18.50, "stock": 30, "id_proveedor": 2},
    {"codigo": "P007", "nombre": "Mangueras", "categoria": "Fontanería", "precio": 15.00, "stock": 40, "id_proveedor": 2},
    {"codigo": "P008", "nombre": "Hierro", "categoria": "Construcción", "precio": 22.00, "stock": 60, "id_proveedor": 3},
    {"codigo": "P009", "nombre": "Barrillas", "categoria": "Construcción", "precio": 30.50, "stock": 35, "id_proveedor": 3},
    {"codigo": "P010", "nombre": "Llave inglesa", "categoria": "Herramientas", "precio": 28.00, "stock": 12, "id_proveedor": 1},
    {"codigo": "P011", "nombre": "Taladro inalámbrico", "categoria": "Eléctricas", "precio": 95.00, "stock": 7, "id_proveedor": 3},
]

PROVEEDORES_INICIALES = [
    {"id_proveedor": 1, "nombre": "FerreMax S.A.", "telefono": "0991111111", "correo": "ventas@ferremax.com"},
    {"id_proveedor": 2, "nombre": "Distribuidora Norte", "telefono": "0982222222", "correo": "info@distribuidoranorte.com"},
    {"id_proveedor": 3, "nombre": "Herramientas del Sur", "telefono": "0973333333", "correo": "contacto@herramientassur.com"},
]

USUARIO_DEMO = {"usuario": "Ericksanchez", "password": "Erick2000"}


def _split_sql_statements(sql_script):
    statements = []
    current = []
    for line in sql_script.split(";"):
        stripped = line.strip()
        if stripped:
            current.append(stripped)
            if stripped.endswith(";"):
                statements.append("; ".join(current).strip())
                current = []
    if current:
        statements.append("; ".join(current).strip())
    return [statement for statement in statements if statement]


def _parameterized_sql(query, params):
    engine = os.getenv("DB_ENGINE", "sqlite").lower()
    if engine in {"sqlite", "sqlite3"}:
        return query.replace("%s", "?"), tuple(params)
    return query, tuple(params)


def _sqlite_connection():
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _mysql_connection():
    if mysql is None:
        raise RuntimeError("mysql-connector-python no está instalado.")
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "ferreteria_db"),
        "autocommit": False,
    }
    return mysql.connector.connect(**config)


def _postgres_connection():
    if psycopg2 is None:
        raise RuntimeError("psycopg2-binary no está instalado.")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        dbname=os.getenv("DB_NAME", "ferreteria_db"),
    )
    conn.autocommit = False
    return conn


def get_db_connection():
    engine = os.getenv("DB_ENGINE", "sqlite").lower()
    if engine in {"sqlite", "sqlite3"}:
        return _sqlite_connection()
    if engine in {"mysql", "mariadb"}:
        return _mysql_connection()
    if engine in {"postgres", "postgresql"}:
        return _postgres_connection()
    return _sqlite_connection()


def _ensure_sqlite_product_supplier_column(conn):
    columns = conn.execute("PRAGMA table_info(productos)").fetchall()
    has_supplier_column = any(column[1] == "id_proveedor" for column in columns)
    if not has_supplier_column:
        conn.execute("ALTER TABLE productos ADD COLUMN id_proveedor INTEGER")
        conn.execute("UPDATE productos SET id_proveedor = 1 WHERE id_proveedor IS NULL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_productos_id_proveedor ON productos(id_proveedor)")


def _initialize_sqlite_database(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS proveedores (
            id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT,
            correo TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            id_proveedor INTEGER,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
        )
        """
    )
    _ensure_sqlite_product_supplier_column(conn)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
        """
    )

    for proveedor in PROVEEDORES_INICIALES:
        conn.execute(
            """
            INSERT OR IGNORE INTO proveedores (id_proveedor, nombre, telefono, correo)
            VALUES (?, ?, ?, ?)
            """,
            (
                proveedor["id_proveedor"],
                proveedor["nombre"],
                proveedor["telefono"],
                proveedor["correo"],
            ),
        )

    product_codes = tuple(producto["codigo"] for producto in PRODUCTOS_INICIALES)
    placeholders = ", ".join("?" for _ in product_codes)
    conn.execute(f"DELETE FROM productos WHERE codigo NOT IN ({placeholders})", product_codes)

    for producto in PRODUCTOS_INICIALES:
        conn.execute(
            """
            INSERT OR IGNORE INTO productos (codigo, nombre, categoria, precio, stock, id_proveedor)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                producto["codigo"],
                producto["nombre"],
                producto["categoria"],
                producto["precio"],
                producto["stock"],
                producto["id_proveedor"],
            ),
        )

    conn.execute(
        "INSERT OR IGNORE INTO usuarios (usuario, password) VALUES (?, ?)",
        (USUARIO_DEMO["usuario"], generate_password_hash(USUARIO_DEMO["password"])),
    )

    conn.commit()


def _initialize_relational_database(conn):
    if not SCHEMA_PATH.exists():
        return
    sql_script = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = _split_sql_statements(sql_script)
    cursor = conn.cursor()
    for statement in statements:
        cursor.execute(statement)
    conn.commit()


def initialize_database():
    conn = None
    try:
        conn = get_db_connection()
        engine = os.getenv("DB_ENGINE", "sqlite").lower()
        if engine in {"sqlite", "sqlite3"}:
            _initialize_sqlite_database(conn)
        else:
            _initialize_relational_database(conn)
    except (sqlite3.Error, OSError):
        if conn is not None:
            conn.close()
        if DATABASE_PATH.exists():
            try:
                DATABASE_PATH.unlink()
            except OSError:
                pass
        conn = _sqlite_connection()
        _initialize_sqlite_database(conn)
    finally:
        if conn:
            conn.close()


def get_user_by_username(usuario):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, usuario, password FROM usuarios WHERE usuario = %s"
        cursor.execute(*_parameterized_sql(query, (usuario,)))
        row = cursor.fetchone()
        if row is None:
            return None
        if hasattr(row, "keys"):
            return dict(row)
        return {"id": row[0], "usuario": row[1], "password": row[2]}
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, usuario, password FROM usuarios WHERE id = %s"
        cursor.execute(*_parameterized_sql(query, (user_id,)))
        row = cursor.fetchone()
        if row is None:
            return None
        if hasattr(row, "keys"):
            return dict(row)
        return {"id": row[0], "usuario": row[1], "password": row[2]}
    finally:
        conn.close()


def create_user(usuario, password_hash):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)"
        cursor.execute(*_parameterized_sql(query, (usuario, password_hash)))
        conn.commit()
        return True
    except (sqlite3.Error, OSError):
        conn.rollback()
        return False
    finally:
        conn.close()


def _normalize_product_row(row):
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    return {
        "codigo": row[0],
        "nombre": row[1],
        "categoria": row[2],
        "precio": float(row[3]),
        "stock": int(row[4]),
        "id_proveedor": row[5],
        "proveedor": row[6] if len(row) > 6 else None,
    }


def get_products():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.codigo, p.nombre, p.categoria, p.precio, p.stock, p.id_proveedor, pr.nombre AS proveedor
            FROM productos p
            LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
            ORDER BY p.codigo
        """
        cursor.execute(*_parameterized_sql(query, ()))
        rows = cursor.fetchall()
        return [_normalize_product_row(row) for row in rows]
    finally:
        conn.close()


def get_product_by_code(codigo):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.codigo, p.nombre, p.categoria, p.precio, p.stock, p.id_proveedor, pr.nombre AS proveedor
            FROM productos p
            LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
            WHERE p.codigo = %s
            """
        cursor.execute(*_parameterized_sql(query, (codigo,)))
        row = cursor.fetchone()
        return _normalize_product_row(row)
    finally:
        conn.close()


def insert_product(producto):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO productos (codigo, nombre, categoria, precio, stock, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        params = (
            producto["codigo"],
            producto["nombre"],
            producto["categoria"],
            float(producto["precio"]),
            int(producto["stock"]),
            producto.get("id_proveedor"),
        )
        cursor.execute(*_parameterized_sql(query, params))
        conn.commit()
        return True
    except (sqlite3.Error, OSError):
        conn.rollback()
        return False
    finally:
        conn.close()


def update_product(codigo_actual, codigo_nuevo, nombre, categoria, precio, stock):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE productos
            SET codigo = %s, nombre = %s, categoria = %s, precio = %s, stock = %s
            WHERE codigo = %s
            """
        params = (codigo_nuevo, nombre, categoria, float(precio), int(stock), codigo_actual)
        cursor.execute(*_parameterized_sql(query, params))
        conn.commit()
        return cursor.rowcount > 0
    except (sqlite3.Error, OSError):
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_product(codigo):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM productos WHERE codigo = %s"
        cursor.execute(*_parameterized_sql(query, (codigo,)))
        conn.commit()
        return cursor.rowcount > 0
    except (sqlite3.Error, OSError):
        conn.rollback()
        return False
    finally:
        conn.close()
