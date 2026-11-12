from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from cuentas.models import Cliente, Perfil

from . import datos_demo as demo
from .mixins import RolRequeridoMixin
from .roles import ADMIN, CLIENTE, ENTRENADOR, FINANCIERO, RECEPCION, rol_de, url_inicio


# =====================================================================
#  AUTENTICACIÓN (funcional)
# =====================================================================

class LoginVista(View):
    template_name = 'core/login.html'

    def get(self, request):
        if rol_de(request.user):
            return redirect(url_inicio(request.user))
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        usuario = User.objects.filter(email__iexact=email).first()
        if usuario is not None:
            usuario = authenticate(request, username=usuario.username, password=password)

        if usuario is None:
            return render(request, self.template_name, {
                'error': 'Correo o contraseña incorrectos.',
                'email': email,
            })

        if rol_de(usuario) is None:
            return render(request, self.template_name, {
                'error': 'Tu cuenta no tiene un rol asignado. Contacta al administrador.',
                'email': email,
            })

        login(request, usuario)

        destino = request.GET.get('next')
        if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
            return redirect(destino)
        return redirect(url_inicio(usuario))


class LogoutVista(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'Sesión cerrada correctamente.')
        return redirect('login')


class RegistroVista(View):
    template_name = 'core/registro.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        datos = {
            campo: request.POST.get(campo, '').strip()
            for campo in ('nombre', 'apellidos', 'dni', 'telefono', 'email')
        }
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        errores = []

        if not all(datos.values()) or not password or not password2:
            errores.append('Completa todos los campos.')

        if datos['dni'] and not (datos['dni'].isdigit() and len(datos['dni']) == 8):
            errores.append('El DNI debe tener exactamente 8 dígitos.')

        if len(datos['nombre']) > 100 or len(datos['apellidos']) > 100:
            errores.append('El nombre y los apellidos no pueden pasar de 100 caracteres.')

        if len(datos['telefono']) > 20:
            errores.append('El teléfono no puede pasar de 20 caracteres.')

        if datos['email']:
            try:
                validate_email(datos['email'])
                if len(datos['email']) > 150:
                    errores.append('El correo es demasiado largo.')
            except ValidationError:
                errores.append('Ingresa un correo electrónico válido.')

            if (User.objects.filter(email__iexact=datos['email']).exists()
                    or User.objects.filter(username__iexact=datos['email']).exists()):
                errores.append('Ya existe una cuenta con ese correo.')

        if datos['dni'] and Cliente.objects.filter(documento=datos['dni']).exists():
            errores.append('Ya existe un cliente registrado con ese DNI.')

        if password and password2 and password != password2:
            errores.append('Las contraseñas no coinciden.')
        elif password:
            try:
                validate_password(password, user=User(
                    username=datos['email'],
                    email=datos['email'],
                    first_name=datos['nombre'],
                    last_name=datos['apellidos'],
                ))
            except ValidationError as e:
                errores.extend(e.messages)

        if errores:
            return render(request, self.template_name, {'errores': errores, 'datos': datos})

        with transaction.atomic():
            usuario = User.objects.create_user(
                username=datos['email'],
                email=datos['email'],
                password=password,
                first_name=datos['nombre'],
                last_name=datos['apellidos'],
            )
            Perfil.objects.create(usuario=usuario, rol=CLIENTE)
            Cliente.objects.create(
                usuario=usuario,
                documento=datos['dni'],
                telefono=datos['telefono'],
            )

        messages.success(request, 'Registro completado. Ya puedes iniciar sesión.')
        return redirect('login')


# =====================================================================
#  PANTALLAS DEL SISTEMA (frontend con datos de demostración)
# =====================================================================

class VistaPanel(RolRequeridoMixin, View):
    """
    Base de todas las pantallas del panel.

    - GET: muestra la plantilla con los datos de contexto().
    - POST: por ahora solo muestra un mensaje de confirmación.
      TODO (fase backend): guardar en la base de datos según request.POST['accion'].
    """
    template_name = None
    mensaje_post = 'Cambios guardados correctamente.'
    mensajes_accion = {}

    def contexto(self, request):
        return {}

    def get(self, request):
        return render(request, self.template_name, self.contexto(request))

    def post(self, request):
        accion = request.POST.get('accion')
        messages.success(request, self.mensajes_accion.get(accion, self.mensaje_post))
        return redirect(request.path)


# ---------- Administrador / Recepcionista / Financiero ----------


def _resumen_facturas():
    emitidas = [f for f in demo.FACTURAS if f['estado'] == 'Emitida']
    anuladas = [f for f in demo.FACTURAS if f['estado'] == 'Anulada']
    total = sum(float(f['monto']) for f in emitidas)
    promedio = total / len(emitidas) if emitidas else 0
    return {
        'total': f'S/. {total:,.0f}',
        'emitidas': len(emitidas),
        'anuladas': len(anuladas),
        'promedio': f'S/. {promedio:,.0f}',
    }


class DashboardVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION, FINANCIERO)
    template_name = 'core/dashboard.html'

    def contexto(self, request):
        rol = rol_de(request.user)
        res = _resumen_facturas()
        kpis = {
            ADMIN: [
                {'valor': 9, 'titulo': 'Clientes registrados'},
                {'valor': 7, 'titulo': 'Membresías activas'},
                {'valor': len(demo.POR_VENCER), 'titulo': 'Por vencer (7 días)'},
                {'valor': res['total'], 'titulo': 'Total facturado'},
            ],
            RECEPCION: [
                {'valor': 9, 'titulo': 'Clientes registrados'},
                {'valor': 7, 'titulo': 'Membresías activas'},
                {'valor': len(demo.POR_VENCER), 'titulo': 'Por vencer (7 días)'},
                {'valor': 2, 'titulo': 'Notificaciones enviadas hoy'},
            ],
            FINANCIERO: [
                {'valor': res['total'], 'titulo': 'Total facturado'},
                {'valor': res['emitidas'], 'titulo': 'Facturas emitidas'},
                {'valor': res['anuladas'], 'titulo': 'Facturas anuladas'},
                {'valor': res['promedio'], 'titulo': 'Ticket promedio'},
            ],
        }
        return {
            'kpis': kpis[rol],
            'por_vencer': demo.POR_VENCER,
            'facturas': demo.FACTURAS[:5],
            'ingresos': demo.INGRESOS_MESES,
        }


class UsuariosVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/usuarios.html'
    mensajes_accion = {
        'agregar': 'Usuario agregado correctamente.',
        'modificar': 'Usuario modificado correctamente.',
        'eliminar': 'Usuario eliminado correctamente.',
    }

    def contexto(self, request):
        return {'usuarios': demo.CLIENTES}


class MembresiasVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/membresias.html'
    mensajes_accion = {
        'asignar': 'Membresía asignada correctamente.',
        'renovar': 'Membresía renovada correctamente.',
        'cancelar': 'Membresía cancelada correctamente.',
    }

    def contexto(self, request):
        return {
            'planes': demo.PLANES_MEMBRESIA,
            'membresias': demo.MEMBRESIAS,
            'clientes': demo.NOMBRES_CLIENTES,
        }


class PagosVista(VistaPanel):
    roles_permitidos = (ADMIN, FINANCIERO)
    template_name = 'core/pagos.html'
    mensajes_accion = {
        'registrar': 'Pago registrado y factura emitida correctamente.',
        'anular': 'Factura anulada correctamente.',
    }

    def contexto(self, request):
        return {'facturas': demo.FACTURAS, 'clientes': demo.NOMBRES_CLIENTES}


class ReporteFacturacionVista(VistaPanel):
    roles_permitidos = (ADMIN, FINANCIERO)
    template_name = 'core/reporte_facturacion.html'

    def contexto(self, request):
        res = _resumen_facturas()
        return {
            'facturas': demo.FACTURAS,
            'ingresos': demo.INGRESOS_MESES,
            'kpis': [
                {'valor': res['total'], 'titulo': 'Total facturado'},
                {'valor': res['emitidas'], 'titulo': 'Facturas emitidas'},
                {'valor': res['anuladas'], 'titulo': 'Facturas anuladas'},
                {'valor': res['promedio'], 'titulo': 'Ticket promedio'},
            ],
        }


class NotificacionesVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/notificaciones.html'
    mensaje_post = 'Notificación enviada correctamente.'

    def contexto(self, request):
        return {'clientes': demo.NOMBRES_CLIENTES, 'enviadas': demo.NOTIFICACIONES_ENVIADAS}


class ClasesGrupalesVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/clases_grupales.html'
    mensajes_accion = {
        'programar': 'Clase programada correctamente y agregada al calendario.',
        'modificar': 'Clase modificada correctamente.',
        'cancelar': 'Clase cancelada. Se notificó a los clientes inscritos.',
    }

    def contexto(self, request):
        programadas = [c for c in demo.CLASES_GRUPALES if c['estado'] == 'Programada']
        return {
            'clases': demo.CLASES_GRUPALES,
            'calendario': demo.CALENDARIO,
            'entrenadores': demo.ENTRENADORES,
            'kpis': [
                {'valor': len(programadas), 'titulo': 'Clases programadas'},
                {'valor': sum(c['cupos'] for c in programadas), 'titulo': 'Cupos disponibles'},
                {'valor': sum(1 for c in programadas if c['cupos'] == 0), 'titulo': 'Clases llenas'},
                {'valor': sum(1 for c in demo.CLASES_GRUPALES if c['estado'] == 'Cancelada'), 'titulo': 'Clases canceladas'},
            ],
        }


class HorariosEntrenadoresVista(VistaPanel):
    roles_permitidos = (ADMIN,)
    template_name = 'core/horarios_entrenadores.html'
    mensajes_accion = {
        'agregar': 'Horario guardado. Se notificó al entrenador.',
        'modificar': 'Horario actualizado. Se notificó al entrenador.',
        'eliminar': 'Horario eliminado correctamente.',
    }

    def contexto(self, request):
        return {
            'dias': demo.DIAS_SEMANA,
            'entrenadores': demo.ENTRENADORES,
            'grid': demo.HORARIO_GRID,
            'horarios': demo.HORARIOS,
        }


# ---------- Administrador / Entrenador ----------

class PlanEntrenamientoVista(VistaPanel):
    roles_permitidos = (ADMIN, ENTRENADOR)
    template_name = 'core/plan_entrenamiento.html'
    mensajes_accion = {
        'asignar': 'Plan asignado correctamente.',
        'modificar': 'Plan modificado correctamente.',
    }

    def contexto(self, request):
        return {
            'clientes': demo.NOMBRES_CLIENTES,
            'programas': demo.PROGRAMAS,
            'planes': demo.PLANES_ASIGNADOS,
        }


# ---------- Entrenador ----------

class DashboardEntrenadorVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/dashboard_entrenador.html'

    def contexto(self, request):
        return {
            'kpis': [
                {'valor': len(demo.CLIENTES_DEL_ENTRENADOR), 'titulo': 'Clientes asignados'},
                {'valor': len(demo.PLANES_ASIGNADOS), 'titulo': 'Planes activos'},
                {'valor': len(demo.PROGRESO), 'titulo': 'Progresos registrados'},
                {'valor': 1, 'titulo': 'Clientes sin registros'},
            ],
            'clientes': demo.CLIENTES_DEL_ENTRENADOR,
            'progresos': demo.PROGRESO,
        }


class EntrenadorClientesVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/entrenador_clientes.html'

    def contexto(self, request):
        return {'clientes': demo.CLIENTES_DEL_ENTRENADOR}


class ProgresoVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/progreso.html'
    mensajes_accion = {
        'registrar': 'Progreso registrado correctamente.',
        'editar': 'Progreso actualizado correctamente.',
        'eliminar': 'Registro de progreso eliminado correctamente.',
    }

    def contexto(self, request):
        return {'registros': demo.PROGRESO, 'clientes': demo.NOMBRES_CLIENTES}


class MiAgendaVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/mi_agenda.html'
    http_method_names = ['get', 'head', 'options']

    def contexto(self, request):
        return {'horario': demo.MI_HORARIO, 'clases': demo.MIS_CLASES}


# ---------- Cliente ----------

class InicioClienteVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/inicio_cliente.html'

    def contexto(self, request):
        return {
            'membresia': demo.MI_MEMBRESIA,
            'plan': demo.MI_PLAN,
            'ultimo_progreso': demo.MI_PROGRESO[-1],
            'ultimo_pago': demo.MIS_PAGOS[0],
            'nuevas': [n for n in demo.MIS_NOTIFICACIONES if n['nueva']],
        }


class MiMembresiaVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/mi_membresia.html'
    mensaje_post = 'Tu solicitud fue enviada a recepción. Te avisaremos cuando esté lista.'

    def contexto(self, request):
        return {'membresia': demo.MI_MEMBRESIA, 'planes': demo.PLANES_MEMBRESIA}


class MiPlanVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/mi_plan.html'

    def contexto(self, request):
        return {'plan': demo.MI_PLAN}


class MiProgresoVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/mi_progreso.html'

    def contexto(self, request):
        return {'registros': demo.MI_PROGRESO, 'ultimo': demo.MI_PROGRESO[-1]}


class MisPagosVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/mis_pagos.html'

    def contexto(self, request):
        return {'pagos': demo.MIS_PAGOS}


class MisNotificacionesVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/mis_notificaciones.html'

    def contexto(self, request):
        return {'notificaciones': demo.MIS_NOTIFICACIONES}


class ClasesClienteVista(VistaPanel):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/clases_cliente.html'
    mensajes_accion = {
        'reservar': 'Reserva confirmada. ¡Te esperamos en la clase!',
        'cancelar_reserva': 'Reserva cancelada correctamente.',
    }

    def contexto(self, request):
        clases = demo.CLASES_CLIENTE
        return {
            'clases': clases,
            'reservas': sum(1 for c in clases if c['reservada']),
        }
