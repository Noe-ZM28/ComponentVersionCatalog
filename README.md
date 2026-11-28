# Component Version Catalog — Prototype v0.1

## What this is
A browser-based front end for consulting projects, components, tickets, change history, and associated files through the FastAPI backend.

**All records, version numbers, ticket keys, people, and URLs are fictitious examples. Do not use them as operational references.**

## Ejecución local en Windows

### 1. Crear el entorno virtual e instalar dependencias

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell no permite activar el entorno, ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a ejecutar el comando de activación.

### 2. Configurar SQL Server

Copia el archivo de ejemplo y configura las variables de conexión:

```powershell
Copy-Item .env.example .env
```

Define al menos `DATABASE_URL` con una cadena de conexión de SQLAlchemy para SQL Server. Puedes usar SQL Server autenticado por Windows o por usuario y contraseña. Ejemplo para autenticación por Windows:

```env
DATABASE_URL="mssql+mssqlpython://@SERVIDOR/NOMBRE_BASE?trusted_connection=yes&encrypt=yes&trust_server_certificate=yes"
EXTERNAL_DATABASE_URL="mssql+mssqlpython://@SERVIDOR/OTRA_BASE?trusted_connection=yes&encrypt=yes&trust_server_certificate=yes"
STORAGE_PATH="storage/files"
```

La aplicación lee el archivo `.env` desde la raíz del repositorio.

### 3. Generar las tablas

Desde la raíz del repositorio ejecuta:

```powershell
cd backend
python -m app.init_db
cd ..
```

Este comando usa los modelos de SQLAlchemy y crea las tablas que todavía no existen; se puede volver a ejecutar de forma segura.

### 4. Ejecutar el proyecto

Desde la raíz del repositorio inicia FastAPI y el front end:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

Abre `http://127.0.0.1:8000/`. Comprueba el estado del backend en `http://127.0.0.1:8000/health`.

El front end usa HTML, CSS y JavaScript y se sirve desde el mismo origen que la API. Para detener el servidor presiona `Ctrl+C`.

The front end uses plain HTML, CSS and JavaScript. To point it at another API origin, define `window.CVC_API_BASE` before loading `js/app.js`.

## Funciones
- Resumen de proyectos, componentes, tickets y cambios.
- Filtros por proyecto/tipo, búsqueda y detalle con historial de cambios.
- Alta de proyectos (con CustNum entero opcional), componentes (con RefID y tipo de componente enum) y tickets; registro de varios cambios en un ticket; edición de cambios.
- Adjuntar archivos al cambio más reciente de un componente y descargarlos desde su historial.
- Tema claro/oscuro con preferencia guardada en el navegador.

La interfaz consume la API en el mismo origen. Los endpoints de escritura no incluyen autenticación; no publiques el servicio ni cargues información sensible hasta configurar los controles de acceso adecuados.

## Datos de demostración
`POST /catalog/seed-demo` carga el catálogo ficticio y, en cada llamada, crea información adicional de demostración con proyectos, componentes y tickets. Cada ticket generado contiene entre 2 y 15 componentes asociados a cambios del mismo proyecto.

## Pruebas
Configura `TEST_DATABASE_URL` en `.env` con una base de pruebas desechable de SQL Server y ejecuta `python -m pytest backend\tests -q` desde la raíz del repositorio. La suite crea y elimina sus tablas en esa base.

## Estructura principal
- `index.html`: interfaz de la aplicación.
- `css/styles.css`: estilos y diseño adaptable.
- `js/app.js`: lógica de interfaz e integración con la API.
- `backend/app/`: endpoints, modelos, esquemas y servicios.
- `backend/tests/`: pruebas automatizadas.
