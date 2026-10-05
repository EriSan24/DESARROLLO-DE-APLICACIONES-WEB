import os
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlsplit

from werkzeug.security import generate_password_hash

try:
    import psycopg2  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    psycopg2 = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "ferreteria.db"

PRODUCTOS_INICIALES = [
    {"codigo": "R001", "nombre": "Camiseta Essential", "categoria": "Camisetas", "marca": "Nike", "talla": "M", "color": "Negro", "genero": "Unisex", "precio": 29.90, "stock": 25, "id_proveedor": 1},
    {"codigo": "R002", "nombre": "Jeans 501 Original", "categoria": "Pantalones", "marca": "Levi's", "talla": "32", "color": "Azul índigo", "genero": "Hombre", "precio": 89.90, "stock": 12, "id_proveedor": 2},
    {"codigo": "R003", "nombre": "Sudadera Classic", "categoria": "Sudaderas", "marca": "Adidas", "talla": "L", "color": "Gris", "genero": "Unisex", "precio": 64.90, "stock": 8, "id_proveedor": 1},
    {"codigo": "R004", "nombre": "Chaqueta Trucker", "categoria": "Chaquetas", "marca": "Levi's", "talla": "M", "color": "Azul", "genero": "Mujer", "precio": 119.90, "stock": 5, "id_proveedor": 2},
    {"codigo": "R005", "nombre": "Zapatillas Air Max", "categoria": "Calzado", "marca": "Nike", "talla": "40", "color": "Blanco", "genero": "Unisex", "precio": 139.90, "stock": 9, "id_proveedor": 3},
    {"codigo": "R006", "nombre": "Polo Slim Fit", "categoria": "Polos", "marca": "Lacoste", "talla": "S", "color": "Verde", "genero": "Hombre", "precio": 74.90, "stock": 14, "id_proveedor": 3},
    {"codigo": "R007", "nombre": "Vestido Midi", "categoria": "Vestidos", "marca": "Zara", "talla": "M", "color": "Negro", "genero": "Mujer", "precio": 59.90, "stock": 11, "id_proveedor": 2},
    {"codigo": "R008", "nombre": "Leggings Training", "categoria": "Deportivo", "marca": "Adidas", "talla": "S", "color": "Negro", "genero": "Mujer", "precio": 39.90, "stock": 18, "id_proveedor": 1},
    {"codigo": "R009", "nombre": "Camisa Oxford", "categoria": "Camisas", "marca": "Tommy Hilfiger", "talla": "L", "color": "Celeste", "genero": "Hombre", "precio": 79.90, "stock": 7, "id_proveedor": 3},
    {"codigo": "R010", "nombre": "Gorra Heritage", "categoria": "Accesorios", "marca": "New Era", "talla": "Única", "color": "Rojo", "genero": "Unisex", "precio": 34.90, "stock": 20, "id_proveedor": 1},
]

PROVEEDORES_INICIALES = [
    {"id_proveedor": 1, "nombre": "Urban Brands Ecuador", "contacto": "Luis Torres", "telefono": "0991111111", "correo": "ventas@urbanbrands.ec"},
    {"id_proveedor": 2, "nombre": "Denim House", "contacto": "Ana Morales", "telefono": "0982222222", "correo": "pedidos@denimhouse.ec"},
    {"id_proveedor": 3, "nombre": "Sportline Distribuciones", "contacto": "Pedro Gómez", "telefono": "0973333333", "correo": "ventas@sportline.ec"},
]

CLIENTES_INICIALES = [
    {"id_cliente": 1, "nombre": "Erick Sánchez", "cedula": "2100000001", "telefono": "0999999999", "correo": "erick.sanchez@gmail.com"},
    {"id_cliente": 2, "nombre": "Estefanía Ramón", "cedula": "2100000002", "telefono": "0988888888", "correo": "estefania.ramon@gmail.com"},
    {"id_cliente": 3, "nombre": "Roberto Mena", "cedula": "2100000003", "telefono": "0977777777", "correo": "roberto.mena@gmail.com"},
]

PRODUCTOS_ANTIGUOS = (
    ("P001", "Martillo"), ("P003", "Taladro"), ("P004", "Sierra"),
    ("P005", "Moladora"), ("P006", "Metro"), ("P007", "Mangueras"),
    ("P008", "Hierro"), ("P009", "Barrillas"), ("P010", "Llave inglesa"),
    ("P011", "Taladro inalámbrico"),
)

USUARIO_DEMO = {"usuario": "Ericksanchez", "password": "Erick2000"}


def _database_engine():
    configured_engine = os.getenv("DB_ENGINE")
    if configured_engine:
        return configured_engine.lower()
    return "postgresql" if os.getenv("DATABASE_URL") else "sqlite"


def _database_errors():
    errors = [sqlite3.Error, OSError]
    if psycopg2 is not None:
        errors.append(psycopg2.Error)
    return tuple(errors)


def _parameterized_sql(query, params):
    engine = _database_engine()
    if engine in {"sqlite", "sqlite3"}:
        sqlite_params = tuple(float(param) if isinstance(param, Decimal) else param for param in params)
        return query.replace("%s", "?"), sqlite_params
    return query, tuple(params)


def _sqlite_connection():
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _postgres_connection():
    if psycopg2 is None:
        raise RuntimeError("psycopg2-binary no está instalado.")
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        host = urlsplit(database_url).hostname or ""
        options = {}
        if host not in {"localhost", "127.0.0.1", "::1"}:
            options["sslmode"] = os.getenv("DB_SSLMODE", "require")
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            dbname=os.getenv("DB_NAME", "ferreteria_db"),
        )
    conn.autocommit = False
    return conn


def get_db_connection():
    engine = _database_engine()
    if engine in {"sqlite", "sqlite3"}:
        return _sqlite_connection()
    if engine in {"postgres", "postgresql"}:
        return _postgres_connection()
    raise RuntimeError(f"Motor de base de datos no compatible: {engine}")


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
            contacto TEXT NOT NULL DEFAULT '',
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
            marca TEXT NOT NULL DEFAULT '',
            talla TEXT NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '',
            genero TEXT NOT NULL DEFAULT 'Unisex',
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
            numero TEXT UNIQUE,
            id_cliente INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            subtotal REAL NOT NULL DEFAULT 0,
            descuento_pct REAL NOT NULL DEFAULT 0,
            descuento REAL NOT NULL DEFAULT 0,
            impuesto REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
        """
    )
    _ensure_sqlite_column(conn, "proveedores", "contacto", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "productos", "marca", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "productos", "talla", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "productos", "color", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "productos", "genero", "TEXT NOT NULL DEFAULT 'Unisex'")
    _ensure_sqlite_column(conn, "facturas", "numero", "TEXT")
    _ensure_sqlite_column(conn, "facturas", "estado", "TEXT NOT NULL DEFAULT 'Pendiente'")
    _ensure_sqlite_column(conn, "facturas", "subtotal", "REAL NOT NULL DEFAULT 0")
    _ensure_sqlite_column(conn, "facturas", "descuento_pct", "REAL NOT NULL DEFAULT 0")
    _ensure_sqlite_column(conn, "facturas", "descuento", "REAL NOT NULL DEFAULT 0")
    _ensure_sqlite_column(conn, "facturas", "impuesto", "REAL NOT NULL DEFAULT 0")
    for invoice in conn.execute("SELECT id_factura FROM facturas WHERE numero IS NULL").fetchall():
        invoice_id = invoice["id_factura"]
        conn.execute("UPDATE facturas SET numero = ? WHERE id_factura = ?", (f"FAC-{invoice_id:03d}", invoice_id))
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_facturas_numero ON facturas(numero)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS detalle_facturas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura INTEGER NOT NULL REFERENCES facturas(id_factura) ON DELETE CASCADE,
            codigo_producto TEXT NOT NULL REFERENCES productos(codigo),
            nombre_prenda TEXT NOT NULL DEFAULT '',
            marca TEXT NOT NULL DEFAULT '',
            talla TEXT NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '',
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0)
        )
        """
    )
    _ensure_sqlite_column(conn, "detalle_facturas", "nombre_prenda", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "detalle_facturas", "marca", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "detalle_facturas", "talla", "TEXT NOT NULL DEFAULT ''")
    _ensure_sqlite_column(conn, "detalle_facturas", "color", "TEXT NOT NULL DEFAULT ''")
    conn.execute(
        """
        UPDATE detalle_facturas SET
            nombre_prenda = (SELECT nombre FROM productos WHERE productos.codigo = detalle_facturas.codigo_producto),
            marca = (SELECT marca FROM productos WHERE productos.codigo = detalle_facturas.codigo_producto),
            talla = (SELECT talla FROM productos WHERE productos.codigo = detalle_facturas.codigo_producto),
            color = (SELECT color FROM productos WHERE productos.codigo = detalle_facturas.codigo_producto)
        WHERE nombre_prenda = ''
        """
    )
    for old_code, old_name in PRODUCTOS_ANTIGUOS:
        conn.execute(
            "DELETE FROM productos WHERE codigo = ? AND nombre = ? AND NOT EXISTS (SELECT 1 FROM detalle_facturas WHERE detalle_facturas.codigo_producto = productos.codigo)",
            (old_code, old_name),
        )

    for proveedor in PROVEEDORES_INICIALES:
        old_supplier_names = ("FerreMax S.A.", "Distribuidora Norte", "Herramientas del Sur")
        conn.execute(
            "UPDATE proveedores SET nombre = ?, contacto = ?, telefono = ?, correo = ? WHERE id_proveedor = ? AND nombre IN (?, ?, ?)",
            (proveedor["nombre"], proveedor["contacto"], proveedor["telefono"], proveedor["correo"], proveedor["id_proveedor"], *old_supplier_names),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO proveedores (id_proveedor, nombre, contacto, telefono, correo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                proveedor["id_proveedor"],
                proveedor["nombre"],
                proveedor["contacto"],
                proveedor["telefono"],
                proveedor["correo"],
            ),
        )

    for cliente in CLIENTES_INICIALES:
        conn.execute(
            "INSERT OR IGNORE INTO clientes (id_cliente, nombre, cedula, telefono, correo) VALUES (?, ?, ?, ?, ?)",
            (cliente["id_cliente"], cliente["nombre"], cliente["cedula"], cliente["telefono"], cliente["correo"]),
        )

    for producto in PRODUCTOS_INICIALES:
        conn.execute(
            """
            INSERT OR IGNORE INTO productos (codigo, nombre, categoria, marca, talla, color, genero, precio, stock, id_proveedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                producto["codigo"],
                producto["nombre"],
                producto["categoria"],
                producto["marca"],
                producto["talla"],
                producto["color"],
                producto["genero"],
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


def _ensure_sqlite_column(conn, table, column, definition):
    columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if not any(existing[1] == column for existing in columns):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _initialize_postgres_database(conn):
    cursor = conn.cursor()
    statements = [
        "CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, usuario VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL)",
        "CREATE TABLE IF NOT EXISTS proveedores (id_proveedor SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL, contacto VARCHAR(100) NOT NULL DEFAULT '', telefono VARCHAR(20), correo VARCHAR(100))",
        "CREATE TABLE IF NOT EXISTS clientes (id_cliente SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL, cedula VARCHAR(20) NOT NULL UNIQUE, telefono VARCHAR(20), correo VARCHAR(100))",
        "CREATE TABLE IF NOT EXISTS productos (codigo VARCHAR(20) PRIMARY KEY, nombre VARCHAR(100) NOT NULL, categoria VARCHAR(50) NOT NULL, marca VARCHAR(60) NOT NULL DEFAULT '', talla VARCHAR(20) NOT NULL DEFAULT '', color VARCHAR(40) NOT NULL DEFAULT '', genero VARCHAR(20) NOT NULL DEFAULT 'Unisex', precio NUMERIC(10,2) NOT NULL CHECK (precio >= 0), stock INTEGER NOT NULL CHECK (stock >= 0), id_proveedor INTEGER REFERENCES proveedores(id_proveedor))",
        "CREATE TABLE IF NOT EXISTS facturas (id_factura SERIAL PRIMARY KEY, numero VARCHAR(25) NOT NULL UNIQUE, id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente), fecha DATE NOT NULL, subtotal NUMERIC(10,2) NOT NULL DEFAULT 0, descuento_pct NUMERIC(5,2) NOT NULL DEFAULT 0, descuento NUMERIC(10,2) NOT NULL DEFAULT 0, impuesto NUMERIC(10,2) NOT NULL DEFAULT 0, total NUMERIC(10,2) NOT NULL CHECK (total >= 0), estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente')",
        "CREATE TABLE IF NOT EXISTS detalle_facturas (id_detalle SERIAL PRIMARY KEY, id_factura INTEGER NOT NULL REFERENCES facturas(id_factura) ON DELETE CASCADE, codigo_producto VARCHAR(20) NOT NULL REFERENCES productos(codigo), nombre_prenda VARCHAR(100) NOT NULL DEFAULT '', marca VARCHAR(60) NOT NULL DEFAULT '', talla VARCHAR(20) NOT NULL DEFAULT '', color VARCHAR(40) NOT NULL DEFAULT '', cantidad INTEGER NOT NULL CHECK (cantidad > 0), precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario >= 0), subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0))",
        "ALTER TABLE detalle_facturas ADD COLUMN IF NOT EXISTS nombre_prenda VARCHAR(100) NOT NULL DEFAULT ''",
        "ALTER TABLE detalle_facturas ADD COLUMN IF NOT EXISTS marca VARCHAR(60) NOT NULL DEFAULT ''",
        "ALTER TABLE detalle_facturas ADD COLUMN IF NOT EXISTS talla VARCHAR(20) NOT NULL DEFAULT ''",
        "ALTER TABLE detalle_facturas ADD COLUMN IF NOT EXISTS color VARCHAR(40) NOT NULL DEFAULT ''",
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS marca VARCHAR(60) NOT NULL DEFAULT ''",
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS talla VARCHAR(20) NOT NULL DEFAULT ''",
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS color VARCHAR(40) NOT NULL DEFAULT ''",
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS genero VARCHAR(20) NOT NULL DEFAULT 'Unisex'",
        "UPDATE detalle_facturas d SET nombre_prenda = p.nombre, marca = p.marca, talla = p.talla, color = p.color FROM productos p WHERE p.codigo = d.codigo_producto AND d.nombre_prenda = ''",
        "ALTER TABLE proveedores ADD COLUMN IF NOT EXISTS contacto VARCHAR(100) NOT NULL DEFAULT ''",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS numero VARCHAR(25)",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente'",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS subtotal NUMERIC(10,2) NOT NULL DEFAULT 0",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS descuento_pct NUMERIC(5,2) NOT NULL DEFAULT 0",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS descuento NUMERIC(10,2) NOT NULL DEFAULT 0",
        "ALTER TABLE facturas ADD COLUMN IF NOT EXISTS impuesto NUMERIC(10,2) NOT NULL DEFAULT 0",
        "UPDATE facturas SET numero = 'FAC-' || LPAD(id_factura::text, 3, '0') WHERE numero IS NULL",
        "ALTER TABLE facturas ALTER COLUMN numero SET NOT NULL",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_facturas_numero ON facturas(numero)",
        "CREATE INDEX IF NOT EXISTS idx_productos_id_proveedor ON productos(id_proveedor)",
    ]
    for statement in statements:
        cursor.execute(statement)

    for old_code, old_name in PRODUCTOS_ANTIGUOS:
        cursor.execute(
            "DELETE FROM productos WHERE codigo = %s AND nombre = %s AND NOT EXISTS (SELECT 1 FROM detalle_facturas WHERE detalle_facturas.codigo_producto = productos.codigo)",
            (old_code, old_name),
        )

    for proveedor in PROVEEDORES_INICIALES:
        cursor.execute(
            "UPDATE proveedores SET nombre = %s, contacto = %s, telefono = %s, correo = %s WHERE id_proveedor = %s AND nombre IN (%s, %s, %s)",
            (proveedor["nombre"], proveedor["contacto"], proveedor["telefono"], proveedor["correo"], proveedor["id_proveedor"], "FerreMax S.A.", "Distribuidora Norte", "Herramientas del Sur"),
        )
        cursor.execute(
            "INSERT INTO proveedores (id_proveedor, nombre, contacto, telefono, correo) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id_proveedor) DO NOTHING",
            (proveedor["id_proveedor"], proveedor["nombre"], proveedor["contacto"], proveedor["telefono"], proveedor["correo"]),
        )
    for cliente in CLIENTES_INICIALES:
        cursor.execute(
            "INSERT INTO clientes (id_cliente, nombre, cedula, telefono, correo) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (cedula) DO NOTHING",
            (cliente["id_cliente"], cliente["nombre"], cliente["cedula"], cliente["telefono"], cliente["correo"]),
        )
    for producto in PRODUCTOS_INICIALES:
        cursor.execute(
            "INSERT INTO productos (codigo, nombre, categoria, marca, talla, color, genero, precio, stock, id_proveedor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (codigo) DO NOTHING",
            (producto["codigo"], producto["nombre"], producto["categoria"], producto["marca"], producto["talla"], producto["color"], producto["genero"], producto["precio"], producto["stock"], producto["id_proveedor"]),
        )
    for table, id_column in (("proveedores", "id_proveedor"), ("clientes", "id_cliente"), ("usuarios", "id"), ("facturas", "id_factura")):
        cursor.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', '{id_column}'), GREATEST(COALESCE((SELECT MAX({id_column}) FROM {table}), 1), 1), true)"
        )
    conn.commit()


def initialize_database():
    conn = None
    try:
        conn = get_db_connection()
        engine = _database_engine()
        if engine in {"sqlite", "sqlite3"}:
            _initialize_sqlite_database(conn)
        else:
            _initialize_postgres_database(conn)
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
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
    except _database_errors():
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
        "marca": row[3],
        "talla": row[4],
        "color": row[5],
        "genero": row[6],
        "precio": float(row[7]),
        "stock": int(row[8]),
        "id_proveedor": row[9],
        "proveedor": row[10] if len(row) > 10 else None,
    }


def get_products():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
                 SELECT p.codigo, p.nombre, p.categoria, p.marca, p.talla, p.color, p.genero,
                     p.precio, p.stock, p.id_proveedor, pr.nombre AS proveedor
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
                 SELECT p.codigo, p.nombre, p.categoria, p.marca, p.talla, p.color, p.genero,
                     p.precio, p.stock, p.id_proveedor, pr.nombre AS proveedor
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
            INSERT INTO productos (codigo, nombre, categoria, marca, talla, color, genero, precio, stock, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        params = (
            producto["codigo"],
            producto["nombre"],
            producto["categoria"],
            producto.get("marca", ""),
            producto.get("talla", ""),
            producto.get("color", ""),
            producto.get("genero", "Unisex"),
            float(producto["precio"]),
            int(producto["stock"]),
            producto.get("id_proveedor"),
        )
        cursor.execute(*_parameterized_sql(query, params))
        conn.commit()
        return True
    except _database_errors():
        conn.rollback()
        return False
    finally:
        conn.close()


def update_product(codigo_actual, codigo_nuevo, nombre, categoria, precio, stock, id_proveedor=None, marca="", talla="", color="", genero="Unisex"):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE productos
            SET codigo = %s, nombre = %s, categoria = %s, marca = %s, talla = %s,
                color = %s, genero = %s, precio = %s, stock = %s, id_proveedor = %s
            WHERE codigo = %s
            """
        params = (codigo_nuevo, nombre, categoria, marca, talla, color, genero, float(precio), int(stock), id_proveedor, codigo_actual)
        cursor.execute(*_parameterized_sql(query, params))
        conn.commit()
        return cursor.rowcount > 0
    except _database_errors():
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
    except _database_errors():
        conn.rollback()
        return False
    finally:
        conn.close()


def _row_as_dict(cursor, row):
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    return dict(zip((column[0] for column in cursor.description), row))


def _read_rows(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(*_parameterized_sql(query, params))
        return [_row_as_dict(cursor, row) for row in cursor.fetchall()]
    finally:
        conn.close()


def _read_row(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(*_parameterized_sql(query, params))
        return _row_as_dict(cursor, cursor.fetchone())
    finally:
        conn.close()


def _write(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(*_parameterized_sql(query, params))
        conn.commit()
        return cursor.rowcount > 0
    except _database_errors():
        conn.rollback()
        return False
    finally:
        conn.close()


def get_clients():
    return _read_rows("SELECT id_cliente, nombre, cedula, telefono, correo FROM clientes ORDER BY id_cliente")


def get_client_by_id(client_id):
    return _read_row("SELECT id_cliente, nombre, cedula, telefono, correo FROM clientes WHERE id_cliente = %s", (client_id,))


def create_client(client):
    return _write(
        "INSERT INTO clientes (nombre, cedula, telefono, correo) VALUES (%s, %s, %s, %s)",
        (client["nombre"], client["cedula"], client["telefono"], client["correo"]),
    )


def update_client(client_id, client):
    return _write(
        "UPDATE clientes SET nombre = %s, cedula = %s, telefono = %s, correo = %s WHERE id_cliente = %s",
        (client["nombre"], client["cedula"], client["telefono"], client["correo"], client_id),
    )


def delete_client(client_id):
    return _write("DELETE FROM clientes WHERE id_cliente = %s", (client_id,))


def get_providers():
    return _read_rows(
        "SELECT id_proveedor, nombre AS empresa, contacto, telefono, correo FROM proveedores ORDER BY id_proveedor"
    )


def get_provider_by_id(provider_id):
    return _read_row(
        "SELECT id_proveedor, nombre AS empresa, contacto, telefono, correo FROM proveedores WHERE id_proveedor = %s",
        (provider_id,),
    )


def create_provider(provider):
    return _write(
        "INSERT INTO proveedores (nombre, contacto, telefono, correo) VALUES (%s, %s, %s, %s)",
        (provider["empresa"], provider["contacto"], provider["telefono"], provider["correo"]),
    )


def update_provider(provider_id, provider):
    return _write(
        "UPDATE proveedores SET nombre = %s, contacto = %s, telefono = %s, correo = %s WHERE id_proveedor = %s",
        (provider["empresa"], provider["contacto"], provider["telefono"], provider["correo"], provider_id),
    )


def delete_provider(provider_id):
    return _write("DELETE FROM proveedores WHERE id_proveedor = %s", (provider_id,))


def get_invoices(estado=None, termino=None):
    query = """
        SELECT f.id_factura, f.numero, f.id_cliente, c.nombre AS cliente, f.fecha,
               f.subtotal, f.descuento_pct, f.descuento, f.impuesto, f.total, f.estado
        FROM facturas f JOIN clientes c ON c.id_cliente = f.id_cliente
        WHERE 1 = 1
    """
    params = []
    if estado in {"Pendiente", "Pagada", "Anulada"}:
        query += " AND f.estado = %s"
        params.append(estado)
    if termino:
        query += " AND (LOWER(f.numero) LIKE %s OR LOWER(c.nombre) LIKE %s)"
        term = f"%{termino.strip().lower()}%"
        params.extend((term, term))
    query += " ORDER BY f.fecha DESC, f.id_factura DESC"
    return _read_rows(query, tuple(params))


def get_invoice_by_id(invoice_id):
    return _read_row(
        """
         SELECT f.id_factura, f.numero, f.id_cliente, c.nombre AS cliente, f.fecha,
             f.subtotal, f.descuento_pct, f.descuento, f.impuesto, f.total, f.estado
        FROM facturas f JOIN clientes c ON c.id_cliente = f.id_cliente
        WHERE f.id_factura = %s
        """,
        (invoice_id,),
    )


def get_invoice_lines(invoice_id):
    return _read_rows(
        """
           SELECT d.codigo_producto, d.cantidad, d.precio_unitario, d.subtotal,
               d.nombre_prenda AS prenda, d.marca, d.talla, d.color, p.stock
        FROM detalle_facturas d JOIN productos p ON p.codigo = d.codigo_producto
        WHERE d.id_factura = %s ORDER BY d.id_detalle
        """,
        (invoice_id,),
    )


def _prepare_invoice_lines(lines):
    quantities = {}
    for line in lines:
        code = str(line.get("codigo_producto", "")).strip()
        try:
            quantity = int(line.get("cantidad", 0))
        except (TypeError, ValueError):
            continue
        if code and quantity > 0:
            quantities[code] = quantities.get(code, 0) + quantity
    if not quantities:
        raise ValueError("La factura debe incluir al menos una prenda.")
    return quantities


def _money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _add_invoice_lines(cursor, invoice_id, quantities):
    subtotal = Decimal("0.00")
    for code, quantity in quantities.items():
        cursor.execute(*_parameterized_sql(
            "SELECT precio, stock, nombre, marca, talla, color FROM productos WHERE codigo = %s", (code,)
        ))
        product = cursor.fetchone()
        if product is None:
            raise ValueError(f"La prenda {code} ya no existe en el inventario.")
        price = product["precio"] if hasattr(product, "keys") else product[0]
        stock = product["stock"] if hasattr(product, "keys") else product[1]
        product_name = product["nombre"] if hasattr(product, "keys") else product[2]
        brand = product["marca"] if hasattr(product, "keys") else product[3]
        size = product["talla"] if hasattr(product, "keys") else product[4]
        color = product["color"] if hasattr(product, "keys") else product[5]
        if int(stock) < quantity:
            raise ValueError(f"Existencias insuficientes para {code}.")
        cursor.execute(*_parameterized_sql(
            "UPDATE productos SET stock = stock - %s WHERE codigo = %s AND stock >= %s",
            (quantity, code, quantity),
        ))
        if cursor.rowcount != 1:
            raise ValueError(f"Existencias insuficientes para {code}.")
        line_subtotal = _money(price) * quantity
        subtotal += line_subtotal
        cursor.execute(*_parameterized_sql(
            "INSERT INTO detalle_facturas (id_factura, codigo_producto, nombre_prenda, marca, talla, color, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (invoice_id, code, product_name, brand, size, color, quantity, price, line_subtotal),
        ))
    return _money(subtotal)


def _invoice_totals(subtotal, discount_percent):
    discount_rate = Decimal(str(discount_percent))
    if discount_rate < 0 or discount_rate > 100:
        raise ValueError("El descuento debe estar entre 0 y 100%.")
    discount = _money(subtotal * discount_rate / Decimal("100"))
    taxable = subtotal - discount
    tax = _money(taxable * Decimal("0.15"))
    return discount, tax, _money(taxable + tax)


def create_invoice(invoice):
    conn = get_db_connection()
    try:
        quantities = _prepare_invoice_lines(invoice.get("lineas", []))
        cursor = conn.cursor()
        params = (invoice["numero"], invoice["id_cliente"], invoice["fecha"], 0, invoice["estado"])
        if _database_engine() in {"sqlite", "sqlite3"}:
            cursor.execute(*_parameterized_sql(
                "INSERT INTO facturas (numero, id_cliente, fecha, total, estado) VALUES (%s, %s, %s, %s, %s)", params
            ))
            invoice_id = cursor.lastrowid
        else:
            cursor.execute(*_parameterized_sql(
                "INSERT INTO facturas (numero, id_cliente, fecha, total, estado) VALUES (%s, %s, %s, %s, %s) RETURNING id_factura", params
            ))
            invoice_id = cursor.fetchone()[0]
        subtotal = _add_invoice_lines(cursor, invoice_id, quantities)
        discount_percent = invoice.get("descuento_pct", 0)
        discount, tax, total = _invoice_totals(subtotal, discount_percent)
        cursor.execute(*_parameterized_sql(
            "UPDATE facturas SET subtotal = %s, descuento_pct = %s, descuento = %s, impuesto = %s, total = %s WHERE id_factura = %s",
            (subtotal, discount_percent, discount, tax, total, invoice_id),
        ))
        conn.commit()
        return True
    except (ValueError, *_database_errors()):
        conn.rollback()
        return False
    finally:
        conn.close()


def update_invoice(invoice_id, invoice):
    conn = get_db_connection()
    try:
        quantities = _prepare_invoice_lines(invoice.get("lineas", []))
        cursor = conn.cursor()
        cursor.execute(*_parameterized_sql("SELECT estado FROM facturas WHERE id_factura = %s", (invoice_id,)))
        current = cursor.fetchone()
        if current is None or (current["estado"] if hasattr(current, "keys") else current[0]) == "Anulada":
            return False
        cursor.execute(*_parameterized_sql(
            "SELECT codigo_producto, cantidad FROM detalle_facturas WHERE id_factura = %s", (invoice_id,)
        ))
        old_lines = cursor.fetchall()
        for line in old_lines:
            code = line["codigo_producto"] if hasattr(line, "keys") else line[0]
            quantity = line["cantidad"] if hasattr(line, "keys") else line[1]
            cursor.execute(*_parameterized_sql(
                "UPDATE productos SET stock = stock + %s WHERE codigo = %s", (quantity, code)
            ))
        cursor.execute(*_parameterized_sql("DELETE FROM detalle_facturas WHERE id_factura = %s", (invoice_id,)))
        subtotal = _add_invoice_lines(cursor, invoice_id, quantities)
        discount_percent = invoice.get("descuento_pct", 0)
        discount, tax, total = _invoice_totals(subtotal, discount_percent)
        cursor.execute(*_parameterized_sql(
            "UPDATE facturas SET numero = %s, id_cliente = %s, fecha = %s, estado = %s, subtotal = %s, descuento_pct = %s, descuento = %s, impuesto = %s, total = %s WHERE id_factura = %s",
            (invoice["numero"], invoice["id_cliente"], invoice["fecha"], invoice["estado"], subtotal, discount_percent, discount, tax, total, invoice_id),
        ))
        success = cursor.rowcount > 0
        conn.commit()
        return success
    except (ValueError, *_database_errors()):
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_invoice(invoice_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(*_parameterized_sql("SELECT estado FROM facturas WHERE id_factura = %s", (invoice_id,)))
        invoice = cursor.fetchone()
        if invoice is None:
            return False
        status = invoice["estado"] if hasattr(invoice, "keys") else invoice[0]
        if status == "Anulada":
            return False
        cursor.execute(*_parameterized_sql(
            "SELECT codigo_producto, cantidad FROM detalle_facturas WHERE id_factura = %s", (invoice_id,)
        ))
        for line in cursor.fetchall():
            code = line["codigo_producto"] if hasattr(line, "keys") else line[0]
            quantity = line["cantidad"] if hasattr(line, "keys") else line[1]
            cursor.execute(*_parameterized_sql(
                "UPDATE productos SET stock = stock + %s WHERE codigo = %s", (quantity, code)
            ))
        cursor.execute(*_parameterized_sql(
            "UPDATE facturas SET estado = 'Anulada' WHERE id_factura = %s", (invoice_id,)
        ))
        conn.commit()
        return cursor.rowcount > 0
    except _database_errors():
        conn.rollback()
        return False
    finally:
        conn.close()



