from django.conf import settings
from django.db import models
from django.utils import timezone

from cuentas.models import Cliente


class ProgramaEntrenamiento(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        FINALIZADO = "FINALIZADO", "Finalizado"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="programas_entrenamiento",
    )
    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="programas_asignados",
    )
    nombre = models.CharField(max_length=120)
    objetivo = models.TextField()
    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.cliente}"


class Ejercicio(models.Model):
    programa = models.ForeignKey(
        ProgramaEntrenamiento,
        on_delete=models.CASCADE,
        related_name="ejercicios",
    )
    nombre = models.CharField(max_length=120)
    series = models.PositiveIntegerField(default=3)
    repeticiones = models.CharField(
        max_length=30,
        help_text="Ejemplo: 12, 8-10 o hasta el fallo",
    )
    peso_recomendado = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kilogramos",
    )
    descanso_segundos = models.PositiveIntegerField(default=60)
    orden = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["orden"]
        unique_together = ("programa", "orden")

    def __str__(self):
        return f"{self.orden}. {self.nombre}"


class SesionEntrenamiento(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"

    programa = models.ForeignKey(
        ProgramaEntrenamiento,
        on_delete=models.PROTECT,
        related_name="sesiones",
    )
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=60)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    notas_entrenador = models.TextField(blank=True)

    class Meta:
        ordering = ["fecha_hora"]

    def __str__(self):
        return f"Sesión: {self.programa.cliente} - {self.fecha_hora:%d/%m/%Y %H:%M}"


class ProgresoCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="progresos",
    )
    entrenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="progresos_registrados",
    )
    fecha = models.DateField(default=timezone.localdate)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    porcentaje_grasa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    medida_pecho_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    medida_cintura_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    peso_levantado = models.DecimalField(
        max_digits=6, 
        decimal_places=1, 
        null=True, blank=True
    )
    repeticiones = models.PositiveIntegerField(
        null=True, 
        blank=True
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Progreso de {self.cliente} - {self.fecha}"