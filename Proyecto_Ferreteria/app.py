from flask import Flask, flash, redirect, render_template, url_for

from forms import ClienteForm, FacturaForm, ProductoForm, ProveedorForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "ferreteria_secret_key_2026"

NOMBRE_SISTEMA = "Ferretería El Constructor"

RESUMEN_SISTEMA = {
    "modulos": 4,
    "mensaje": "Panel de administración activo",
}

PRODUCTOS = [
    {"codigo": "P001", "nombre": "Martillo", "categoria": "Herramientas", "precio": 12.50, "stock": 25},
    {"codigo": "P002", "nombre": "Clavo 3in", "categoria": "Ferretería", "precio": 0.05, "stock": 200},
    {"codigo": "P003", "nombre": "Taladro", "categoria": "Eléctricas", "precio": 85.00, "stock": 5},
    {"codigo": "P004", "nombre": "Sierra", "categoria": "Herramientas", "precio": 45.00, "stock": 0},
]

CLIENTES = [
    {"id": "C001", "nombre": "erick Sanchez", "cedula": "2100000001", "telefono": "0999999999", "correo": "juan@gmail.com"},
    {"id": "C002", "nombre": "estefania ramon", "cedula": "2100000002", "telefono": "0988888888", "correo": "maria@gmail.com"},
    {"id": "C003", "nombre": "roberto mecias", "cedula": "2100000003", "telefono": "0977777777", "correo": "carlos@gmail.com"},
]

PROVEEDORES = [
    {"id": "PR001", "empresa": "FerreImport S.A.", "contacto": "Luis Torres", "telefono": "0991111111", "correo": "ventas@ferreimport.com"},
    {"id": "PR002", "empresa": "Distribuidora Amazónica", "contacto": "Ana Morales", "telefono": "0982222222", "correo": "info@distribuidora.com"},
    {"id": "PR003", "empresa": "Herramientas del Ecuador", "contacto": "Pedro Gómez", "telefono": "0973333333", "correo": "contacto@herramientas.com"},
]

FACTURAS = [
    {"numero": "FAC-001", "cliente": "Juan Pérez", "fecha": "15/08/2026", "total": 125.50, "estado": "Pagada"},
    {"numero": "FAC-002", "cliente": "María López", "fecha": "15/08/2026", "total": 85.00, "estado": "Pagada"},
    {"numero": "FAC-003", "cliente": "Carlos Sánchez", "fecha": "16/08/2026", "total": 45.75, "estado": "Pendiente"},
]


@app.route("/")
def index():
    productos_destacados = PRODUCTOS[:3]
    return render_template(
        "index.html",
        productos=productos_destacados,
        nombre_sistema=NOMBRE_SISTEMA,
        resumen=RESUMEN_SISTEMA,
    )


@app.route("/productos")
def productos():
    return render_template("productos.html", productos=PRODUCTOS, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/productos/formulario", methods=["GET", "POST"])
def formulario_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        PRODUCTOS.append(
            {
                "codigo": form.codigo.data.strip(),
                "nombre": form.nombre.data.strip(),
                "categoria": form.categoria.data.strip(),
                "precio": float(form.precio.data),
                "stock": int(form.stock.data),
            }
        )
        flash("Producto registrado correctamente.", "success")
        return redirect(url_for("productos"))
    return render_template("formulario_producto.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/clientes")
def clientes():
    return render_template("clientes.html", clientes=CLIENTES, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/clientes/formulario", methods=["GET", "POST"])
def formulario_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        CLIENTES.append(
            {
                "id": f"C{len(CLIENTES) + 1:03d}",
                "nombre": form.nombre.data.strip(),
                "cedula": form.cedula.data.strip(),
                "telefono": form.telefono.data.strip(),
                "correo": form.correo.data.strip(),
            }
        )
        flash("Cliente registrado correctamente.", "success")
        return redirect(url_for("clientes"))
    return render_template("formulario_cliente.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", proveedores=PROVEEDORES, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/proveedores/formulario", methods=["GET", "POST"])
def formulario_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        PROVEEDORES.append(
            {
                "id": f"PR{len(PROVEEDORES) + 1:03d}",
                "empresa": form.empresa.data.strip(),
                "contacto": form.contacto.data.strip(),
                "telefono": form.telefono.data.strip(),
                "correo": form.correo.data.strip(),
            }
        )
        flash("Proveedor registrado correctamente.", "success")
        return redirect(url_for("proveedores"))
    return render_template("formulario_proveedor.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html", facturas=FACTURAS, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/facturacion/formulario", methods=["GET", "POST"])
def formulario_facturacion():
    form = FacturaForm()
    if form.validate_on_submit():
        FACTURAS.append(
            {
                "numero": form.numero.data.strip(),
                "cliente": form.cliente.data.strip(),
                "fecha": form.fecha.data.strftime("%d/%m/%Y"),
                "total": float(form.total.data),
                "estado": form.estado.data,
            }
        )
        flash("Factura registrada correctamente.", "success")
        return redirect(url_for("facturacion"))
    return render_template("formulario_facturacion.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


if __name__ == "__main__":
    app.run(debug=True)
