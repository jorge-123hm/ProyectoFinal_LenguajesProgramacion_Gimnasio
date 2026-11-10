from django.contrib import admin

from .models import Ejercicio, ProgramaEntrenamiento, ProgresoCliente, SesionEntrenamiento


class EjercicioInline(admin.TabularInline):
    model = Ejercicio
    extra = 1


@admin.register(ProgramaEntrenamiento)
class ProgramaEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cliente", "entrenador", "fecha_inicio", "estado")
    list_filter = ("estado", "entrenador")
    search_fields = ("nombre", "cliente__usuario__first_name", "cliente__usuario__last_name")
    inlines = [EjercicioInline]


@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("programa", "fecha_hora", "duracion_minutos", "estado")
    list_filter = ("estado",)
    search_fields = ("programa__cliente__usuario__username",)


@admin.register(ProgresoCliente)
class ProgresoClienteAdmin(admin.ModelAdmin):
    list_display = ("cliente", "entrenador", "fecha", "peso_kg", "porcentaje_grasa")
    list_filter = ("entrenador",)
    search_fields = ("cliente__usuario__username",)