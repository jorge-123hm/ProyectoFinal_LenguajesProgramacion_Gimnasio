from django.conf import settings
from django.db import models


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        RECEPCIONISTA = "RECEPCION", "Recepcionista"
        ENTRENADOR = "ENTRENADOR", "Entrenador"
        FINANCIERO = "FINANCIERO", "Administrador financiero"
        CLIENTE = "CLIENTE", "Cliente"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(max_length=15, choices=Rol.choices)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.get_rol_display()}"


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cliente",
    )
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username
    
class Notificacion(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"Notificación para {self.cliente} - {self.fecha_envio:%d/%m/%Y}"