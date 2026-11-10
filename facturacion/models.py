from django.db import models
from django.utils import timezone

from cuentas.models import Cliente
from membresias.models import Membresia


class Factura(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADA = "PAGADA", "Pagada"
        ANULADA = "ANULADA", "Anulada"

    numero = models.CharField(max_length=30, unique=True, blank=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="facturas",
    )
    membresia = models.ForeignKey(
        Membresia,
        on_delete=models.PROTECT,
        related_name="facturas",
        null=True,
        blank=True,
    )
    fecha_emision = models.DateField(default=timezone.localdate)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    def save(self, *args, **kwargs):
        self.total = self.subtotal + self.impuesto

        if not self.numero:
            super().save(*args, **kwargs)
            self.numero = f"FAC-{timezone.now():%Y}-{self.pk:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero or "Factura sin número"


class Pago(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        YAPE_PLIN = "YAPE_PLIN", "Yape/Plin"

    factura = models.ForeignKey(
        Factura,
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    fecha_pago = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    referencia = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Pago de {self.monto} - {self.factura.numero}"