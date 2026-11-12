from .roles import ADMIN, CLIENTE, ENTRENADOR, FINANCIERO, RECEPCION

# (texto del menú, nombre de la url)
MENUS = {
    ADMIN: [
        ('Dashboard', 'dashboard'),
        ('Usuarios', 'usuarios'),
        ('Membresía', 'membresias'),
        ('Plan de Entrenamiento', 'plan_entrenamiento'),
        ('Clases Grupales', 'clases_grupales'),
        ('Horarios', 'horarios_entrenadores'),
        ('Pagos', 'pagos'),
    ],
    RECEPCION: [
        ('Dashboard', 'dashboard'),
        ('Clientes', 'usuarios'),
        ('Membresías', 'membresias'),
        ('Clases Grupales', 'clases_grupales'),
        ('Notificaciones', 'notificaciones'),
    ],
    ENTRENADOR: [
        ('Dashboard', 'dashboard_entrenador'),
        ('Usuario', 'entrenador_clientes'),
        ('Plan de Entrenamiento', 'plan_entrenamiento'),
        ('Progreso', 'progreso'),
        ('Mi Horario y Clases', 'mi_agenda'),
    ],
    FINANCIERO: [
        ('Dashboard', 'dashboard'),
        ('Pagos', 'pagos'),
        ('Reportes', 'reporte_facturacion'),
    ],
    CLIENTE: [
        ('Inicio', 'inicio_cliente'),
        ('Mi Membresía', 'mi_membresia'),
        ('Mi Plan', 'mi_plan'),
        ('Mi Progreso', 'mi_progreso'),
        ('Clases Grupales', 'clases_cliente'),
        ('Mis Pagos', 'mis_pagos'),
        ('Notificaciones', 'mis_notificaciones'),
    ],
}


def menu_de(rol):
    return [{'nombre': nombre, 'url': url} for nombre, url in MENUS.get(rol, [])]
