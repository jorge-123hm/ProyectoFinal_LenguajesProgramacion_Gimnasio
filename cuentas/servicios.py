from datetime import timedelta

from django.utils import timezone

from membresias.models import Membresia
from membresias.servicios import DIAS_RENOVACION_ANTICIPADA, ReglaDeNegocio, marcar_vencidas

from .models import Cliente
from .notificaciones import notificar_varios

LONGITUD_MAXIMA = 300

# Grupos de destinatarios que ofrece la pantalla de Notificaciones
GRUPOS = ('todos', 'por_vencer', 'vencidas')


def clientes_del_grupo(grupo):
    """Clientes activos que pertenecen a un grupo de destinatarios."""
    marcar_vencidas()
    clientes = Cliente.objects.filter(activo=True)

    if grupo == 'todos':
        return clientes

    if grupo == 'por_vencer':
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=DIAS_RENOVACION_ANTICIPADA)
        return clientes.filter(
            membresias__estado=Membresia.Estado.ACTIVA,
            membresias__fecha_vencimiento__gte=hoy,
            membresias__fecha_vencimiento__lte=limite,
        ).distinct()

    if grupo == 'vencidas':
        return (clientes
                .filter(membresias__estado=Membresia.Estado.VENCIDA)
                .exclude(membresias__estado=Membresia.Estado.ACTIVA)
                .distinct())

    raise ReglaDeNegocio('El grupo de destinatarios no es válido.')


def enviar_notificacion(clientes, mensaje):
    """CS11: envía un mensaje a uno o varios clientes. Devuelve cuántos lo recibieron."""
    mensaje = mensaje.strip()
    if not mensaje:
        raise ReglaDeNegocio('Escribe el mensaje de la notificación.')
    if len(mensaje) > LONGITUD_MAXIMA:
        raise ReglaDeNegocio(f'El mensaje no puede pasar de {LONGITUD_MAXIMA} caracteres.')

    clientes = list(clientes)
    if not clientes:
        raise ReglaDeNegocio('No hay clientes que cumplan ese criterio.')
    return notificar_varios(clientes, mensaje)