from .menus import menu_de
from .roles import ROL_NOMBRES, rol_de


def usuario_actual(request):
    user = request.user
    if not user.is_authenticated:
        return {}
    nombre = user.get_full_name() or user.username
    iniciales = ''.join(p[0] for p in nombre.split()[:2]).upper()
    rol = rol_de(user)
    return {
        'nombre_usuario': nombre,
        'iniciales': iniciales,
        'rol_usuario': rol,
        'rol_nombre': ROL_NOMBRES.get(rol, '').upper(),
        'menu': menu_de(rol),
    }
