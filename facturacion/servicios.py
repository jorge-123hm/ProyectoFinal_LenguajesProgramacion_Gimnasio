from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from cuentas.notificaciones import notificar
from membresias.models import Membresia
from membresias.servicios import ReglaDeNegocio

from .models import Factura, Pago


def membresia_de_referencia(cliente):
    """Membresía a la que se asocia un pago: la activa más reciente o,
    si no hay, la última que no esté cancelada."""
    membresias = Membresia.objects.filter(cliente=cliente)
    activa = (membresias
            .filter(estado=Membresia.Estado.ACTIVA)
            .order_by('-fecha_vencimiento')
            .first())
    if activa:
        return activa
    return (membresias
            .exclude(estado=Membresia.Estado.CANCELADA)
            .order_by('-fecha_vencimiento')
            .first())


@transaction.atomic
def registrar_pago(cliente, monto, fecha, metodo, concepto):
    """CS09: registra un pago y emite su factura (queda PAGADA)."""
    if monto <= 0:
        raise ReglaDeNegocio('El monto debe ser mayor que cero.')
    if fecha > timezone.localdate():
        raise ReglaDeNegocio('La fecha del pago no puede ser futura.')
    if metodo not in Pago.Metodo.values:
        raise ReglaDeNegocio('El método de pago no es válido.')

    membresia = None
    if concepto == 'membresia':
        membresia = membresia_de_referencia(cliente)
        if membresia is None:
            raise ReglaDeNegocio(
                'El cliente no tiene una membresía registrada. '
                'Asígnala primero en la sección Membresías.'
            )

    factura = Factura.objects.create(
        cliente=cliente,
        membresia=membresia,
        fecha_emision=fecha,
        subtotal=monto,
        impuesto=Decimal('0'),
        estado=Factura.Estado.PAGADA,
    )
    momento = timezone.make_aware(datetime.combine(fecha, timezone.localtime().time()))
    Pago.objects.create(factura=factura, fecha_pago=momento, monto=monto, metodo=metodo)
    notificar(cliente, f'Registramos tu pago de S/. {monto:.2f}. Factura {factura.numero}.')
    return factura

def anular_factura(numero):
    """Anula una factura. El historial de pagos se conserva."""
    try:
        factura = Factura.objects.get(numero=numero)
    except Factura.DoesNotExist:
        raise ReglaDeNegocio('La factura seleccionada no existe.')
    if factura.estado == Factura.Estado.ANULADA:
        raise ReglaDeNegocio('La factura ya está anulada.')
    factura.estado = Factura.Estado.ANULADA
    factura.save(update_fields=['estado'])
    return factura