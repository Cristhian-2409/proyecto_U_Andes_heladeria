# Dom Sweet 🍦

Aplicación web de heladería construida con Django, Bootstrap y PostgreSQL en Docker.

## Inicio rápido local

1. Crear y activar el entorno virtual: `python -m venv .venv` y en Windows `.venv\Scripts\Activate.ps1`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar las variables `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT` para el PostgreSQL local.
4. Crear migraciones: `python manage.py makemigrations`
5. Aplicarlas: `python manage.py migrate`
6. Cargar catálogo demo: `python manage.py seed_demo`
7. Ejecutar: `python manage.py runserver`

También puedes crear un administrador con `python manage.py createsuperuser`.

## Docker

La imagen web utiliza `python:3.14.7-slim`.

Ejecuta `docker compose up --build` y abre http://localhost:8000. El servicio web ejecuta migraciones al iniciar y espera a que PostgreSQL esté disponible. El PostgreSQL del contenedor se publica en el puerto `5433` porque el puerto `5432` se reserva para una instalación local de PostgreSQL. Para datos demo: `docker compose exec web python manage.py seed_demo`.

## Roles

- **Administrador**: acceso total y administración Django.
- **Empleado**: CRUD de ingredientes/productos; no ve rentabilidad.
- **Cliente**: catálogo, calorías y compras.
- **Público**: catálogo público.

El registro asigna automáticamente rol Cliente. El comando demo crea `admin / Admin123!` y `empleado / Empleado123!`; cambia estas contraseñas en un entorno real.
