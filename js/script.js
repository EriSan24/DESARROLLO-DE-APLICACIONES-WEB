const formulario = document.getElementById("formProducto");
const lista = document.getElementById("listaProductos");
const mensaje = document.getElementById("mensaje");
const total = document.getElementById("total");

let contador = 0;

formulario.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombre = document.getElementById("nombre").value.trim();
    const descripcion = document.getElementById("descripcion").value.trim();
    const categoria = document.getElementById("categoria").value;

    if (nombre === "" || descripcion === "" || categoria === "") {
        mensaje.innerHTML = `
            <div class="alert alert-danger">
                Todos los campos son obligatorios.
            </div>
        `;
        return;
    }

    mensaje.innerHTML = `
        <div class="alert alert-success">
            Registro agregado correctamente.
        </div>
    `;

    const tarjeta = document.createElement("div");
    tarjeta.className = "card mt-3 shadow";

    tarjeta.innerHTML = `
        <div class="card-body">
            <h5>${nombre}</h5>
            <p>${descripcion}</p>
            <span class="badge bg-primary">${categoria}</span>
            <button class="btn btn-danger float-end eliminar">Eliminar</button>
        </div>
    `;

    lista.appendChild(tarjeta);

    contador++;
    total.textContent = contador;

    formulario.reset();

    tarjeta.querySelector(".eliminar").addEventListener("click", function () {
        tarjeta.remove();
        contador--;
        total.textContent = contador;
    });
});
