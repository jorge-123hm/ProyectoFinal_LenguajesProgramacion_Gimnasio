from django.urls import path
from .views import (
    LoginVista, LogoutVista, RegistroVista, InicioClienteVista,
    DashboardVista, UsuariosVista, PlanEntrenamientoVista, ProgresoVista,
)

urlpatterns = [
    path('', LoginVista.as_view(), name='login'),
    path('logout/', LogoutVista.as_view(), name='logout'),
    path('registro/', RegistroVista.as_view(), name='registro'),
    path('inicio/', InicioClienteVista.as_view(), name='inicio_cliente'),
    path('dashboard/', DashboardVista.as_view(), name='dashboard'),
    path('usuarios/', UsuariosVista.as_view(), name='usuarios'),
    path('plan-entrenamiento/', PlanEntrenamientoVista.as_view(), name='plan_entrenamiento'),
    path('progreso/', ProgresoVista.as_view(), name='progreso'),
]