from datetime import timedelta

from django.db import models
from django.utils import timezone

from cuentas.models import Cliente


class PlanMembresia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    duracion_dias = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Membresia(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        VENCIDA = "VENCIDA", "Vencida"
        CANCELADA = "CANCELADA", "Cancelada"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="membresias",
    )
    plan = models.ForeignKey(
        PlanMembresia,
        on_delete=models.PROTECT,
        related_name="membresias",
    )
    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_vencimiento = models.DateField(blank=True)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.ACTIVA,
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = (
                self.fecha_inicio + timedelta(days=self.plan.duracion_dias)
            )
        super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        return (
            self.estado == self.Estado.ACTIVA
            and self.fecha_vencimiento >= timezone.localdate()
        )

    def __str__(self):
        return f"{self.cliente} - {self.plan}"