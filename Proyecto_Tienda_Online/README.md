# Monte & Hilo

Aplicación Flask para una boutique de ropa de marca. Gestiona prendas por marca, tipo, talla, color y línea; clientes; distribuidores; inventario; facturas de varias prendas; cobros y anulaciones.

## Funciones de venta

- Selección de cliente y una o más prendas por factura.
- Precio y existencias consultados en el servidor; la cantidad no puede superar el inventario.
- Cálculo de subtotal, descuento porcentual, IVA del 15% y total.
- Edición de comprobantes no anulados, consulta del detalle e impresión.
- Anulación con devolución de existencias y conservación del historial contable.
- Búsqueda por número/cliente y filtros por estado.

Las tablas principales son `clientes`, `proveedores`, `productos`, `facturas` y `detalle_facturas`. Los productos se relacionan con sus distribuidores y cada factura con su cliente y sus prendas mediante claves foráneas.

## Ejecución local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000/. En local se crea `data/ferreteria.db`; las credenciales de muestra son `Ericksanchez` / `Erick2000`. También puedes registrar una cuenta en `/registro`.

## Render y PostgreSQL

El Blueprint `render.yaml` configura Gunicorn y PostgreSQL para esta aplicación. Conecta el repositorio en Render y crea los recursos desde el Blueprint; el despliegue genera `SECRET_KEY` y asigna `DATABASE_URL`. La app crea o migra las tablas al iniciar. No configures `DB_ENGINE=sqlite` en producción.

Cuando termine el despliegue, usa la URL pública que Render asigne al servicio desde cualquier navegador. La aplicación y sus datos viven en el servidor, no en la pestaña del navegador ni en la computadora desde la que se inició localmente. El plan gratuito de Render puede suspender el servicio cuando está inactivo, por lo que la primera visita puede tardar en responder.

En la URL publicada, inicia sesión y prueba una venta con dos prendas: confirmar existencias, aplicar descuento, ver/imprimir la factura, editarla y anularla. La anulación debe restaurar el stock. La tasa IVA configurada es 15% y se puede ajustar en la capa de datos según las reglas aplicables al negocio.