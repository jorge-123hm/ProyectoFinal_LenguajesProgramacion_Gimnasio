from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .roles import rol_de, url_inicio


class RolRequeridoMixin(LoginRequiredMixin):
    """Exige sesión iniciada y que el rol esté en roles_permitidos."""
    roles_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if rol_de(request.user) not in self.roles_permitidos:
            messages.error(request, 'No tienes permiso para entrar a esa sección.')
            return redirect(url_inicio(request.user))
        return super().dispatch(request, *args, **kwargs)