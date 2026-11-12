"""
Datos de demostración para el frontend.

IMPORTANTE: estos datos son ficticios y solo sirven para mostrar las pantallas.
En la fase de backend cada lista se reemplazará por consultas a la base de datos.
"""

CLIENTES = [
    {'id': 1, 'nombre': 'David', 'apellidos': 'Lachira', 'dni': '72145896', 'telefono': '987654321',
     'email': 'da.lachira@email.com', 'membresia': 'Premium'},
    {'id': 2, 'nombre': 'Odalis', 'apellidos': 'Domínguez', 'dni': '70239481', 'telefono': '912345678',
     'email': 'odalis@email.com', 'membresia': 'Básico'},
    {'id': 3, 'nombre': 'Jorge', 'apellidos': 'Suárez', 'dni': '45871236', 'telefono': '961234567',
     'email': 'jorge.suarez@email.com', 'membresia': 'Premium'},
    {'id': 4, 'nombre': 'Yarlequé', 'apellidos': 'Timaná', 'dni': '71203548', 'telefono': '930123456',
     'email': 'yarleque@email.com', 'membresia': 'Básico'},
    {'id': 5, 'nombre': 'María', 'apellidos': 'López', 'dni': '46012387', 'telefono': '915678234',
     'email': 'maria.lopez@email.com', 'membresia': 'Standard'},
    {'id': 6, 'nombre': 'Carlos', 'apellidos': 'Fernández', 'dni': '73345129', 'telefono': '987123654',
     'email': 'carlos.fernandez@email.com', 'membresia': 'Premium'},
    {'id': 7, 'nombre': 'Lucía', 'apellidos': 'Martínez', 'dni': '47788216', 'telefono': '951234789',
     'email': 'lucia.martinez@email.com', 'membresia': 'Básico'},
    {'id': 8, 'nombre': 'Pedro', 'apellidos': 'García', 'dni': '40965731', 'telefono': '921345678',
     'email': 'pedro.garcia@email.com', 'membresia': 'Standard'},
    {'id': 9, 'nombre': 'Elena', 'apellidos': 'Torres', 'dni': '74410982', 'telefono': '912345987',
     'email': 'elena.torres@email.com', 'membresia': 'Premium'},
]

NOMBRES_CLIENTES = [f"{c['nombre']} {c['apellidos']}" for c in CLIENTES]

# Precios y beneficios de ejemplo: ajústalos a los del gimnasio.
PLANES_MEMBRESIA = [
    {'nombre': 'Básico', 'precio': '80.00', 'duracion': 30, 'destacado': False,
     'beneficios': ['Acceso a sala de musculación', 'Horario de 6:00 a 22:00', 'Casillero diario']},
    {'nombre': 'Standard', 'precio': '120.00', 'duracion': 30, 'destacado': False,
     'beneficios': ['Todo lo del plan Básico', 'Clases grupales', 'Evaluación física mensual']},
    {'nombre': 'Premium', 'precio': '180.00', 'duracion': 30, 'destacado': True,
     'beneficios': ['Todo lo del plan Standard', 'Entrenador personalizado', 'Plan de entrenamiento a medida']},
]

MEMBRESIAS = [
    {'id': 1, 'cliente': 'David Lachira', 'plan': 'Premium', 'inicio': '2026-10-20', 'vencimiento': '2026-11-19', 'estado': 'Activa', 'dias': 9},
    {'id': 2, 'cliente': 'Odalis Domínguez', 'plan': 'Básico', 'inicio': '2026-10-12', 'vencimiento': '2026-11-11', 'estado': 'Activa', 'dias': 1},
    {'id': 3, 'cliente': 'Jorge Suárez', 'plan': 'Premium', 'inicio': '2026-10-25', 'vencimiento': '2026-11-24', 'estado': 'Activa', 'dias': 14},
    {'id': 4, 'cliente': 'Yarlequé Timaná', 'plan': 'Básico', 'inicio': '2026-09-05', 'vencimiento': '2026-10-05', 'estado': 'Vencida', 'dias': 0},
    {'id': 5, 'cliente': 'María López', 'plan': 'Standard', 'inicio': '2026-11-01', 'vencimiento': '2026-12-01', 'estado': 'Activa', 'dias': 21},
    {'id': 6, 'cliente': 'Carlos Fernández', 'plan': 'Premium', 'inicio': '2026-10-15', 'vencimiento': '2026-11-14', 'estado': 'Activa', 'dias': 4},
    {'id': 7, 'cliente': 'Lucía Martínez', 'plan': 'Básico', 'inicio': '2026-08-10', 'vencimiento': '2026-09-09', 'estado': 'Cancelada', 'dias': 0},
    {'id': 8, 'cliente': 'Pedro García', 'plan': 'Standard', 'inicio': '2026-10-30', 'vencimiento': '2026-11-29', 'estado': 'Activa', 'dias': 19},
    {'id': 9, 'cliente': 'Elena Torres', 'plan': 'Premium', 'inicio': '2026-11-05', 'vencimiento': '2026-12-05', 'estado': 'Activa', 'dias': 25},
]

POR_VENCER = [m for m in MEMBRESIAS if m['estado'] == 'Activa' and m['dias'] <= 7]

FACTURAS = [
    {'id': 'F001-0009', 'cliente': 'Elena Torres', 'monto': '180.00', 'fecha': '2026-11-05', 'estado': 'Emitida', 'concepto': 'Membresía Premium'},
    {'id': 'F001-0008', 'cliente': 'María López', 'monto': '120.00', 'fecha': '2026-11-01', 'estado': 'Emitida', 'concepto': 'Membresía Standard'},
    {'id': 'F001-0007', 'cliente': 'Pedro García', 'monto': '120.00', 'fecha': '2026-10-30', 'estado': 'Emitida', 'concepto': 'Membresía Standard'},
    {'id': 'F001-0006', 'cliente': 'Jorge Suárez', 'monto': '180.00', 'fecha': '2026-10-25', 'estado': 'Emitida', 'concepto': 'Membresía Premium'},
    {'id': 'F001-0005', 'cliente': 'David Lachira', 'monto': '180.00', 'fecha': '2026-10-20', 'estado': 'Emitida', 'concepto': 'Membresía Premium'},
    {'id': 'F001-0004', 'cliente': 'Carlos Fernández', 'monto': '180.00', 'fecha': '2026-10-15', 'estado': 'Emitida', 'concepto': 'Membresía Premium'},
    {'id': 'F001-0003', 'cliente': 'Odalis Domínguez', 'monto': '80.00', 'fecha': '2026-10-12', 'estado': 'Anulada', 'concepto': 'Membresía Básico'},
    {'id': 'F001-0002', 'cliente': 'Yarlequé Timaná', 'monto': '80.00', 'fecha': '2026-09-05', 'estado': 'Emitida', 'concepto': 'Membresía Básico'},
]

_ingresos = [('Jun', 4200), ('Jul', 4650), ('Ago', 4380), ('Sep', 5100), ('Oct', 5480), ('Nov', 3120)]
_max = max(v for _, v in _ingresos)
INGRESOS_MESES = [{'mes': m, 'monto': v, 'altura': round(v / _max * 100)} for m, v in _ingresos]

PROGRAMAS = [
    'Programa de Fuerza',
    'Programa de Resistencia',
    'Programa de Hipertrofia',
    'Programa de Pérdida de Peso',
    'Programa de Flexibilidad',
]

PLANES_ASIGNADOS = [
    {'id': 1, 'cliente': 'Carlos Fernández', 'programa': 'Programa de Fuerza', 'objetivos': 'Aumentar su masa muscular',
     'capacidades': 'Condiciones no tan buenas', 'frecuencia': 4, 'entrenador': 'Claudio Torres', 'fecha': '2026-10-15'},
    {'id': 2, 'cliente': 'Odalis Domínguez', 'programa': 'Programa de Resistencia', 'objetivos': 'Mejorar resistencia cardiovascular',
     'capacidades': 'Condición física regular', 'frecuencia': 3, 'entrenador': 'Claudio Torres', 'fecha': '2026-10-12'},
    {'id': 3, 'cliente': 'Elena Torres', 'programa': 'Programa de Pérdida de Peso', 'objetivos': 'Bajar 6 kg en tres meses',
     'capacidades': 'Sin lesiones, nivel principiante', 'frecuencia': 5, 'entrenador': 'Claudio Torres', 'fecha': '2026-11-05'},
    {'id': 4, 'cliente': 'Jorge Suárez', 'programa': 'Programa de Hipertrofia', 'objetivos': 'Ganar volumen en tren superior',
     'capacidades': 'Buena condición, experiencia previa', 'frecuencia': 5, 'entrenador': 'Claudio Torres', 'fecha': '2026-10-25'},
]

PROGRESO = [
    {'id': 1, 'cliente': 'Odalis Domínguez', 'fecha': '2026-11-02', 'peso': 50, 'repeticiones': 12, 'comentario': 'Buen progreso esta semana'},
    {'id': 2, 'cliente': 'Carlos Fernández', 'fecha': '2026-11-03', 'peso': 70, 'repeticiones': 10, 'comentario': 'Mejorar técnica'},
    {'id': 3, 'cliente': 'Elena Torres', 'fecha': '2026-11-04', 'peso': 30, 'repeticiones': 15, 'comentario': 'Incrementar peso la próxima sesión'},
    {'id': 4, 'cliente': 'Jorge Suárez', 'fecha': '2026-11-05', 'peso': 80, 'repeticiones': 8, 'comentario': 'Excelente fuerza en press de banca'},
]

CLIENTES_DEL_ENTRENADOR = [
    {'cliente': 'Carlos Fernández', 'objetivo': 'Aumentar su masa muscular', 'programa': 'Programa de Fuerza',
     'frecuencia': 4, 'ultimo': '2026-11-03'},
    {'cliente': 'Odalis Domínguez', 'objetivo': 'Mejorar resistencia cardiovascular', 'programa': 'Programa de Resistencia',
     'frecuencia': 3, 'ultimo': '2026-11-02'},
    {'cliente': 'Elena Torres', 'objetivo': 'Bajar 6 kg en tres meses', 'programa': 'Programa de Pérdida de Peso',
     'frecuencia': 5, 'ultimo': '2026-11-04'},
    {'cliente': 'Jorge Suárez', 'objetivo': 'Ganar volumen en tren superior', 'programa': 'Programa de Hipertrofia',
     'frecuencia': 5, 'ultimo': '2026-11-05'},
    {'cliente': 'María López', 'objetivo': 'Tonificar y mejorar postura', 'programa': 'Programa de Flexibilidad',
     'frecuencia': 3, 'ultimo': 'Sin registros'},
]

NOTIFICACIONES_ENVIADAS = [
    {'id': 1, 'destinatario': 'Odalis Domínguez', 'mensaje': 'Tu membresía vence mañana. Renueva en recepción para no perder tu acceso.', 'fecha': '2026-11-10'},
    {'id': 2, 'destinatario': 'Clientes con membresía por vencer', 'mensaje': 'Recuerda renovar tu membresía antes de la fecha de vencimiento.', 'fecha': '2026-11-09'},
    {'id': 3, 'destinatario': 'Todos los clientes', 'mensaje': 'El gimnasio atenderá en horario especial este feriado: 8:00 a 14:00.', 'fecha': '2026-11-06'},
]

# ---------- Datos del cliente (pantallas "Mi ...") ----------

MI_MEMBRESIA = {
    'plan': 'Premium', 'estado': 'Activa', 'precio': '180.00',
    'inicio': '2026-10-15', 'vencimiento': '2026-11-14', 'dias': 4, 'porcentaje': 87,
}

MI_PLAN = {
    'programa': 'Programa de Fuerza', 'objetivo': 'Aumentar su masa muscular', 'frecuencia': 4,
    'entrenador': 'Claudio Torres', 'desde': '2026-10-15',
    'rutina': [
        {'dia': 'Lunes', 'enfoque': 'Pecho y tríceps', 'ejercicios': 'Press plano, press inclinado, fondos, extensiones', 'series': '4 x 10'},
        {'dia': 'Martes', 'enfoque': 'Espalda y bíceps', 'ejercicios': 'Dominadas, remo con barra, curl con barra', 'series': '4 x 10'},
        {'dia': 'Jueves', 'enfoque': 'Pierna', 'ejercicios': 'Sentadilla, prensa, peso muerto rumano', 'series': '4 x 8'},
        {'dia': 'Viernes', 'enfoque': 'Hombros y abdomen', 'ejercicios': 'Press militar, elevaciones laterales, crunch', 'series': '3 x 12'},
    ],
}

_mi_prog = [('2026-10-20', 55, 10, 'Primera sesión, buena técnica'),
            ('2026-10-27', 60, 10, 'Subió carga sin problemas'),
            ('2026-11-03', 70, 10, 'Mejorar técnica'),
            ('2026-11-08', 75, 8, 'Gran avance en fuerza')]
_mp_max = max(p[1] for p in _mi_prog)
MI_PROGRESO = [{'fecha': f, 'peso': p, 'repeticiones': r, 'comentario': c, 'altura': round(p / _mp_max * 100)}
               for f, p, r, c in _mi_prog]

MIS_PAGOS = [
    {'id': 'F001-0004', 'concepto': 'Membresía Premium', 'monto': '180.00', 'fecha': '2026-10-15', 'estado': 'Emitida'},
    {'id': 'F001-0001', 'concepto': 'Membresía Premium', 'monto': '180.00', 'fecha': '2026-09-15', 'estado': 'Emitida'},
]

MIS_NOTIFICACIONES = [
    {'mensaje': 'Tu membresía vence en 4 días. Renueva en recepción para no perder tu acceso.', 'fecha': '2026-11-10', 'nueva': True},
    {'mensaje': 'Tu entrenador registró tu progreso de la semana. ¡Sigue así!', 'fecha': '2026-11-08', 'nueva': True},
    {'mensaje': 'El gimnasio atenderá en horario especial este feriado: 8:00 a 14:00.', 'fecha': '2026-11-06', 'nueva': False},
    {'mensaje': 'Bienvenido a SMART FIT. Tu plan de entrenamiento ya está disponible.', 'fecha': '2026-10-15', 'nueva': False},
]


# =====================================================================
#  Clases grupales y horarios de entrenadores
# =====================================================================

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
ENTRENADORES = ['Claudio Torres', 'Andrea Quispe', 'Marco Valdivia']

# (id, nombre, descripción, entrenador, fecha, hora, duración, capacidad, inscritos, estado, día)
_CLASES = [
    (1, 'Spinning', 'Ciclismo indoor de alta intensidad', 'Andrea Quispe', '2026-11-12', '07:00', 45, 15, 12, 'Programada', 'Jueves'),
    (2, 'Funcional', 'Circuito de fuerza y resistencia', 'Claudio Torres', '2026-11-12', '18:30', 60, 20, 20, 'Programada', 'Jueves'),
    (3, 'Yoga', 'Flexibilidad, respiración y relajación', 'Andrea Quispe', '2026-11-13', '08:00', 60, 12, 5, 'Programada', 'Viernes'),
    (4, 'Zumba', 'Baile aeróbico para toda la familia', 'Marco Valdivia', '2026-11-13', '19:00', 60, 25, 18, 'Programada', 'Viernes'),
    (5, 'Boxeo funcional', 'Técnica de golpeo y acondicionamiento', 'Claudio Torres', '2026-11-14', '10:00', 60, 15, 9, 'Programada', 'Sábado'),
    (6, 'Spinning', 'Ciclismo indoor de alta intensidad', 'Andrea Quispe', '2026-11-09', '07:00', 45, 15, 14, 'Finalizada', 'Lunes'),
    (7, 'Yoga', 'Flexibilidad, respiración y relajación', 'Andrea Quispe', '2026-11-10', '08:00', 60, 12, 4, 'Cancelada', 'Martes'),
]

CLASES_GRUPALES = []
for (_id, _nom, _desc, _ent, _fecha, _hora, _dur, _cap, _insc, _est, _dia) in _CLASES:
    _nombres = NOMBRES_CLIENTES[:min(_insc, 8)]
    _resto = _insc - len(_nombres)
    if _insc == 0:
        _texto = 'Sin inscritos'
    else:
        _texto = ', '.join(_nombres)
        if _resto > 0:
            _texto += f' y {_resto} más'
    CLASES_GRUPALES.append({
        'id': _id, 'nombre': _nom, 'descripcion': _desc, 'entrenador': _ent,
        'fecha': _fecha, 'hora': _hora, 'duracion': _dur, 'capacidad': _cap,
        'inscritos': _insc, 'cupos': _cap - _insc,
        'porcentaje': round(_insc / _cap * 100),
        'estado': _est, 'dia': _dia, 'inscritos_nombres': _texto,
    })

CALENDARIO = [
    {
        'dia': d,
        'clases': sorted(
            [{'hora': c['hora'], 'nombre': c['nombre'], 'entrenador': c['entrenador'], 'estado': c['estado']}
             for c in CLASES_GRUPALES if c['dia'] == d],
            key=lambda x: x['hora'],
        ),
    }
    for d in DIAS_SEMANA
]

# (id, entrenador, día, inicio, fin)
_HORARIOS = [
    (1, 'Claudio Torres', 'Lunes', '06:00', '14:00'),
    (2, 'Claudio Torres', 'Miércoles', '06:00', '14:00'),
    (3, 'Claudio Torres', 'Jueves', '14:00', '21:00'),
    (4, 'Claudio Torres', 'Sábado', '08:00', '13:00'),
    (5, 'Andrea Quispe', 'Lunes', '06:00', '12:00'),
    (6, 'Andrea Quispe', 'Martes', '06:00', '12:00'),
    (7, 'Andrea Quispe', 'Jueves', '06:00', '12:00'),
    (8, 'Andrea Quispe', 'Viernes', '06:00', '12:00'),
    (9, 'Marco Valdivia', 'Martes', '14:00', '21:00'),
    (10, 'Marco Valdivia', 'Viernes', '14:00', '21:00'),
    (11, 'Marco Valdivia', 'Sábado', '14:00', '20:00'),
]

HORARIOS = [
    {'id': i, 'entrenador': e, 'dia': d, 'inicio': ini, 'fin': fin}
    for i, e, d, ini, fin in sorted(_HORARIOS, key=lambda h: (ENTRENADORES.index(h[1]), DIAS_SEMANA.index(h[2]), h[3]))
]


def _celdas(entrenador):
    """Una lista de 7 textos (uno por día de la semana) para la tabla semanal."""
    celdas = []
    for d in DIAS_SEMANA:
        rango = ''
        for h in HORARIOS:
            if h['entrenador'] == entrenador and h['dia'] == d:
                rango = f"{h['inicio']} - {h['fin']}"
        celdas.append(rango)
    return celdas


HORARIO_GRID = [{'entrenador': e, 'celdas': _celdas(e)} for e in ENTRENADORES]

# Datos del entrenador que ha iniciado sesión (demostración: Claudio Torres)
MI_HORARIO = [{'dia': d, 'rango': r} for d, r in zip(DIAS_SEMANA, _celdas('Claudio Torres'))]
MIS_CLASES = [c for c in CLASES_GRUPALES if c['entrenador'] == 'Claudio Torres']

# Datos del cliente (demostración): clases con cupo y sus reservas
CLASES_CLIENTE = [
    dict(c, reservada=(c['id'] in (1, 5)), llena=(c['cupos'] <= 0))
    for c in CLASES_GRUPALES if c['estado'] == 'Programada'
]
