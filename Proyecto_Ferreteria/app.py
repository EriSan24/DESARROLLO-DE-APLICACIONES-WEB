from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    productos = [
        {"codigo": "P001", "nombre": "Martillo", "categoria": "Herramientas", "precio": 12.50, "stock": 25},
        {"codigo": "P002", "nombre": "Clavo 3in", "categoria": "Ferretería", "precio": 0.05, "stock": 200},
        {"codigo": "P003", "nombre": "Taladro", "categoria": "Eléctricas", "precio": 85.00, "stock": 5},
    ]
    return render_template("index.html", productos=productos)


@app.route("/productos")
def productos():
    items = [
        {"codigo": "P001", "nombre": "Martillo", "categoria": "Herramientas", "precio": 12.50, "stock": 25},
        {"codigo": "P002", "nombre": "Clavo 3in", "categoria": "Ferretería", "precio": 0.05, "stock": 200},
        {"codigo": "P003", "nombre": "Taladro", "categoria": "Eléctricas", "precio": 85.00, "stock": 5},
        {"codigo": "P004", "nombre": "Sierra", "categoria": "Herramientas", "precio": 45.00, "stock": 0},
    ]
    return render_template("productos.html", productos=items)


@app.route("/clientes")
def clientes():
    items = [
        {"id": "C001", "nombre": "Juan Pérez", "cedula": "2100000001", "telefono": "0999999999", "correo": "juan@gmail.com"},
        {"id": "C002", "nombre": "María López", "cedula": "2100000002", "telefono": "0988888888", "correo": "maria@gmail.com"},
        {"id": "C003", "nombre": "Carlos Sánchez", "cedula": "2100000003", "telefono": "0977777777", "correo": "carlos@gmail.com"},
    ]
    return render_template("clientes.html", clientes=items)


@app.route("/proveedores")
def proveedores():
    items = [
        {"id": "PR001", "empresa": "FerreImport S.A.", "contacto": "Luis Torres", "telefono": "0991111111", "correo": "ventas@ferreimport.com"},
        {"id": "PR002", "empresa": "Distribuidora Amazónica", "contacto": "Ana Morales", "telefono": "0982222222", "correo": "info@distribuidora.com"},
        {"id": "PR003", "empresa": "Herramientas del Ecuador", "contacto": "Pedro Gómez", "telefono": "0973333333", "correo": "contacto@herramientas.com"},
    ]
    return render_template("proveedores.html", proveedores=items)


@app.route("/facturacion")
def facturacion():
    items = [
        {"numero": "FAC-001", "cliente": "Juan Pérez", "fecha": "15/08/2026", "total": 125.50, "estado": "Pagada"},
        {"numero": "FAC-002", "cliente": "María López", "fecha": "15/08/2026", "total": 85.00, "estado": "Pagada"},
        {"numero": "FAC-003", "cliente": "Carlos Sánchez", "fecha": "16/08/2026", "total": 45.75, "estado": "Pendiente"},
    ]
    return render_template("facturacion.html", facturas=items)


if __name__ == "__main__":
    app.run(debug=True)
