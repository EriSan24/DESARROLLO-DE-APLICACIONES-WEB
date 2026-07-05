const formulario = document.getElementById("formProducto");
const lista = document.getElementById("listaProductos");
const mensaje = document.getElementById("mensaje");
const total = document.getElementById("total");

const nombreInput = document.getElementById("nombre");
const descripcionInput = document.getElementById("descripcion");
const categoriaSelect = document.getElementById("categoria");

const feedbackNombre = document.getElementById("nombreFeedback");
const feedbackDescripcion = document.getElementById("descripcionFeedback");
const feedbackCategoria = document.getElementById("categoriaFeedback");

let registros = [];

const MIN_NOMBRE = 5;
const MIN_DESCRIPCION = 15;

function validarNombre() {
    const valor = nombreInput.value.trim();
    if (valor === "") {
        feedbackNombre.textContent = "El nombre es obligatorio.";
        setInvalid(nombreInput);
        return false;
    }

    if (valor.length < MIN_NOMBRE) {
        feedbackNombre.textContent = `El nombre debe tener al menos ${MIN_NOMBRE} caracteres.`;
        setInvalid(nombreInput);
        return false;
    }

    feedbackNombre.textContent = "";
    setValid(nombreInput);
    return true;
}

function validarDescripcion() {
    const valor = descripcionInput.value.trim();
    if (valor === "") {
        feedbackDescripcion.textContent = "La descripción es obligatoria.";
        setInvalid(descripcionInput);
        return false;
    }

    if (valor.length < MIN_DESCRIPCION) {
        feedbackDescripcion.textContent = `La descripción debe tener al menos ${MIN_DESCRIPCION} caracteres.`;
        setInvalid(descripcionInput);
        return false;
    }

    feedbackDescripcion.textContent = "";
    setValid(descripcionInput);
    return true;
}

function validarCategoria() {
    const valor = categoriaSelect.value;
    if (valor === "") {
        feedbackCategoria.textContent = "Selecciona una categoría válida.";
        setInvalid(categoriaSelect);
        return false;
    }

    feedbackCategoria.textContent = "";
    setValid(categoriaSelect);
    return true;
}

function setValid(elemento) {
    elemento.classList.remove("is-invalid");
    elemento.classList.add("is-valid");
}

function setInvalid(elemento) {
    elemento.classList.remove("is-valid");
    elemento.classList.add("is-invalid");
}

function limpiarClases() {
    [nombreInput, descripcionInput, categoriaSelect].forEach((elemento) => {
        elemento.classList.remove("is-invalid", "is-valid");
    });
}

function mostrarMensaje(tipo, texto) {
    mensaje.innerHTML = `
        <div class="alert ${tipo} alert-dismissible fade show" role="alert">
            ${texto}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        </div>
    `;
}

function actualizarTotal() {
    total.textContent = registros.length;
}

function crearTarjeta(registro) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "card mt-3 shadow";

    tarjeta.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="card-title">${registro.nombre}</h5>
                    <p class="card-text mb-2">${registro.descripcion}</p>
                    <span class="badge bg-primary">${registro.categoria}</span>
                </div>
                <button class="btn btn-danger btn-sm eliminar">Eliminar</button>
            </div>
        </div>
    `;

    tarjeta.querySelector(".eliminar").addEventListener("click", () => {
        const index = registros.indexOf(registro);
        if (index > -1) {
            registros.splice(index, 1);
            tarjeta.remove();
            actualizarTotal();
            mostrarMensaje("alert-danger", "Registro eliminado correctamente.");
        }
    });

    lista.appendChild(tarjeta);
}

function registrarProducto(event) {
    event.preventDefault();

    const nombreValido = validarNombre();
    const descripcionValida = validarDescripcion();
    const categoriaValida = validarCategoria();

    if (!nombreValido || !descripcionValida || !categoriaValida) {
        mostrarMensaje("alert-danger", "Hay errores en el formulario. Corrige los campos antes de registrar.");
        return;
    }

    const nuevoRegistro = {
        nombre: nombreInput.value.trim(),
        descripcion: descripcionInput.value.trim(),
        categoria: categoriaSelect.value,
    };

    registros.push(nuevoRegistro);
    crearTarjeta(nuevoRegistro);
    actualizarTotal();
    mostrarMensaje("alert-success", "Registro agregado correctamente.");
    formulario.reset();
    limpiarClases();
}

nombreInput.addEventListener("input", validarNombre);
nombreInput.addEventListener("blur", validarNombre);

descripcionInput.addEventListener("input", validarDescripcion);
descripcionInput.addEventListener("blur", validarDescripcion);

categoriaSelect.addEventListener("change", validarCategoria);

formulario.addEventListener("submit", registrarProducto);
