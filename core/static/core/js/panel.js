// SMART FIT - comportamiento común de las pantallas del panel
document.addEventListener('DOMContentLoaded', () => {
    const $$ = (selector, raiz = document) => Array.from(raiz.querySelectorAll(selector));

    // Copia los data-* de una fila de tabla a los campos (name) y textos (data-texto) de una ventana modal
    function llenarDesdeFila(dialogo, fila) {
        $$('[name]', dialogo).forEach((campo) => {
            const valor = fila.dataset[campo.name];
            if (valor !== undefined) campo.value = valor;
        });
        $$('[data-texto]', dialogo).forEach((el) => {
            const valor = fila.dataset[el.dataset.texto];
            if (valor !== undefined) el.textContent = valor;
        });
    }

    // Abrir una ventana modal (si el botón está dentro de una fila, la rellena con sus datos)
    $$('[data-abrir]').forEach((boton) => {
        boton.addEventListener('click', () => {
            const dialogo = document.getElementById(boton.dataset.abrir);
            const fila = boton.closest('tr');
            if (fila) llenarDesdeFila(dialogo, fila);
            dialogo.showModal();
        });
    });

    // Botones de la barra superior que actúan sobre la fila seleccionada
    $$('[data-fila-accion]').forEach((boton) => {
        boton.addEventListener('click', () => {
            const tabla = document.getElementById(boton.dataset.tabla);
            const fila = tabla.querySelector('tbody tr.seleccionada');
            if (!fila) {
                alert('Primero selecciona una fila de la tabla.');
                return;
            }
            const dialogo = document.getElementById(boton.dataset.filaAccion);
            llenarDesdeFila(dialogo, fila);
            dialogo.showModal();
        });
    });

    // Cerrar ventanas modales (botón Cancelar o clic fuera)
    $$('[data-cerrar]').forEach((boton) => {
        boton.addEventListener('click', () => boton.closest('dialog').close());
    });
    $$('dialog.modal').forEach((dialogo) => {
        dialogo.addEventListener('click', (e) => {
            if (e.target === dialogo) dialogo.close();
        });
    });

    // Selección de filas
    $$('.tabla-seleccionable tbody tr').forEach((fila) => {
        fila.addEventListener('click', () => {
            const yaSeleccionada = fila.classList.contains('seleccionada');
            $$('tr.seleccionada', fila.parentElement).forEach((f) => f.classList.remove('seleccionada'));
            if (!yaSeleccionada) fila.classList.add('seleccionada');
        });
    });

    // Buscador de tablas
    $$('[data-filtrar]').forEach((campo) => {
        campo.addEventListener('input', () => {
            const tabla = document.getElementById(campo.dataset.filtrar);
            const texto = campo.value.toLowerCase();
            $$('tbody tr', tabla).forEach((fila) => {
                fila.hidden = !fila.textContent.toLowerCase().includes(texto);
            });
        });
    });

    // Confirmación antes de enviar (anular, cancelar, etc.)
    $$('form[data-confirmar]').forEach((formulario) => {
        formulario.addEventListener('submit', (e) => {
            if (!confirm(formulario.dataset.confirmar)) e.preventDefault();
        });
    });

    // Plantillas rápidas de mensaje
    $$('[data-plantilla]').forEach((boton) => {
        boton.addEventListener('click', () => {
            const caja = document.getElementById('mensaje');
            if (caja) caja.value = boton.dataset.plantilla;
        });
    });

    // Imprimir / guardar como PDF
    $$('[data-imprimir]').forEach((boton) => {
        boton.addEventListener('click', () => window.print());
    });

    // Fecha de hoy por defecto
    $$('input[type="date"][data-hoy]').forEach((campo) => {
        if (!campo.value) campo.value = new Date().toLocaleDateString('en-CA');
    });
});
