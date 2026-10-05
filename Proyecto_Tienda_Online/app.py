import os
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from conexion import (
    create_user,
    create_client,
    create_invoice,
    create_provider,
    delete_product,
    delete_client,
    delete_invoice,
    delete_provider,
    get_client_by_id,
    get_clients,
    get_invoice_by_id,
    get_invoice_lines,
    get_invoices,
    get_product_by_code,
    get_products,
    get_provider_by_id,
    get_providers,
    get_user_by_id,
    get_user_by_username,
    initialize_database,
    insert_product,
    update_client,
    update_invoice,
    update_product,
    update_provider,
)
from forms import ClienteForm, FacturaForm, LoginForm, ProductoForm, ProveedorForm, UsuarioForm
from models import Usuario

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ferreteria_secret_key_2026")
app.config["WTF_CSRF_ENABLED"] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debe iniciar sesión para acceder a esta página."


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return Usuario(user_data["id"], user_data["usuario"], user_data["password"])
    return None


NOMBRE_SISTEMA = "Monte & Hilo"

RESUMEN_SISTEMA = {
    "modulos": 4,
    "mensaje": "Ropa de marca, escogida para durar",
}

initialize_database()


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = UsuarioForm()
    if form.validate_on_submit():
        username = form.usuario.data.strip()
        if get_user_by_username(username):
            flash("El nombre de usuario ya existe. Intente con otro.", "danger")
        else:
            password_hash = generate_password_hash(form.password.data)
            if create_user(username, password_hash):
                flash("Usuario registrado correctamente. Ahora puede iniciar sesión.", "success")
                return redirect(url_for("login"))
            flash("No se pudo registrar el usuario. Inténtelo nuevamente.", "danger")
    return render_template("registro.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.usuario.data.strip()
        password = form.password.data
        user_data = get_user_by_username(username)

        if user_data and check_password_hash(user_data["password"], password):
            user = Usuario(user_data["id"], user_data["usuario"], user_data["password"])
            login_user(user)
            flash(f"Bienvenido, {user.usuario}.", "success")
            return redirect(url_for("index"))

        flash("Credenciales incorrectas. Verifique su usuario y contraseña.", "danger")
    return render_template("login.html", form=form, nombre_sistema=NOMBRE_SISTEMA)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


@app.route("/")
def index():
    image_urls = [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=85",
    ]
    productos_destacados = get_products()[:4]
    for image_index, product in enumerate(productos_destacados):
        product["imagen"] = image_urls[image_index]
    return render_template(
        "index.html",
        productos=productos_destacados,
        nombre_sistema=NOMBRE_SISTEMA,
        resumen=RESUMEN_SISTEMA,
    )


def _set_product_supplier_choices(form):
    form.id_proveedor.choices = [(0, "Sin proveedor")] + [
        (provider["id_proveedor"], provider["empresa"]) for provider in get_providers()
    ]


def _set_invoice_client_choices(form):
    form.id_cliente.choices = [(client["id_cliente"], client["nombre"]) for client in get_clients()]


@app.route("/productos")
@login_required
def productos():
    return render_template("productos.html", productos=get_products(), nombre_sistema=NOMBRE_SISTEMA)


@app.route("/productos/formulario", methods=["GET", "POST"])
@login_required
def formulario_producto():
    form = ProductoForm()
    _set_product_supplier_choices(form)
    if form.validate_on_submit():
        producto = {
            "codigo": form.codigo.data.strip(),
            "nombre": form.nombre.data.strip(),
            "categoria": form.categoria.data.strip(),
            "marca": form.marca.data.strip(),
            "talla": form.talla.data.strip(),
            "color": form.color.data.strip(),
            "genero": form.genero.data,
            "precio": float(form.precio.data),
            "stock": int(form.stock.data),
            "id_proveedor": form.id_proveedor.data or None,
        }
        if insert_product(producto):
            flash("Producto registrado correctamente.", "success")
            return redirect(url_for("productos"))
        flash("No se pudo registrar el producto. Verifique el código o la conexión.", "danger")
    return render_template("formulario_producto.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=False)


@app.route("/productos/editar/<codigo>", methods=["GET", "POST"])
@login_required
def editar_producto(codigo):
    producto = get_product_by_code(codigo)
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos"))

    form = ProductoForm()
    _set_product_supplier_choices(form)
    if request.method == "GET":
        form.codigo.data = producto["codigo"]
        form.nombre.data = producto["nombre"]
        form.categoria.data = producto["categoria"]
        form.marca.data = producto["marca"]
        form.talla.data = producto["talla"]
        form.color.data = producto["color"]
        form.genero.data = producto["genero"]
        form.precio.data = producto["precio"]
        form.stock.data = producto["stock"]
        form.id_proveedor.data = producto["id_proveedor"] or 0

    if form.validate_on_submit():
        codigo_actual = producto["codigo"]
        codigo_nuevo = form.codigo.data.strip()
        nombre = form.nombre.data.strip()
        categoria = form.categoria.data.strip()
        precio = float(form.precio.data)
        stock = int(form.stock.data)

        if update_product(
            codigo_actual, codigo_nuevo, nombre, categoria, precio, stock,
            form.id_proveedor.data or None, form.marca.data.strip(), form.talla.data.strip(),
            form.color.data.strip(), form.genero.data,
        ):
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("productos"))
        flash("No se pudo actualizar el producto.", "danger")

    return render_template("formulario_producto.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=True, codigo=codigo)


@app.route("/productos/eliminar/<codigo>", methods=["POST"])
@login_required
def eliminar_producto(codigo):
    if delete_product(codigo):
        flash("Producto eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el producto.", "danger")
    return redirect(url_for("productos"))


@app.route("/clientes")
@login_required
def clientes():
    return render_template("clientes.html", clientes=get_clients(), nombre_sistema=NOMBRE_SISTEMA)


@app.route("/clientes/formulario", methods=["GET", "POST"])
@login_required
def formulario_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        client = {
            "nombre": form.nombre.data.strip(),
            "cedula": form.cedula.data.strip(),
            "telefono": form.telefono.data.strip(),
            "correo": form.correo.data.strip(),
        }
        if create_client(client):
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes"))
        flash("No se pudo registrar el cliente. Verifique que la cédula no esté registrada.", "danger")
    return render_template("formulario_cliente.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=False)


@app.route("/clientes/editar/<int:client_id>", methods=["GET", "POST"])
@login_required
def editar_cliente(client_id):
    client = get_client_by_id(client_id)
    if not client:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes"))
    form = ClienteForm()
    if request.method == "GET":
        form.nombre.data = client["nombre"]
        form.cedula.data = client["cedula"]
        form.telefono.data = client["telefono"]
        form.correo.data = client["correo"]
    if form.validate_on_submit():
        updated_client = {
            "nombre": form.nombre.data.strip(),
            "cedula": form.cedula.data.strip(),
            "telefono": form.telefono.data.strip(),
            "correo": form.correo.data.strip(),
        }
        if update_client(client_id, updated_client):
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("clientes"))
        flash("No se pudo actualizar el cliente. Verifique que la cédula no esté duplicada.", "danger")
    return render_template("formulario_cliente.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=True)


@app.route("/clientes/eliminar/<int:client_id>", methods=["POST"])
@login_required
def eliminar_cliente(client_id):
    if delete_client(client_id):
        flash("Cliente eliminado correctamente.", "success")
    else:
        flash("No se puede eliminar: el cliente puede tener facturas asociadas.", "danger")
    return redirect(url_for("clientes"))


@app.route("/proveedores")
@login_required
def proveedores():
    return render_template("proveedores.html", proveedores=get_providers(), nombre_sistema=NOMBRE_SISTEMA)


@app.route("/proveedores/formulario", methods=["GET", "POST"])
@login_required
def formulario_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        provider = {
            "empresa": form.empresa.data.strip(),
            "contacto": form.contacto.data.strip(),
            "telefono": form.telefono.data.strip(),
            "correo": form.correo.data.strip(),
        }
        if create_provider(provider):
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores"))
        flash("No se pudo registrar el proveedor.", "danger")
    return render_template("formulario_proveedor.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=False)


@app.route("/proveedores/editar/<int:provider_id>", methods=["GET", "POST"])
@login_required
def editar_proveedor(provider_id):
    provider = get_provider_by_id(provider_id)
    if not provider:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores"))
    form = ProveedorForm()
    if request.method == "GET":
        form.empresa.data = provider["empresa"]
        form.contacto.data = provider["contacto"]
        form.telefono.data = provider["telefono"]
        form.correo.data = provider["correo"]
    if form.validate_on_submit():
        updated_provider = {
            "empresa": form.empresa.data.strip(),
            "contacto": form.contacto.data.strip(),
            "telefono": form.telefono.data.strip(),
            "correo": form.correo.data.strip(),
        }
        if update_provider(provider_id, updated_provider):
            flash("Proveedor actualizado correctamente.", "success")
            return redirect(url_for("proveedores"))
        flash("No se pudo actualizar el proveedor.", "danger")
    return render_template("formulario_proveedor.html", form=form, nombre_sistema=NOMBRE_SISTEMA, editar=True)


@app.route("/proveedores/eliminar/<int:provider_id>", methods=["POST"])
@login_required
def eliminar_proveedor(provider_id):
    if delete_provider(provider_id):
        flash("Proveedor eliminado correctamente.", "success")
    else:
        flash("No se puede eliminar: el proveedor puede tener productos asociados.", "danger")
    return redirect(url_for("proveedores"))


@app.route("/facturacion")
@login_required
def facturacion():
    estado = request.args.get("estado", "")
    termino = request.args.get("q", "").strip()
    facturas = get_invoices(estado=estado, termino=termino)
    return render_template(
        "facturacion.html", facturas=facturas, filtro_estado=estado, termino=termino,
        nombre_sistema=NOMBRE_SISTEMA,
    )


@app.route("/facturacion/formulario", methods=["GET", "POST"])
@login_required
def formulario_facturacion():
    form = FacturaForm()
    _set_invoice_client_choices(form)
    if form.validate_on_submit():
        lines, line_error = _invoice_lines_from_request()
        if line_error:
            flash(line_error, "danger")
            return render_template("formulario_facturacion.html", form=form, productos=get_products(), lineas=[], nombre_sistema=NOMBRE_SISTEMA, editar=False)
        invoice = {
            "numero": form.numero.data.strip(),
            "id_cliente": form.id_cliente.data,
            "fecha": form.fecha.data.isoformat(),
            "estado": form.estado.data,
            "descuento_pct": float(form.descuento_pct.data),
            "lineas": lines,
        }
        if create_invoice(invoice):
            flash("Factura registrada correctamente.", "success")
            return redirect(url_for("facturacion"))
        flash("No se pudo registrar. Revise el número, las prendas seleccionadas y sus existencias.", "danger")
    return render_template("formulario_facturacion.html", form=form, productos=get_products(), lineas=[], nombre_sistema=NOMBRE_SISTEMA, editar=False)


def _invoice_lines_from_request():
    codes = request.form.getlist("codigo_producto")
    quantities = request.form.getlist("cantidad")
    lines = []
    for code, raw_quantity in zip(codes, quantities):
        if not code and not raw_quantity:
            continue
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            return [], "Cada renglón debe tener una cantidad entera mayor que cero."
        if not code or quantity < 1:
            return [], "Seleccione una prenda y una cantidad mayor que cero en cada renglón."
        lines.append({"codigo_producto": code, "cantidad": quantity})
    if not lines:
        return [], "Agregue al menos una prenda a la factura."
    return lines, None


@app.route("/facturacion/editar/<int:invoice_id>", methods=["GET", "POST"])
@login_required
def editar_factura(invoice_id):
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash("Factura no encontrada.", "danger")
        return redirect(url_for("facturacion"))
    if invoice["estado"] == "Anulada":
        flash("Una factura anulada no se puede editar.", "warning")
        return redirect(url_for("facturacion"))
    form = FacturaForm()
    _set_invoice_client_choices(form)
    if request.method == "GET":
        form.numero.data = invoice["numero"]
        form.id_cliente.data = invoice["id_cliente"]
        invoice_date = invoice["fecha"]
        form.fecha.data = invoice_date if isinstance(invoice_date, date) else date.fromisoformat(str(invoice_date))
        form.estado.data = invoice["estado"]
        form.descuento_pct.data = invoice["descuento_pct"]
    lines = get_invoice_lines(invoice_id)
    if form.validate_on_submit():
        lines, line_error = _invoice_lines_from_request()
        if line_error:
            flash(line_error, "danger")
            return render_template("formulario_facturacion.html", form=form, productos=get_products(), lineas=get_invoice_lines(invoice_id), nombre_sistema=NOMBRE_SISTEMA, editar=True)
        updated_invoice = {
            "numero": form.numero.data.strip(),
            "id_cliente": form.id_cliente.data,
            "fecha": form.fecha.data.isoformat(),
            "estado": form.estado.data,
            "descuento_pct": float(form.descuento_pct.data),
            "lineas": lines,
        }
        if update_invoice(invoice_id, updated_invoice):
            flash("Factura actualizada correctamente.", "success")
            return redirect(url_for("facturacion"))
        flash("No se pudo actualizar. Revise el número, las prendas y sus existencias.", "danger")
    return render_template("formulario_facturacion.html", form=form, productos=get_products(), lineas=lines if request.method == "POST" else get_invoice_lines(invoice_id), nombre_sistema=NOMBRE_SISTEMA, editar=True)


@app.route("/facturacion/ver/<int:invoice_id>")
@login_required
def ver_factura(invoice_id):
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash("Factura no encontrada.", "danger")
        return redirect(url_for("facturacion"))
    return render_template(
        "ver_factura.html", factura=invoice, lineas=get_invoice_lines(invoice_id), nombre_sistema=NOMBRE_SISTEMA
    )


@app.route("/facturacion/eliminar/<int:invoice_id>", methods=["POST"])
@login_required
def eliminar_factura(invoice_id):
    if delete_invoice(invoice_id):
        flash("Factura anulada y existencias devueltas al inventario.", "success")
    else:
        flash("No se pudo anular; revise si ya estaba anulada.", "danger")
    return redirect(url_for("facturacion"))


if __name__ == "__main__":
    app.run(debug=True)
