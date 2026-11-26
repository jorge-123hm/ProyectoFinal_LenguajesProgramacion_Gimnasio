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

from django.db.models import Prefetch
from membresias.models import Membresia, PlanMembresia

from datetime import date

from membresias.servicios import (
    ReglaDeNegocio, asignar_membresia, cancelar_membresia,
    marcar_vencidas, renovar_membresia,
)

from decimal import Decimal, InvalidOperation

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from facturacion.models import Factura
from facturacion.servicios import anular_factura, registrar_pago

from django.db.models import Max

from entrenamiento.models import ProgramaEntrenamiento, ProgresoCliente
from entrenamiento.servicios import (
    PROGRAMAS, asignar_programa, editar_progreso,
    modificar_programa, registrar_progreso,
)

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

class DashboardVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION, FINANCIERO)
    template_name = 'core/dashboard.html'

    def contexto(self, request):
        rol = rol_de(request.user)
        res = _resumen_facturas(Factura.objects.all())
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
            'facturas': [_factura_a_dict(f) for f in _facturas_qs().order_by('-fecha_emision', '-id')[:5]],
            'ingresos': _ingresos_por_mes(),
        }

def _leer_datos_cliente(post):
    return {
        campo: post.get(campo, '').strip()
        for campo in ('nombre', 'apellidos', 'dni', 'telefono', 'email')
    }


def _validar_cliente(datos, cliente=None):
    """Devuelve la lista de errores. Al editar, se pasa el cliente para ignorar sus propios datos."""
    errores = []

    if not all(datos.values()):
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

        usuarios = User.objects.all()
        if cliente is not None:
            usuarios = usuarios.exclude(pk=cliente.usuario_id)
        if (usuarios.filter(email__iexact=datos['email']).exists()
                or usuarios.filter(username__iexact=datos['email']).exists()):
            errores.append('Ya existe una cuenta con ese correo.')

    if datos['dni']:
        clientes = Cliente.objects.all()
        if cliente is not None:
            clientes = clientes.exclude(pk=cliente.pk)
        if clientes.filter(documento=datos['dni']).exists():
            errores.append('Ya existe un cliente registrado con ese DNI.')

    return errores

class UsuariosVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/usuarios.html'

    def contexto(self, request):
        marcar_vencidas()
        activas = Prefetch(
            'membresias',
            queryset=(Membresia.objects
                    .filter(estado=Membresia.Estado.ACTIVA)
                    .select_related('plan')
                    .order_by('-fecha_vencimiento')),
            to_attr='activas',
        )
        clientes = (Cliente.objects
                    .filter(activo=True)
                    .select_related('usuario')
                    .prefetch_related(activas)
                    .order_by('usuario__last_name', 'usuario__first_name'))
        return {
            'usuarios': [
                {
                    'id': c.pk,
                    'nombre': c.usuario.first_name,
                    'apellidos': c.usuario.last_name,
                    'dni': c.documento,
                    'telefono': c.telefono,
                    'email': c.usuario.email,
                    'membresia': c.activas[0].plan.nombre if c.activas else 'Sin membresía',
                }
                for c in clientes
            ]
        }

    def post(self, request):
        accion = request.POST.get('accion')
        if accion == 'agregar':
            self._agregar(request)
        elif accion == 'modificar':
            self._modificar(request)
        elif accion == 'eliminar':
            self._eliminar(request)
        return redirect('usuarios')

    def _agregar(self, request):
        datos = _leer_datos_cliente(request.POST)
        nombre_plan = request.POST.get('membresia', 'Sin membresía')
        errores = _validar_cliente(datos)

        plan = None
        if nombre_plan != 'Sin membresía':
            plan = PlanMembresia.objects.filter(nombre=nombre_plan, activo=True).first()
            if plan is None:
                errores.append(f'El plan «{nombre_plan}» no existe. Créalo en el panel de administración.')

        if errores:
            for e in errores:
                messages.error(request, e)
            return

        with transaction.atomic():
            usuario = User.objects.create_user(
                username=datos['email'],
                email=datos['email'],
                password=datos['dni'],  # contraseña inicial = DNI
                first_name=datos['nombre'],
                last_name=datos['apellidos'],
            )
            Perfil.objects.create(usuario=usuario, rol=CLIENTE)
            cliente = Cliente.objects.create(
                usuario=usuario,
                documento=datos['dni'],
                telefono=datos['telefono'],
            )
            if plan:
                Membresia.objects.create(cliente=cliente, plan=plan)

        messages.success(request, 'Usuario agregado correctamente. Su contraseña inicial es su DNI.')

    def _cliente_seleccionado(self, request):
        try:
            return Cliente.objects.select_related('usuario').get(pk=request.POST.get('id'), activo=True)
        except (Cliente.DoesNotExist, ValueError):
            messages.error(request, 'El usuario seleccionado no existe.')
            return None

    def _modificar(self, request):
        cliente = self._cliente_seleccionado(request)
        if cliente is None:
            return

        datos = _leer_datos_cliente(request.POST)
        errores = _validar_cliente(datos, cliente)
        if errores:
            for e in errores:
                messages.error(request, e)
            return

        with transaction.atomic():
            usuario = cliente.usuario
            if usuario.username.lower() == usuario.email.lower():
                usuario.username = datos['email']
            usuario.email = datos['email']
            usuario.first_name = datos['nombre']
            usuario.last_name = datos['apellidos']
            usuario.save()

            cliente.documento = datos['dni']
            cliente.telefono = datos['telefono']
            cliente.save()

        messages.success(request, 'Usuario modificado correctamente.')

    def _eliminar(self, request):
        cliente = self._cliente_seleccionado(request)
        if cliente is None:
            return

        # Eliminación lógica: conserva el historial de pagos, membresías y progreso
        with transaction.atomic():
            cliente.membresias.filter(estado=Membresia.Estado.ACTIVA).update(
                estado=Membresia.Estado.CANCELADA
            )
            cliente.activo = False
            cliente.save(update_fields=['activo'])
            cliente.usuario.is_active = False
            cliente.usuario.save(update_fields=['is_active'])

        messages.success(request, 'Usuario eliminado correctamente.')

def _nombre_completo(cliente):
    return cliente.usuario.get_full_name() or cliente.usuario.username


def _obtener_fecha(texto):
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise ReglaDeNegocio('La fecha ingresada no es válida.')


def _obtener_plan(nombre):
    plan = PlanMembresia.objects.filter(nombre=nombre, activo=True).first()
    if plan is None:
        raise ReglaDeNegocio('El plan seleccionado no existe o no está activo.')
    return plan


def _obtener_cliente(pk):
    try:
        return Cliente.objects.select_related('usuario').get(pk=pk, activo=True)
    except (Cliente.DoesNotExist, ValueError):
        raise ReglaDeNegocio('El cliente seleccionado no existe.')


def _obtener_membresia(pk):
    try:
        return Membresia.objects.select_related('cliente__usuario', 'plan').get(pk=pk)
    except (Membresia.DoesNotExist, ValueError):
        raise ReglaDeNegocio('La membresía seleccionada no existe.')

class MembresiasVista(VistaPanel):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/membresias.html'

    def contexto(self, request):
        marcar_vencidas()
        planes = list(PlanMembresia.objects.filter(activo=True).order_by('precio'))
        destacado = planes[-1].pk if len(planes) > 1 else None
        membresias = (Membresia.objects
                    .filter(cliente__activo=True)
                    .select_related('cliente__usuario', 'plan')
                    .order_by('-creada_en'))
        clientes = (Cliente.objects
                    .filter(activo=True)
                    .select_related('usuario')
                    .order_by('usuario__last_name', 'usuario__first_name'))
        return {
            'planes': [
                {
                    'nombre': p.nombre,
                    'precio': f'{p.precio:.2f}',
                    'duracion': p.duracion_dias,
                    'destacado': p.pk == destacado,
                    'beneficios': [l.strip() for l in p.descripcion.splitlines() if l.strip()],
                }
                for p in planes
            ],
            'membresias': [
                {
                    'id': m.pk,
                    'cliente': _nombre_completo(m.cliente),
                    'plan': m.plan.nombre,
                    'inicio': m.fecha_inicio.isoformat(),
                    'vencimiento': m.fecha_vencimiento.isoformat(),
                    'estado': m.get_estado_display(),
                }
                for m in membresias
            ],
            'clientes': [{'id': c.pk, 'nombre': _nombre_completo(c)} for c in clientes],
        }

    def post(self, request):
        accion = request.POST.get('accion')
        try:
            if accion == 'asignar':
                self._asignar(request)
            elif accion == 'renovar':
                self._renovar(request)
            elif accion == 'cancelar':
                self._cancelar(request)
        except ReglaDeNegocio as error:
            messages.error(request, str(error))
        return redirect('membresias')

    def _asignar(self, request):
        cliente = _obtener_cliente(request.POST.get('cliente'))
        plan = _obtener_plan(request.POST.get('plan'))
        inicio = _obtener_fecha(request.POST.get('inicio', ''))
        membresia = asignar_membresia(cliente, plan, inicio)
        messages.success(
            request,
            f'Membresía {plan.nombre} asignada a {_nombre_completo(cliente)} '
            f'hasta el {membresia.fecha_vencimiento:%d/%m/%Y}.',
        )

    def _renovar(self, request):
        membresia = _obtener_membresia(request.POST.get('id'))
        plan = _obtener_plan(request.POST.get('plan'))
        inicio = _obtener_fecha(request.POST.get('inicio', ''))
        membresia = renovar_membresia(membresia, plan, inicio)
        messages.success(
            request,
            f'Membresía renovada. Nuevo vencimiento: {membresia.fecha_vencimiento:%d/%m/%Y}.',
        )

    def _cancelar(self, request):
        membresia = _obtener_membresia(request.POST.get('id'))
        cancelar_membresia(membresia, request.POST.get('motivo', '').strip())
        messages.success(request, 'Membresía cancelada correctamente.')

MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _facturas_qs():
    return Factura.objects.select_related('cliente__usuario', 'membresia__plan')


def _factura_a_dict(f):
    return {
        'id': f.numero,
        'cliente': _nombre_completo(f.cliente),
        'concepto': f'Membresía {f.membresia.plan.nombre}' if f.membresia else 'Servicio adicional',
        'monto': f'{f.total:.2f}',
        'fecha': f.fecha_emision.isoformat(),
        'estado': f.get_estado_display(),
    }


def _resumen_facturas(queryset):
    """Indicadores de un conjunto de facturas (las anuladas no cuentan en el total)."""
    validas = queryset.exclude(estado=Factura.Estado.ANULADA)
    agregado = validas.aggregate(total=Sum('total'), cantidad=Count('pk'))
    total = agregado['total'] or Decimal('0')
    cantidad = agregado['cantidad']
    promedio = total / cantidad if cantidad else Decimal('0')
    return {
        'total': f'S/. {total:,.0f}',
        'emitidas': cantidad,
        'anuladas': queryset.filter(estado=Factura.Estado.ANULADA).count(),
        'promedio': f'S/. {promedio:,.0f}',
    }


def _inicios_de_mes(hoy, cantidad):
    inicios = []
    for atras in range(cantidad - 1, -1, -1):
        mes = hoy.month - atras
        anio = hoy.year
        while mes <= 0:
            mes += 12
            anio -= 1
        inicios.append(date(anio, mes, 1))
    return inicios


def _ingresos_por_mes(cantidad=6):
    """Total facturado por mes (sin anuladas) en los últimos meses, para el gráfico."""
    inicios = _inicios_de_mes(timezone.localdate(), cantidad)
    por_mes = (Factura.objects
            .exclude(estado=Factura.Estado.ANULADA)
            .filter(fecha_emision__gte=inicios[0])
            .annotate(mes=TruncMonth('fecha_emision'))
            .values('mes')
            .annotate(suma=Sum('total')))
    totales = {(fila['mes'].year, fila['mes'].month): fila['suma'] for fila in por_mes}
    valores = [totales.get((i.year, i.month), Decimal('0')) for i in inicios]
    maximo = max(valores) if valores else Decimal('0')
    return [
        {
            'mes': MESES[i.month - 1],
            'monto': f'{v:.0f}',
            'altura': round(v / maximo * 100) if maximo else 0,
        }
        for i, v in zip(inicios, valores)
    ]


def _obtener_monto(texto):
    try:
        monto = Decimal(texto)
    except (InvalidOperation, TypeError):
        raise ReglaDeNegocio('El monto ingresado no es válido.')
    if not monto.is_finite() or monto > Decimal('99999999.99'):
        raise ReglaDeNegocio('El monto ingresado no es válido.')
    return monto.quantize(Decimal('0.01'))


def _fecha_o_none(texto):
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


class PagosVista(VistaPanel):
    roles_permitidos = (ADMIN, FINANCIERO)
    template_name = 'core/pagos.html'

    def contexto(self, request):
        facturas = _facturas_qs().order_by('-fecha_emision', '-id')
        clientes = (Cliente.objects
                    .filter(activo=True)
                    .select_related('usuario')
                    .order_by('usuario__last_name', 'usuario__first_name'))
        return {
            'facturas': [_factura_a_dict(f) for f in facturas],
            'clientes': [{'id': c.pk, 'nombre': _nombre_completo(c)} for c in clientes],
        }

    def post(self, request):
        accion = request.POST.get('accion')
        try:
            if accion == 'registrar':
                cliente = _obtener_cliente(request.POST.get('cliente'))
                monto = _obtener_monto(request.POST.get('monto'))
                fecha = _obtener_fecha(request.POST.get('fecha', ''))
                factura = registrar_pago(
                    cliente, monto, fecha,
                    request.POST.get('metodo'),
                    request.POST.get('concepto', 'membresia'),
                )
                messages.success(
                    request,
                    f'Pago de S/. {monto:.2f} registrado. Factura {factura.numero} emitida.',
                )
            elif accion == 'anular':
                factura = anular_factura(request.POST.get('id'))
                messages.success(request, f'Factura {factura.numero} anulada correctamente.')
        except ReglaDeNegocio as error:
            messages.error(request, str(error))
        return redirect('pagos')


class ReporteFacturacionVista(VistaPanel):
    roles_permitidos = (ADMIN, FINANCIERO)
    template_name = 'core/reporte_facturacion.html'

    def contexto(self, request):
        hoy = timezone.localdate()
        desde = _fecha_o_none(request.GET.get('desde')) or _inicios_de_mes(hoy, 6)[0]
        hasta = _fecha_o_none(request.GET.get('hasta')) or hoy
        if desde > hasta:
            messages.error(request, 'La fecha inicial no puede ser posterior a la final.')
            desde, hasta = _inicios_de_mes(hoy, 6)[0], hoy

        estado = request.GET.get('estado', '')
        facturas = _facturas_qs().filter(fecha_emision__gte=desde, fecha_emision__lte=hasta)
        if estado in Factura.Estado.values:
            facturas = facturas.filter(estado=estado)
        else:
            estado = ''

        res = _resumen_facturas(facturas)
        if not facturas.exists():
            messages.warning(request, 'No hay facturas en el periodo seleccionado.')

        return {
            'filtros': {'desde': desde.isoformat(), 'hasta': hasta.isoformat(), 'estado': estado},
            'estados': [{'valor': v, 'texto': t} for v, t in Factura.Estado.choices],
            'facturas': [_factura_a_dict(f) for f in facturas.order_by('-fecha_emision', '-id')],
            'ingresos': _ingresos_por_mes(),
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

def _nombre_de_usuario(usuario):
    return usuario.get_full_name() or usuario.username


def _obtener_entero(texto, mensaje, maximo=9999):
    try:
        valor = int(texto)
    except (TypeError, ValueError):
        raise ReglaDeNegocio(mensaje)
    if not 0 <= valor <= maximo:
        raise ReglaDeNegocio(mensaje)
    return valor


def _obtener_peso(texto):
    try:
        peso = Decimal(texto)
    except (InvalidOperation, TypeError):
        raise ReglaDeNegocio('El peso levantado no es válido.')
    if not peso.is_finite() or peso < 0 or peso > Decimal('99999.9'):
        raise ReglaDeNegocio('El peso levantado no es válido.')
    return peso.quantize(Decimal('0.1'))


def _obtener_programa(pk):
    try:
        return (ProgramaEntrenamiento.objects
                .select_related('cliente__usuario', 'entrenador')
                .get(pk=pk))
    except (ProgramaEntrenamiento.DoesNotExist, ValueError):
        raise ReglaDeNegocio('El plan seleccionado no existe.')


def _obtener_progreso(pk, entrenador):
    try:
        return (ProgresoCliente.objects
                .select_related('cliente__usuario')
                .get(pk=pk, entrenador=entrenador))
    except (ProgresoCliente.DoesNotExist, ValueError):
        raise ReglaDeNegocio('El registro seleccionado no existe.')


def _progreso_a_dict(r):
    return {
        'id': r.pk,
        'cliente': _nombre_completo(r.cliente),
        'fecha': r.fecha.isoformat(),
        'peso': f'{r.peso_levantado:.1f}' if r.peso_levantado is not None else '',
        'repeticiones': r.repeticiones if r.repeticiones is not None else '',
        'comentario': r.observaciones,
    }


def _clientes_del_entrenador(entrenador):
    """Clientes con un programa en curso a cargo del entrenador."""
    programas = (ProgramaEntrenamiento.objects
                .filter(entrenador=entrenador, estado=ProgramaEntrenamiento.Estado.ACTIVO)
                .select_related('cliente__usuario')
                .order_by('cliente__usuario__last_name', 'cliente__usuario__first_name'))
    programas = list(programas)
    ultimos = dict(
        ProgresoCliente.objects
        .filter(cliente_id__in=[p.cliente_id for p in programas])
        .values('cliente_id')
        .annotate(ultimo=Max('fecha'))
        .values_list('cliente_id', 'ultimo')
    )
    return [
        {
            'cliente': _nombre_completo(p.cliente),
            'objetivo': p.objetivo,
            'programa': p.nombre,
            'frecuencia': p.frecuencia,
            'ultimo': ultimos[p.cliente_id].isoformat() if p.cliente_id in ultimos else 'Sin registros',
        }
        for p in programas
    ]


def _clientes_para_select():
    clientes = (Cliente.objects
                .filter(activo=True)
                .select_related('usuario')
                .order_by('usuario__last_name', 'usuario__first_name'))
    return [{'id': c.pk, 'nombre': _nombre_completo(c)} for c in clientes]


class PlanEntrenamientoVista(VistaPanel):
    roles_permitidos = (ADMIN, ENTRENADOR)
    template_name = 'core/plan_entrenamiento.html'

    def contexto(self, request):
        programas = (ProgramaEntrenamiento.objects
                    .filter(estado=ProgramaEntrenamiento.Estado.ACTIVO)
                    .select_related('cliente__usuario', 'entrenador')
                    .order_by('-fecha_inicio', '-id'))
        if rol_de(request.user) == ENTRENADOR:
            programas = programas.filter(entrenador=request.user)
        return {
            'clientes': _clientes_para_select(),
            'programas': PROGRAMAS,
            'planes': [
                {
                    'id': p.pk,
                    'cliente': _nombre_completo(p.cliente),
                    'programa': p.nombre,
                    'objetivos': p.objetivo,
                    'capacidades': p.capacidades,
                    'frecuencia': p.frecuencia,
                    'entrenador': _nombre_de_usuario(p.entrenador),
                    'fecha': p.fecha_inicio.isoformat(),
                }
                for p in programas
            ],
        }

    def post(self, request):
        accion = request.POST.get('accion')
        es_entrenador = rol_de(request.user) == ENTRENADOR
        try:
            frecuencia = _obtener_entero(
                request.POST.get('frecuencia'),
                'La frecuencia debe estar entre 1 y 7 días por semana.',
            )
            nombre = request.POST.get('programa', '')
            objetivos = request.POST.get('objetivos', '').strip()
            capacidades = request.POST.get('capacidades', '').strip()

            if accion == 'asignar':
                cliente = _obtener_cliente(request.POST.get('cliente'))
                programa = asignar_programa(
                    cliente,
                    request.user if es_entrenador else None,
                    nombre, objetivos, capacidades, frecuencia,
                )
                messages.success(
                    request,
                    f'Plan «{programa.nombre}» asignado a {_nombre_completo(cliente)}. '
                    f'Entrenador: {_nombre_de_usuario(programa.entrenador)}.',
                )
            elif accion == 'modificar':
                programa = _obtener_programa(request.POST.get('id'))
                if es_entrenador and programa.entrenador_id != request.user.pk:
                    raise ReglaDeNegocio('Ese plan pertenece a otro entrenador.')
                modificar_programa(programa, nombre, objetivos, capacidades, frecuencia)
                messages.success(request, 'Plan modificado correctamente.')
        except ReglaDeNegocio as error:
            messages.error(request, str(error))
        return redirect('plan_entrenamiento')


class DashboardEntrenadorVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/dashboard_entrenador.html'

    def contexto(self, request):
        clientes = _clientes_del_entrenador(request.user)
        registros = (ProgresoCliente.objects
                    .filter(entrenador=request.user)
                    .select_related('cliente__usuario'))
        return {
            'kpis': [
                {'valor': len(clientes), 'titulo': 'Clientes asignados'},
                {'valor': len(clientes), 'titulo': 'Planes activos'},
                {'valor': registros.count(), 'titulo': 'Progresos registrados'},
                {'valor': sum(1 for c in clientes if c['ultimo'] == 'Sin registros'),
                'titulo': 'Clientes sin registros'},
            ],
            'clientes': clientes,
            'progresos': [_progreso_a_dict(r) for r in registros.order_by('-fecha', '-id')[:5]],
        }

# ---------- Entrenador ----------

class EntrenadorClientesVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/entrenador_clientes.html'

    def contexto(self, request):
        return {'clientes': _clientes_del_entrenador(request.user)}


class ProgresoVista(VistaPanel):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/progreso.html'

    def contexto(self, request):
        registros = (ProgresoCliente.objects
                    .filter(entrenador=request.user)
                    .select_related('cliente__usuario')
                    .order_by('-fecha', '-id'))
        return {
            'registros': [_progreso_a_dict(r) for r in registros],
            'clientes': _clientes_para_select(),
        }

    def post(self, request):
        accion = request.POST.get('accion')
        try:
            if accion in ('registrar', 'editar'):
                fecha = _obtener_fecha(request.POST.get('fecha', ''))
                peso = _obtener_peso(request.POST.get('peso'))
                repeticiones = _obtener_entero(
                    request.POST.get('repeticiones'), 'Las repeticiones no son válidas.'
                )
                comentario = request.POST.get('comentario', '').strip()

            if accion == 'registrar':
                cliente = _obtener_cliente(request.POST.get('cliente'))
                registrar_progreso(cliente, request.user, fecha, peso, repeticiones, comentario)
                messages.success(request, 'Progreso registrado correctamente.')
            elif accion == 'editar':
                registro = _obtener_progreso(request.POST.get('id'), request.user)
                editar_progreso(registro, fecha, peso, repeticiones, comentario)
                messages.success(request, 'Progreso actualizado correctamente.')
            elif accion == 'eliminar':
                registro = _obtener_progreso(request.POST.get('id'), request.user)
                registro.delete()
                messages.success(request, 'Registro de progreso eliminado correctamente.')
        except ReglaDeNegocio as error:
            messages.error(request, str(error))
        return redirect('progreso')


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
