from flask import Flask, flash, redirect, render_template, request, url_for

from conexion import (
    delete_product,
    get_product_by_code,
    get_products,
    initialize_database,
    insert_product,
    update_product,
)
from forms import ClienteForm, FacturaForm, ProductoForm, ProveedorForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "ferreteria_secret_key_2026"

NOMBRE_SISTEMA = "Ferretería Erick"

RESUMEN_SISTEMA = {
    "modulos": 4,
    "mensaje": "Panel de administración de la ferretería activo",
}

CLIENTES = [
    {"id": "C001", "nombre": "Erick Sánchez", "cedula": "2100000001", "telefono": "0999999999", "correo": "erick.sanchez@gmail.com"},
    {"id": "C002", "nombre": "Estefanía Ramón", "cedula": "2100000002", "telefono": "0988888888", "correo": "estefania.ramon@gmail.com"},
    {"id": "C003", "nombre": "Roberto Mena", "cedula": "2100000003", "telefono": "0977777777", "correo": "roberto.mena@gmail.com"},
]

PROVEEDORES = [
    {"id": "PR001", "empresa": "FerreMax S.A.", "contacto": "Luis Torres", "telefono": "0991111111", "correo": "ventas@ferremax.com"},
    {"id": "PR002", "empresa": "Distribuidora Norte", "contacto": "Ana Morales", "telefono": "0982222222", "correo": "info@distribuidoranorte.com"},
    {"id": "PR003", "empresa": "Herramientas del Sur", "contacto": "Pedro Gómez", "telefono": "0973333333", "correo": "contacto@herramientassur.com"},
]

FACTURAS = [
    {"numero": "FAC-001", "cliente": "Erick Sánchez", "fecha": "15/08/2026", "total": 125.50, "estado": "Pagada"},
    {"numero": "FAC-002", "cliente": "Estefanía Ramón", "fecha": "15/08/2026", "total": 85.00, "estado": "Pagada"},
    {"numero": "FAC-003", "cliente": "Roberto Mena", "fecha": "16/08/2026", "total": 45.75, "estado": "Pendiente"},
]

initialize_database()


@app.route("/")
def index():
    productos_destacados = get_products()[:3]
    return render_template(
        "index.html",
        productos=productos_destacados,
        nombre_sistema=NOMBRE_SISTEMA,
        resumen=RESUMEN_SISTEMA,
    )


@app.route("/productos")
def productos():
    return render_template("productos.html", productos=get_products(), nombre_sistema=NOMBRE_SISTEMA)


@app.route("/productos/formulario", methods=["GET", "POST"])
def formulario_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        producto = {
            "codigo": form.codigo.data.strip(),
            "nombre": form.nombre.data.strip(),
            "categoria": form.categoria.data.strip(),
            "precio": float(form.precio.data),
            "stock": int(form.stock.data),
        }
        if insert_product(producto):
            flash("Producto registrado correctamente.", "success")
            return redirect(url_for("productos"))
        flash("No se pudo registrar el producto. Verifique el código o la conexión.", "danger")
    return render_template("formulario_producto.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=False)


@app.route("/productos/editar/<codigo>", methods=["GET", "POST"])
def editar_producto(codigo):
    producto = get_product_by_code(codigo)
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos"))

    form = ProductoForm()
    if request.method == "GET":
        form.codigo.data = producto["codigo"]
        form.nombre.data = producto["nombre"]
        form.categoria.data = producto["categoria"]
        form.precio.data = producto["precio"]
        form.stock.data = producto["stock"]

    if form.validate_on_submit():
        codigo_actual = producto["codigo"]
        codigo_nuevo = form.codigo.data.strip()
        nombre = form.nombre.data.strip()
        categoria = form.categoria.data.strip()
        precio = float(form.precio.data)
        stock = int(form.stock.data)

        if update_product(codigo_actual, codigo_nuevo, nombre, categoria, precio, stock):
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("productos"))
        flash("No se pudo actualizar el producto.", "danger")

    return render_template("formulario_producto.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=True, codigo=codigo)


@app.route("/productos/eliminar/<codigo>", methods=["POST"])
def eliminar_producto(codigo):
    if delete_product(codigo):
        flash("Producto eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el producto.", "danger")
    return redirect(url_for("productos"))


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
