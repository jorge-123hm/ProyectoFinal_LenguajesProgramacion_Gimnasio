# SMART FIT - Sistema de Gestión de Gimnasio

Aplicación web para gestionar un gimnasio: clientes, membresías, pagos y
facturación, entrenamiento personalizado, progreso de los socios, clases
grupales y horarios de entrenadores.

Proyecto desarrollado con **Django (Python)** y **PostgreSQL**.

> **Estado actual:** avance de frontend. Las pantallas de todos los roles están
> terminadas y el inicio de sesión, el registro y el control de acceso por rol
> son funcionales. Los datos que muestran las pantallas son de demostración
> y la conexión con la base de datos se completa en la siguiente fase.

## Funcionalidades

| Módulo | Descripción |
|---|---|
| Autenticación | Inicio de sesión por correo, registro de clientes y cierre de sesión |
| Control de acceso | Cada rol ve solo sus pantallas; el resto queda bloqueado |
| Clientes | Registro, modificación y consulta de socios |
| Membresías | Asignar, renovar y cancelar; planes Básico, Standard y Premium |
| Pagos y facturación | Registro de pagos, facturas y reporte de facturación |
| Entrenamiento | Plan personalizado por cliente y registro de progreso |
| Clases grupales | Programación, calendario semanal y reservas de clientes |
| Horarios | Disponibilidad semanal de los entrenadores |
| Notificaciones | Avisos a los clientes (vencimientos, pagos, comunicados) |

## Roles

| Rol | Pantallas |
|---|---|
| Administrador | Dashboard, usuarios, membresías, plan de entrenamiento, clases, horarios, pagos |
| Recepcionista | Dashboard, clientes, membresías, clases, notificaciones |
| Entrenador | Dashboard, mis clientes, plan de entrenamiento, progreso, mi horario y clases |
| Administrador financiero | Dashboard, pagos, reporte de facturación |
| Cliente | Inicio, membresía, plan, progreso, clases, pagos, notificaciones |

## Tecnologías

- Python 3
- Django 5.2
- PostgreSQL
- HTML, CSS y JavaScript

## Instalación

**1. Clonar el repositorio**
```powershell
git clone https://github.com/jorge-123hm/ProyectoFinal_LenguajesProgramacion_Gimnasio.git
```

**2. Crear y activar el entorno virtual**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**3. Instalar las dependencias**
```powershell
pip install -r requirements.txt
```

**4. Crear la base de datos**

En pgAdmin crea una base de datos vacía llamada `gimnasio_db`.

**5. Configurar las variables de entorno**
```powershell
copy .env.example .env
```
Abre `.env` y completa tus valores:
```
SECRET_KEY=una_clave_secreta_larga
DB_NAME=gimnasio_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_de_postgres
DB_HOST=localhost
DB_PORT=5432
```
Para generar una `SECRET_KEY`:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**6. Crear las tablas**
```powershell
python manage.py migrate
```

**7. Crear el usuario administrador**
```powershell
python manage.py createsuperuser
```
Usa un correo real o de prueba: el inicio de sesión del sistema es por correo.

**8. Ejecutar el servidor**
```powershell
python manage.py runserver
```
Abre http://127.0.0.1:8000/

## Configuración inicial de roles

El sistema asigna las pantallas según el rol del usuario. Para tu primer acceso:

1. Entra a http://127.0.0.1:8000/admin/ con el usuario creado.
2. En **Cuentas → Perfils → Añadir**, elige tu usuario y el rol **Administrador**.
3. Entra a http://127.0.0.1:8000/ con tu **correo** y contraseña.

Para crear usuarios de otros roles (recepcionista, entrenador, financiero),
crea el usuario en **Users** (con correo, nombre y apellido) y luego su **Perfil**
con el rol correspondiente. Los clientes se crean solos desde la pantalla de
**Regístrate aquí**.

## Estructura del proyecto

```
config/          Configuración del proyecto
core/            Interfaz: vistas, rutas, plantillas y estáticos
cuentas/         Perfiles (roles), clientes y notificaciones
membresias/      Planes y membresías
facturacion/     Facturas y pagos
entrenamiento/   Programas, ejercicios, sesiones y progreso
programacion/    Horarios de entrenadores, clases grupales y reservas
database/        Script SQL de la base de datos
docs/            Documentación de la arquitectura
```

Más detalle en [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md).

## Base de datos

El script con la estructura completa está en
[`database/script_bd.sql`](database/script_bd.sql). Para usarlo, ejecútalo en
pgAdmin (Query Tool) sobre una base de datos vacía. En el proyecto, las tablas
se crean con `python manage.py migrate`.

## Documentación

- [Arquitectura del sistema](docs/ARQUITECTURA.md)
- [Script de la base de datos](database/script_bd.sql)

## Próximos pasos

- Conectar las pantallas con la base de datos (guardar, editar y eliminar).
- Generar facturas y actualizar la membresía al registrar un pago.
- Reservas de clases con control de cupos.
- Notificaciones automáticas por vencimiento de membresía.

## Equipo

- Canales Palomino Graciela Luciana
- Saire Flores Guadalupe Dayana
- Huaynalaya Montes Pedro David Jorge

**Curso:** Lenguajes de Programacion · **Docente:** Sardon Paniagua Anibal