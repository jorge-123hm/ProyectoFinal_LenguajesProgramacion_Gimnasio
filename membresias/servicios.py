from datetime import timedelta

from django.utils import timezone

from cuentas.notificaciones import notificar

from .models import Membresia

# Una membresía vigente solo puede renovarse en sus últimos días
DIAS_RENOVACION_ANTICIPADA = 7


class ReglaDeNegocio(Exception):
    """Se lanza cuando una operación no cumple las reglas del negocio."""


def marcar_vencidas():
    """Pasa a VENCIDA las membresías activas cuya fecha de vencimiento ya pasó."""
    return Membresia.objects.filter(
        estado=Membresia.Estado.ACTIVA,
        fecha_vencimiento__lt=timezone.localdate(),
    ).update(estado=Membresia.Estado.VENCIDA)


def asignar_membresia(cliente, plan, fecha_inicio):
    """CS03: asigna una membresía nueva. El cliente no debe tener otra activa."""
    marcar_vencidas()
    if Membresia.objects.filter(cliente=cliente, estado=Membresia.Estado.ACTIVA).exists():
        raise ReglaDeNegocio(
            'El cliente ya tiene una membresía activa. '
            'Renuévala o cancélala antes de asignar una nueva.'
        )
    membresia = Membresia.objects.create(cliente=cliente, plan=plan, fecha_inicio=fecha_inicio)
    notificar(
        cliente,
        f'Tu membresía {plan.nombre} está activa hasta el {membresia.fecha_vencimiento:%d/%m/%Y}.',
    )
    return membresia


def renovar_membresia(membresia, plan, fecha_inicio):
    """CS04: extiende la vigencia de una membresía activa (por vencer) o vencida."""
    marcar_vencidas()
    membresia.refresh_from_db()

    if membresia.estado == Membresia.Estado.CANCELADA:
        raise ReglaDeNegocio('La membresía está cancelada. Asigna una nueva membresía al cliente.')

    if membresia.estado == Membresia.Estado.VENCIDA:
        if Membresia.objects.filter(
            cliente=membresia.cliente, estado=Membresia.Estado.ACTIVA
        ).exists():
            raise ReglaDeNegocio('El cliente ya tiene una membresía activa.')
    else:
        faltan = (membresia.fecha_vencimiento - timezone.localdate()).days
        if faltan > DIAS_RENOVACION_ANTICIPADA:
            raise ReglaDeNegocio(
                f'La membresía sigue vigente hasta el {membresia.fecha_vencimiento:%d/%m/%Y}. '
                f'No es necesario renovarla todavía (solo en los últimos '
                f'{DIAS_RENOVACION_ANTICIPADA} días).'
            )
        # Renovación anticipada: el nuevo periodo empieza al terminar el actual
        fecha_inicio = max(fecha_inicio, membresia.fecha_vencimiento)

    membresia.plan = plan
    membresia.fecha_inicio = fecha_inicio
    membresia.fecha_vencimiento = fecha_inicio + timedelta(days=plan.duracion_dias)
    membresia.estado = Membresia.Estado.ACTIVA
    membresia.motivo_cancelacion = ''
    membresia.save()
    notificar(
        membresia.cliente,
        f'Tu membresía {plan.nombre} fue renovada hasta el {membresia.fecha_vencimiento:%d/%m/%Y}.',
    )
    return membresia


def cancelar_membresia(membresia, motivo=''):
    """CS05: cancela una membresía activa y guarda el motivo."""
    marcar_vencidas()
    membresia.refresh_from_db()

    if membresia.estado == Membresia.Estado.VENCIDA:
        raise ReglaDeNegocio('La membresía ya está vencida y no puede ser cancelada.')
    if membresia.estado == Membresia.Estado.CANCELADA:
        raise ReglaDeNegocio('La membresía ya está cancelada.')

    membresia.estado = Membresia.Estado.CANCELADA
    membresia.motivo_cancelacion = motivo
    membresia.save(update_fields=['estado', 'motivo_cancelacion'])
    notificar(membresia.cliente, 'Tu membresía fue cancelada. Si fue un error, comunícate con recepción.')
    return membresia