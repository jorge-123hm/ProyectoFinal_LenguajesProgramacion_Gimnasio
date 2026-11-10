from django.contrib import admin
from .models import Cliente, Perfil, Notificacion

admin.site.register(Perfil)
admin.site.register(Cliente)
admin.site.register(Notificacion)