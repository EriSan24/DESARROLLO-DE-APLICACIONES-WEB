CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS productos (
    codigo VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    id_proveedor INT,
    CONSTRAINT fk_productos_proveedores FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_facturas_clientes FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

INSERT INTO proveedores (nombre, telefono, correo) VALUES
('FerreMax S.A.', '0991111111', 'ventas@ferremax.com'),
('Distribuidora Norte', '0982222222', 'info@distribuidoranorte.com'),
('Herramientas del Sur', '0973333333', 'contacto@herramientassur.com')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

INSERT INTO productos (codigo, nombre, categoria, precio, stock, id_proveedor) VALUES
('P001', 'Martillo', 'Herramientas', 12.50, 25, 1),
('P002', 'Clavo 3in', 'Ferretería', 0.05, 200, 2),
('P003', 'Taladro', 'Eléctricas', 85.00, 5, 3),
('P004', 'Sierra', 'Herramientas', 45.00, 0, 1)
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), categoria = VALUES(categoria), precio = VALUES(precio), stock = VALUES(stock), id_proveedor = VALUES(id_proveedor);
