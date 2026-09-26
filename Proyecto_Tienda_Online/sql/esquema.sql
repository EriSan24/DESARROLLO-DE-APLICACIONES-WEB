CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100) NOT NULL DEFAULT '',
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS productos (
    codigo VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    marca VARCHAR(60) NOT NULL,
    talla VARCHAR(20) NOT NULL,
    color VARCHAR(40) NOT NULL,
    genero VARCHAR(20) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor)
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura SERIAL PRIMARY KEY,
    numero VARCHAR(25) NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    fecha DATE NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL DEFAULT 0,
    descuento_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,
    descuento NUMERIC(10, 2) NOT NULL DEFAULT 0,
    impuesto NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total NUMERIC(10, 2) NOT NULL CHECK (total >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente'
);

CREATE TABLE IF NOT EXISTS detalle_facturas (
    id_detalle SERIAL PRIMARY KEY,
    id_factura INTEGER NOT NULL REFERENCES facturas(id_factura) ON DELETE CASCADE,
    codigo_producto VARCHAR(20) NOT NULL REFERENCES productos(codigo),
    nombre_prenda VARCHAR(100) NOT NULL,
    marca VARCHAR(60) NOT NULL,
    talla VARCHAR(20) NOT NULL,
    color VARCHAR(40) NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal NUMERIC(10, 2) NOT NULL CHECK (subtotal >= 0)
);