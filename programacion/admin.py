from django.contrib import admin

from .models import ClaseGrupal, HorarioEntrenador, ReservaClase


@admin.register(HorarioEntrenador)
class HorarioEntrenadorAdmin(admin.ModelAdmin):
    list_display = ("entrenador", "dia_semana", "hora_inicio", "hora_fin")
    list_filter = ("dia_semana", "entrenador")


@admin.register(ClaseGrupal)
class ClaseGrupalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "entrenador",
        "fecha_hora",
        "capacidad_maxima",
        "cupos_disponibles",
        "estado",
    )
    list_filter = ("estado", "entrenador")
    search_fields = ("nombre",)


@admin.register(ReservaClase)
class ReservaClaseAdmin(admin.ModelAdmin):
    list_display = ("clase", "cliente", "estado", "creada_en")
    list_filter = ("estado",)
    search_fields = (
        "cliente__usuario__first_name",
        "cliente__usuario__last_name",
        "clase__nombre",
    )