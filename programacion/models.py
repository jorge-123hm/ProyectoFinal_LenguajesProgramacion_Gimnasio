from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cuentas.models import Cliente


class HorarioEntrenador(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="horarios_disponibles",
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ["entrenador", "dia_semana", "hora_inicio"]

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

    def __str__(self):
        return f"{self.entrenador} - {self.get_dia_semana_display()}"


class ClaseGrupal(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        CANCELADA = "CANCELADA", "Cancelada"
        FINALIZADA = "FINALIZADA", "Finalizada"

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="clases_grupales",
    )
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=60)
    capacidad_maxima = models.PositiveIntegerField(default=15)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )

    class Meta:
        ordering = ["fecha_hora"]

    @property
    def cupos_disponibles(self):
        reservas_confirmadas = self.reservas.filter(
            estado=ReservaClase.Estado.CONFIRMADA
        ).count()
        return self.capacidad_maxima - reservas_confirmadas

    def __str__(self):
        return f"{self.nombre} - {self.fecha_hora:%d/%m/%Y %H:%M}"


class ReservaClase(models.Model):
    class Estado(models.TextChoices):
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        CANCELADA = "CANCELADA", "Cancelada"
        ASISTIO = "ASISTIO", "Asistió"
        FALTO = "FALTO", "Faltó"

    clase = models.ForeignKey(
        ClaseGrupal,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="reservas_clases",
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.CONFIRMADA,
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("clase", "cliente")
        ordering = ["-creada_en"]

    def clean(self):
        if (
            self.estado == self.Estado.CONFIRMADA
            and not self.pk
            and self.clase.cupos_disponibles <= 0
        ):
            raise ValidationError("No hay cupos disponibles para esta clase.")

    def __str__(self):
        return f"{self.cliente} - {self.clase}"