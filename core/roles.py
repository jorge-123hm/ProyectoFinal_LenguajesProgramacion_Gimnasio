from cuentas.models import Perfil

ADMIN = Perfil.Rol.ADMINISTRADOR.value
RECEPCION = Perfil.Rol.RECEPCIONISTA.value
ENTRENADOR = Perfil.Rol.ENTRENADOR.value
FINANCIERO = Perfil.Rol.FINANCIERO.value
CLIENTE = Perfil.Rol.CLIENTE.value

ROL_NOMBRES = dict(Perfil.Rol.choices)

# Pantalla a la que llega cada rol después de iniciar sesión
INICIO_POR_ROL = {
    ADMIN: 'dashboard',
    RECEPCION: 'dashboard',
    FINANCIERO: 'dashboard',
    ENTRENADOR: 'dashboard_entrenador',
    CLIENTE: 'inicio_cliente',
}


def rol_de(user):
    """Devuelve el rol del usuario o None si no tiene."""
    if not user.is_authenticated:
        return None
    if hasattr(user, 'perfil'):
        return user.perfil.rol
    if user.is_superuser:
        return ADMIN
    return None


def url_inicio(user):
    return INICIO_POR_ROL.get(rol_de(user), 'login')