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
from membresias.models import Membresia

from .mixins import RolRequeridoMixin
from .roles import ADMIN, CLIENTE, ENTRENADOR, FINANCIERO, RECEPCION, rol_de, url_inicio


# ---------- Autenticación ----------

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

        # vereifica que los datos esten completos
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

        # Con errores: se muestran y se permite corregir
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


# ---------- Cliente ----------

class InicioClienteVista(RolRequeridoMixin, View):
    roles_permitidos = (CLIENTE,)
    template_name = 'core/inicio_cliente.html'

    def get(self, request):
        cliente = getattr(request.user, 'cliente', None)
        membresia = None
        if cliente is not None:
            membresia = (
                cliente.membresias
                .filter(estado=Membresia.Estado.ACTIVA)
                .order_by('-fecha_vencimiento')
                .first()
            )
        return render(request, self.template_name, {'membresia': membresia})


# --datos simulados en administracion ----------

class DashboardVista(RolRequeridoMixin, View):
    roles_permitidos = (ADMIN, RECEPCION, FINANCIERO)
    template_name = 'core/dashboard.html'

    def get(self, request):
        return render(request, self.template_name)


class UsuariosVista(RolRequeridoMixin, View):
    roles_permitidos = (ADMIN, RECEPCION)
    template_name = 'core/usuarios.html'

    def get(self, request):
        usuarios = [
            {
                'nombre': 'Guadalupe',
                'apellidos': 'Saire Flores',
                'telefono': '987654321',
                'correo': 'guadalupe.saire@email.com',
                'membresia': 'Premium',
            },
            {
                'nombre': 'Graciela',
                'apellidos': 'Canales Palomino',
                'telefono': '912345678',
                'correo': 'graciela.canales@email.com',
                'membresia': 'Básico',
            },
        ]
        return render(request, self.template_name, {'usuarios': usuarios})


# -datos simulados de vista entrenador-

class PlanEntrenamientoVista(RolRequeridoMixin, View):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/plan_entrenamiento.html'

    def contexto(self):
        return {
            'clientes': [
                'Guadalupe Saire Flores',
                'Carlos Fernández',
                'María López',
            ],
            'programas': [
                'Programa de Fuerza',
                'Programa de Resistencia',
                'Programa de Pérdida de Peso',
                'Programa de Flexibilidad',
            ],
        }

    def get(self, request):
        return render(request, self.template_name, self.contexto())

    def post(self, request):
        datos = self.contexto()
        datos['mensaje'] = 'Plan asignado correctamente.'
        return render(request, self.template_name, datos)


class ProgresoVista(RolRequeridoMixin, View):
    roles_permitidos = (ENTRENADOR,)
    template_name = 'core/progreso.html'

    def contexto(self):
        return {
            'registros': [
                {'nombre': 'Jorge Montes', 'fecha': '2026-11-02', 'peso': 50,
                'repeticiones': 12, 'comentario': 'Buen progreso esta semana'},
                {'nombre': 'Luciana Palomino', 'fecha': '2026-11-03', 'peso': 70,
                'repeticiones': 10, 'comentario': 'Mejorar técnica'},
                {'nombre': 'Dayana Saire', 'fecha': '2026-11-04', 'peso': 30,
                'repeticiones': 15, 'comentario': 'Incrementar peso la próxima sesión'},
            ],
            'clientes': ['Jorge Montes', 'Luciana Palomino', 'Dayana Saire'],
        }

    def get(self, request):
        return render(request, self.template_name, self.contexto())

    def post(self, request):
        datos = self.contexto()
        datos['mensaje'] = 'Progreso registrado correctamente.'
        return render(request, self.template_name, datos)