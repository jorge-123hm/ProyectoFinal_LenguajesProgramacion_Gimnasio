from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from cuentas.models import Notificacion, Perfil
from membresias.models import Membresia
from membresias.servicios import ReglaDeNegocio, marcar_vencidas

from .models import ClaseGrupal, HorarioEntrenador, ReservaClase

User = get_user_model()

DURACION_MINIMA = 15
DURACION_MAXIMA = 240
CAPACIDAD_MAXIMA = 100


def entrenadores():
    """Usuarios activos con rol Entrenador."""
    return (User.objects
            .filter(perfil__rol=Perfil.Rol.ENTRENADOR, is_active=True)
            .order_by('last_name', 'first_name', 'username'))


def marcar_finalizadas():
    """Pasa a FINALIZADA las clases programadas que ya terminaron."""
    ahora = timezone.now()
    candidatas = ClaseGrupal.objects.filter(
        estado=ClaseGrupal.Estado.PROGRAMADA, fecha_hora__lt=ahora
    )
    ids = [
        c.pk for c in candidatas
        if c.fecha_hora + timedelta(minutes=c.duracion_minutos) < ahora
    ]
    if ids:
        ClaseGrupal.objects.filter(pk__in=ids).update(estado=ClaseGrupal.Estado.FINALIZADA)
    return len(ids)


def _notificar(clientes, mensaje):
    Notificacion.objects.bulk_create(
        [Notificacion(cliente=c, mensaje=mensaje) for c in clientes]
    )


# ---------------------------------------------------------------------
#  Horarios de los entrenadores
# ---------------------------------------------------------------------

def _validar_horario(entrenador, dia, inicio, fin, excluir=None):
    if not Perfil.objects.filter(usuario=entrenador, rol=Perfil.Rol.ENTRENADOR).exists():
        raise ReglaDeNegocio('El usuario seleccionado no es un entrenador.')
    if dia not in HorarioEntrenador.DiaSemana.values:
        raise ReglaDeNegocio('El día seleccionado no es válido.')
    if inicio >= fin:
        raise ReglaDeNegocio('La hora de inicio debe ser anterior a la hora de fin.')
    cruces = HorarioEntrenador.objects.filter(
        entrenador=entrenador, dia_semana=dia, hora_inicio__lt=fin, hora_fin__gt=inicio
    )
    if excluir is not None:
        cruces = cruces.exclude(pk=excluir.pk)
    if cruces.exists():
        raise ReglaDeNegocio('El horario se cruza con otro ya registrado para ese entrenador y día.')


def agregar_horario(entrenador, dia, inicio, fin):
    _validar_horario(entrenador, dia, inicio, fin)
    return HorarioEntrenador.objects.create(
        entrenador=entrenador, dia_semana=dia, hora_inicio=inicio, hora_fin=fin
    )


def modificar_horario(horario, entrenador, dia, inicio, fin):
    _validar_horario(entrenador, dia, inicio, fin, excluir=horario)
    horario.entrenador = entrenador
    horario.dia_semana = dia
    horario.hora_inicio = inicio
    horario.hora_fin = fin
    horario.save()
    return horario


# ---------------------------------------------------------------------
#  Clases grupales
# ---------------------------------------------------------------------

def _validar_clase(nombre, entrenador, inicio, duracion, capacidad, excluir=None):
    """Verifica que el horario y la capacidad estén disponibles (CS de clases grupales)."""
    if not nombre:
        raise ReglaDeNegocio('Escribe el nombre de la clase.')
    if len(nombre) > 120:
        raise ReglaDeNegocio('El nombre de la clase no puede pasar de 120 caracteres.')
    if not Perfil.objects.filter(usuario=entrenador, rol=Perfil.Rol.ENTRENADOR).exists():
        raise ReglaDeNegocio('El usuario seleccionado no es un entrenador.')
    if not DURACION_MINIMA <= duracion <= DURACION_MAXIMA:
        raise ReglaDeNegocio(
            f'La duración debe estar entre {DURACION_MINIMA} y {DURACION_MAXIMA} minutos.'
        )
    if not 1 <= capacidad <= CAPACIDAD_MAXIMA:
        raise ReglaDeNegocio(f'La capacidad debe estar entre 1 y {CAPACIDAD_MAXIMA} personas.')
    if inicio <= timezone.now():
        raise ReglaDeNegocio('La clase debe programarse en una fecha y hora futuras.')

    local = timezone.localtime(inicio)
    fin = local + timedelta(minutes=duracion)
    if fin.date() != local.date():
        raise ReglaDeNegocio('La clase debe terminar el mismo día en que empieza.')

    # El entrenador debe tener horario disponible que cubra toda la clase
    cubierto = HorarioEntrenador.objects.filter(
        entrenador=entrenador,
        dia_semana=local.weekday(),
        hora_inicio__lte=local.time(),
        hora_fin__gte=fin.time(),
    ).exists()
    if not cubierto:
        raise ReglaDeNegocio(
            'El entrenador no tiene horario disponible en ese día y hora. '
            'Revisa la sección Horarios o elige otro horario.'
        )

    # No puede dictar dos clases a la vez
    cercanas = ClaseGrupal.objects.filter(
        entrenador=entrenador,
        estado=ClaseGrupal.Estado.PROGRAMADA,
        fecha_hora__lt=inicio + timedelta(minutes=duracion),
        fecha_hora__gt=inicio - timedelta(minutes=DURACION_MAXIMA),
    )
    if excluir is not None:
        cercanas = cercanas.exclude(pk=excluir.pk)
    for otra in cercanas:
        if otra.fecha_hora + timedelta(minutes=otra.duracion_minutos) > inicio:
            raise ReglaDeNegocio(
                f'El entrenador ya tiene la clase «{otra.nombre}» en ese horario.'
            )


def programar_clase(nombre, descripcion, entrenador, inicio, duracion, capacidad):
    _validar_clase(nombre, entrenador, inicio, duracion, capacidad)
    return ClaseGrupal.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        entrenador=entrenador,
        fecha_hora=inicio,
        duracion_minutos=duracion,
        capacidad_maxima=capacidad,
    )


@transaction.atomic
def modificar_clase(clase, nombre, descripcion, entrenador, inicio, duracion, capacidad):
    if clase.estado != ClaseGrupal.Estado.PROGRAMADA:
        raise ReglaDeNegocio('Solo se pueden modificar las clases programadas.')
    _validar_clase(nombre, entrenador, inicio, duracion, capacidad, excluir=clase)

    reservas = list(
        clase.reservas.filter(estado=ReservaClase.Estado.CONFIRMADA).select_related('cliente')
    )
    if capacidad < len(reservas):
        raise ReglaDeNegocio(
            f'La capacidad no puede ser menor que los {len(reservas)} clientes ya inscritos.'
        )

    cambio_horario = clase.fecha_hora != inicio or clase.entrenador_id != entrenador.pk
    clase.nombre = nombre
    clase.descripcion = descripcion
    clase.entrenador = entrenador
    clase.fecha_hora = inicio
    clase.duracion_minutos = duracion
    clase.capacidad_maxima = capacidad
    clase.save()

    if cambio_horario and reservas:
        local = timezone.localtime(inicio)
        _notificar(
            [r.cliente for r in reservas],
            f'La clase «{nombre}» cambió: ahora será el {local:%d/%m/%Y} a las {local:%H:%M}.',
        )
    return clase


@transaction.atomic
def cancelar_clase(clase):
    """Cancela la clase y avisa a los clientes inscritos. Devuelve cuántos fueron avisados."""
    if clase.estado != ClaseGrupal.Estado.PROGRAMADA:
        raise ReglaDeNegocio('Solo se pueden cancelar las clases programadas.')

    reservas = list(
        clase.reservas.filter(estado=ReservaClase.Estado.CONFIRMADA).select_related('cliente')
    )
    clase.estado = ClaseGrupal.Estado.CANCELADA
    clase.save(update_fields=['estado'])

    if reservas:
        local = timezone.localtime(clase.fecha_hora)
        _notificar(
            [r.cliente for r in reservas],
            f'La clase «{clase.nombre}» del {local:%d/%m/%Y} a las {local:%H:%M} fue cancelada.',
        )
        ReservaClase.objects.filter(pk__in=[r.pk for r in reservas]).update(
            estado=ReservaClase.Estado.CANCELADA
        )
    return len(reservas)


# ---------------------------------------------------------------------
#  Reservas de los clientes
# ---------------------------------------------------------------------

@transaction.atomic
def reservar_clase(cliente, clase_id):
    marcar_vencidas()
    marcar_finalizadas()
    try:
        # Se bloquea la fila de la clase para no sobrepasar la capacidad
        clase = ClaseGrupal.objects.select_for_update().get(pk=clase_id)
    except (ClaseGrupal.DoesNotExist, ValueError, TypeError):
        raise ReglaDeNegocio('La clase seleccionada no existe.')

    if clase.estado != ClaseGrupal.Estado.PROGRAMADA or clase.fecha_hora <= timezone.now():
        raise ReglaDeNegocio('La clase ya no está disponible para reservas.')
    if not Membresia.objects.filter(cliente=cliente, estado=Membresia.Estado.ACTIVA).exists():
        raise ReglaDeNegocio('Necesitas una membresía activa para reservar clases.')

    reserva = ReservaClase.objects.filter(clase=clase, cliente=cliente).first()
    if reserva and reserva.estado == ReservaClase.Estado.CONFIRMADA:
        raise ReglaDeNegocio('Ya tienes una reserva en esta clase.')
    if clase.cupos_disponibles <= 0:
        raise ReglaDeNegocio('La clase no tiene cupos disponibles.')

    if reserva:
        reserva.estado = ReservaClase.Estado.CONFIRMADA
        reserva.save(update_fields=['estado'])
    else:
        ReservaClase.objects.create(clase=clase, cliente=cliente)
    return clase


def cancelar_reserva(cliente, clase_id):
    try:
        reserva = (ReservaClase.objects
                   .select_related('clase')
                   .filter(clase_id=clase_id, cliente=cliente,
                           estado=ReservaClase.Estado.CONFIRMADA)
                   .first())
    except (ValueError, TypeError):
        reserva = None
    if reserva is None:
        raise ReglaDeNegocio('No tienes una reserva activa en esa clase.')
    if reserva.clase.fecha_hora <= timezone.now():
        raise ReglaDeNegocio('La clase ya comenzó; no se puede cancelar la reserva.')
    reserva.estado = ReservaClase.Estado.CANCELADA
    reserva.save(update_fields=['estado'])
    return reserva.clase
