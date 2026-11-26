from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from cuentas.models import Perfil
from membresias.models import Membresia
from membresias.servicios import ReglaDeNegocio, marcar_vencidas

from .models import ProgramaEntrenamiento, ProgresoCliente

User = get_user_model()

# Programas que se pueden asignar (catálogo del gimnasio)
PROGRAMAS = [
    'Programa de Fuerza',
    'Programa de Resistencia',
    'Programa de Hipertrofia',
    'Programa de Pérdida de Peso',
    'Programa de Flexibilidad',
]


def entrenador_disponible():
    """El entrenador activo con menos programas en curso."""
    return (User.objects
            .filter(perfil__rol=Perfil.Rol.ENTRENADOR, is_active=True)
            .annotate(carga=Count(
                'programas_asignados',
                filter=Q(programas_asignados__estado=ProgramaEntrenamiento.Estado.ACTIVO),
            ))
            .order_by('carga', 'last_name', 'first_name')
            .first())


def _validar_plan(nombre, objetivo, capacidades, frecuencia):
    if nombre not in PROGRAMAS:
        raise ReglaDeNegocio('El programa seleccionado no es válido.')
    if not objetivo or not capacidades:
        raise ReglaDeNegocio('Completa los objetivos y las capacidades físicas del cliente.')
    if not 1 <= frecuencia <= 7:
        raise ReglaDeNegocio('La frecuencia debe estar entre 1 y 7 días por semana.')


def asignar_programa(cliente, entrenador, nombre, objetivo, capacidades, frecuencia):
    """CS06: asigna un programa personalizado. Si no se indica entrenador, el sistema
    mantiene el del cliente o elige al entrenador disponible."""
    _validar_plan(nombre, objetivo, capacidades, frecuencia)

    marcar_vencidas()
    if not Membresia.objects.filter(cliente=cliente, estado=Membresia.Estado.ACTIVA).exists():
        raise ReglaDeNegocio(
            'El cliente no tiene una membresía activa. '
            'Asígnale una membresía antes de asignar un programa.'
        )

    activos = cliente.programas_entrenamiento.filter(estado=ProgramaEntrenamiento.Estado.ACTIVO)

    if entrenador is None:
        previo = activos.select_related('entrenador').first()
        entrenador = previo.entrenador if previo else entrenador_disponible()
        if entrenador is None:
            raise ReglaDeNegocio(
                'No hay entrenadores disponibles. Crea un usuario con el rol Entrenador.'
            )

    with transaction.atomic():
        # El programa anterior queda en el historial del cliente
        activos.update(
            estado=ProgramaEntrenamiento.Estado.FINALIZADO,
            fecha_fin=timezone.localdate(),
        )
        return ProgramaEntrenamiento.objects.create(
            cliente=cliente,
            entrenador=entrenador,
            nombre=nombre,
            objetivo=objetivo,
            capacidades=capacidades,
            frecuencia=frecuencia,
        )


def modificar_programa(programa, nombre, objetivo, capacidades, frecuencia):
    """CS08: modifica el programa vigente de un cliente."""
    _validar_plan(nombre, objetivo, capacidades, frecuencia)
    if programa.estado != ProgramaEntrenamiento.Estado.ACTIVO:
        raise ReglaDeNegocio('El plan ya no está activo y no se puede modificar.')
    programa.nombre = nombre
    programa.objetivo = objetivo
    programa.capacidades = capacidades
    programa.frecuencia = frecuencia
    programa.save()
    return programa


def registrar_progreso(cliente, entrenador, fecha, peso, repeticiones, comentario):
    """CS07: registra el progreso de un cliente que tenga un programa en curso."""
    if not cliente.programas_entrenamiento.filter(
        estado=ProgramaEntrenamiento.Estado.ACTIVO
    ).exists():
        raise ReglaDeNegocio(
            'El cliente no tiene un programa asignado. '
            'Primero asígnale uno en Plan de Entrenamiento.'
        )
    if fecha > timezone.localdate():
        raise ReglaDeNegocio('La fecha del registro no puede ser futura.')
    return ProgresoCliente.objects.create(
        cliente=cliente,
        entrenador=entrenador,
        fecha=fecha,
        peso_levantado=peso,
        repeticiones=repeticiones,
        observaciones=comentario,
    )


def editar_progreso(registro, fecha, peso, repeticiones, comentario):
    if fecha > timezone.localdate():
        raise ReglaDeNegocio('La fecha del registro no puede ser futura.')
    registro.fecha = fecha
    registro.peso_levantado = peso
    registro.repeticiones = repeticiones
    registro.observaciones = comentario
    registro.save()
    return registro