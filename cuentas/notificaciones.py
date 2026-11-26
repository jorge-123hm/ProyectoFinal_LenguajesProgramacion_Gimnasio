from .models import Notificacion

def notificar(cliente, mensaje):
    """Crea una notificación interna para un cliente."""
    return Notificacion.objects.create(cliente=cliente, mensaje=mensaje)


def notificar_varios(clientes, mensaje):
    """Crea la misma notificación para varios clientes. Devuelve cuántas creó."""
    notificaciones = [Notificacion(cliente=c, mensaje=mensaje) for c in clientes]
    Notificacion.objects.bulk_create(notificaciones)
    return len(notificaciones)