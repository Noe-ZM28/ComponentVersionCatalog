# Component Version Catalog — Prototype v0.1

## What this is
A browser-based front end for consulting projects, components, tickets, change history, and associated files through the FastAPI backend.

**All records, version numbers, ticket keys, people, and URLs are fictitious examples. Do not use them as operational references.**

## Run locally
1. Install the backend requirements: `python -m pip install -r requirements.txt`.
2. Initialize or update the database schema from the backend directory: `cd backend` then `python -m app.init_db`.
3. Return to the repository root and start the API and front end: `python -m uvicorn app.main:app --app-dir backend --reload`.
4. Open `http://127.0.0.1:8000/`. The interface and API share an origin; interactive catalog actions require the backend to be running.
5. Create projects, components, tickets and changes, inspect component history, and attach/download files. The theme preference is saved in the browser.

The front end uses plain HTML, CSS and JavaScript. To point it at another API origin, define `window.CVC_API_BASE` before loading `js/app.js`.

## Funciones
- Resumen de proyectos, componentes, tickets y cambios.
- Filtros por proyecto/tipo, búsqueda y detalle con historial de cambios.
- Alta de proyectos (con CustNum entero opcional), componentes (con RefID) y tickets; registro de varios cambios en un ticket; edición de cambios.
- Adjuntar archivos al cambio más reciente de un componente y descargarlos desde su historial.
- Tema claro/oscuro con preferencia guardada en el navegador.

La interfaz consume la API en el mismo origen. Los endpoints de escritura no incluyen autenticación; no publiques el servicio ni cargues información sensible hasta configurar los controles de acceso adecuados.

## Datos de demostración
`POST /catalog/seed-demo` carga el catálogo ficticio y, en cada llamada, crea entre 1 y 15 cambios adicionales con tickets, componentes o proyectos de demostración.

## Pruebas
Ejecuta `python -m pytest backend\tests -q` desde la raíz del repositorio. La suite usa SQLite en memoria y almacenamiento temporal.

## Estructura principal
- `index.html`: interfaz de la aplicación.
- `css/styles.css`: estilos y diseño adaptable.
- `js/app.js`: lógica de interfaz e integración con la API.
- `backend/app/`: endpoints, modelos, esquemas y servicios.
- `backend/tests/`: pruebas automatizadas.
