# Arquitectura del sistema SMART FIT

Sistema web de gestión de gimnasio desarrollado con **Django (Python)** y
**PostgreSQL**. Sigue el patrón **MVC** (en Django: Modelo – Vista – Plantilla),
organizado en capas y en paquetes (apps) por funcionalidad.

## 1. Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3 |
| Framework web | Django 5.2 |
| Base de datos | PostgreSQL |
| Interfaz | HTML, CSS y JavaScript (sin librerías externas) |
| Autenticación | Sistema de usuarios de Django con perfiles por rol |

## 2. Estructura de carpetas

```
Gimnasio/
├── manage.py
├── requirements.txt
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
│
├── config/                      # Configuración del proyecto
│   ├── settings.py              # Apps, base de datos, idioma, plantillas
│   ├── urls.py                  # Rutas principales
│   ├── wsgi.py
│   └── asgi.py
│
├── cuentas/                     # PAQUETE: Gestión de clientes y usuarios
│   ├── models.py                # Perfil (rol), Cliente, Notificacion
│   ├── admin.py
│   └── migrations/
│
├── membresias/                  # PAQUETE: Gestión de membresías
│   ├── models.py                # PlanMembresia, Membresia
│   ├── admin.py
│   └── migrations/
│
├── facturacion/                 # PAQUETE: Facturación y pagos
│   ├── models.py                # Factura, Pago
│   ├── admin.py
│   └── migrations/
│
├── entrenamiento/               # PAQUETE: Entrenamiento personalizado
│   ├── models.py                # ProgramaEntrenamiento, Ejercicio,
│   │                            # SesionEntrenamiento, ProgresoCliente
│   ├── admin.py
│   └── migrations/
│
├── programacion/                # PAQUETE: Clases grupales y horarios
│   ├── models.py                # HorarioEntrenador, ClaseGrupal, ReservaClase
│   ├── admin.py
│   └── migrations/
│
├── core/                        # PAQUETE: Presentación y control (interfaz)
│   ├── views.py                 # Vistas (controladores) de todas las pantallas
│   ├── urls.py                  # Rutas de la aplicación
│   ├── mixins.py                # Control de acceso por rol
│   ├── roles.py                 # Roles y pantalla de inicio por rol
│   ├── menus.py                 # Menú lateral según el rol
│   ├── context_processors.py    # Datos del usuario para las plantillas
│   ├── templates/core/          # Plantillas HTML (vistas)
│   │   ├── base_panel.html      # Plantilla base del panel
│   │   ├── login.html, registro.html
│   │   ├── dashboard.html, dashboard_entrenador.html
│   │   ├── usuarios.html, membresias.html, pagos.html,
│   │   │   reporte_facturacion.html, notificaciones.html
│   │   ├── clases_grupales.html, horarios_entrenadores.html
│   │   ├── plan_entrenamiento.html, progreso.html,
│   │   │   entrenador_clientes.html, mi_agenda.html
│   │   └── inicio_cliente.html, mi_membresia.html, mi_plan.html,
│   │       mi_progreso.html, mis_pagos.html, mis_notificaciones.html,
│   │       clases_cliente.html
│   └── static/core/             # Archivos estáticos
│       ├── css/                 # dashboard.css, login.css, panel.css
│       ├── js/                  # panel.js
│       └── img/                 # Logo e iconos
│
├── database/
│   └── script_bd.sql            # Script de la base de datos (PostgreSQL)
│
└── docs/
    └── ARQUITECTURA.md          # la arquitectura (esta misma)
```

## 3. Paquetes y responsabilidades

| Paquete | Responsabilidad | Entidades |
|---|---|---|
| `cuentas` | Registro y datos de clientes, roles de usuario, notificaciones | Perfil, Cliente, Notificacion |
| `membresias` | Planes y membresías de los clientes | PlanMembresia, Membresia |
| `facturacion` | Facturas y pagos | Factura, Pago |
| `entrenamiento` | Programas personalizados, ejercicios, sesiones y progreso | ProgramaEntrenamiento, Ejercicio, SesionEntrenamiento, ProgresoCliente |
| `programacion` | Horarios de entrenadores y clases grupales con reservas | HorarioEntrenador, ClaseGrupal, ReservaClase |
| `core` | Interfaz de usuario, rutas, control de acceso por rol | (no define entidades) |

## 4. Capas

```
┌──────────────────────────────────────────────────────────┐
│ CAPA DE PRESENTACIÓN   core/templates + core/static      │
│ (Vista: HTML, CSS, JS)                                   │
└──────────────────────────┬───────────────────────────────┘
                           │ solicitudes HTTP
┌──────────────────────────▼───────────────────────────────┐
│ CAPA CONTROLADORA      core/urls.py + core/views.py      │
│ (Controlador)          core/mixins.py  (permisos por rol)│
└──────────────────────────┬───────────────────────────────┘
                           │ ORM de Django
┌──────────────────────────▼───────────────────────────────┐
│ CAPA DE NEGOCIO Y DATOS  cuentas · membresias ·          │
│ (Modelo)                 facturacion · entrenamiento ·   │
│                          programacion  (models.py)       │
└──────────────────────────┬───────────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │   PostgreSQL    │
                  └─────────────────┘
```

## 5. Dependencias entre paquetes

```
core ──► cuentas, membresias, facturacion, entrenamiento, programacion
facturacion   ──► membresias, cuentas
membresias    ──► cuentas
entrenamiento ──► cuentas
programacion  ──► cuentas
cuentas       ──► (solo el sistema de usuarios de Django)
```

`cuentas` es la base del sistema y no depende de ningún otro paquete propio.

## 6. Roles y acceso

| Rol | Pantallas principales |
|---|---|
| Administrador | Dashboard, usuarios, membresías, plan de entrenamiento, clases, horarios, pagos |
| Recepcionista | Dashboard, clientes, membresías, clases, notificaciones |
| Entrenador | Dashboard, mis clientes, plan de entrenamiento, progreso, mi horario y clases |
| Administrador financiero | Dashboard, pagos, reporte de facturación |
| Cliente | Inicio, membresía, plan, progreso, clases, pagos, notificaciones |

El acceso a cada pantalla se controla con `RolRequeridoMixin` (`core/mixins.py`):
si el rol no está permitido, se redirige al inicio del usuario con un mensaje.

## 7. Estado del proyecto

- **Completo:** modelos y migraciones, autenticación y control de acceso por rol,
  y todas las pantallas conectadas a la base de datos: clientes, membresías, pagos
  y facturas, plan de entrenamiento y progreso, clases grupales, horarios,
  notificaciones y dashboards.