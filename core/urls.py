from django.urls import path

from . import views

urlpatterns = [
    # Autenticación
    path('', views.LoginVista.as_view(), name='login'),
    path('logout/', views.LogoutVista.as_view(), name='logout'),
    path('registro/', views.RegistroVista.as_view(), name='registro'),

    # Administrador / Recepcionista / Financiero
    path('dashboard/', views.DashboardVista.as_view(), name='dashboard'),
    path('usuarios/', views.UsuariosVista.as_view(), name='usuarios'),
    path('membresias/', views.MembresiasVista.as_view(), name='membresias'),
    path('pagos/', views.PagosVista.as_view(), name='pagos'),
    path('reporte-facturacion/', views.ReporteFacturacionVista.as_view(), name='reporte_facturacion'),
    path('notificaciones/', views.NotificacionesVista.as_view(), name='notificaciones'),
    path('clases-grupales/', views.ClasesGrupalesVista.as_view(), name='clases_grupales'),
    path('horarios-entrenadores/', views.HorariosEntrenadoresVista.as_view(), name='horarios_entrenadores'),

    # Administrador / Entrenador
    path('plan-entrenamiento/', views.PlanEntrenamientoVista.as_view(), name='plan_entrenamiento'),

    # Entrenador
    path('entrenador/dashboard/', views.DashboardEntrenadorVista.as_view(), name='dashboard_entrenador'),
    path('entrenador/clientes/', views.EntrenadorClientesVista.as_view(), name='entrenador_clientes'),
    path('progreso/', views.ProgresoVista.as_view(), name='progreso'),
    path('entrenador/mi-agenda/', views.MiAgendaVista.as_view(), name='mi_agenda'),

    # Cliente
    path('inicio/', views.InicioClienteVista.as_view(), name='inicio_cliente'),
    path('mi-membresia/', views.MiMembresiaVista.as_view(), name='mi_membresia'),
    path('mi-plan/', views.MiPlanVista.as_view(), name='mi_plan'),
    path('mi-progreso/', views.MiProgresoVista.as_view(), name='mi_progreso'),
    path('clases/', views.ClasesClienteVista.as_view(), name='clases_cliente'),
    path('mis-pagos/', views.MisPagosVista.as_view(), name='mis_pagos'),
    path('mis-notificaciones/', views.MisNotificacionesVista.as_view(), name='mis_notificaciones'),
]
