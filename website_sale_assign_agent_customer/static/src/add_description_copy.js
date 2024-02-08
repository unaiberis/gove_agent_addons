odoo.define('website_sale_assign_agent_customer.add_description_copy', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');

    // Variables para almacenar elementos DOM reutilizables
    var commentInput = $('#comment');
    var pagarAhoraButton = $('.btn.btn-primary.float-right.d-none.d-xl-inline-block');

    // Función para inicializar el formulario
    function initializeForm() {
        var isCartPage = window.location.pathname.indexOf('/shop/cart') !== -1;
        var cartProductsTable = $('#cart_products');

        if (isCartPage) {
            var form = createForm();
            cartProductsTable.after(form);
            getOrderData();
        }
    }

    // Función para crear el elemento del formulario
    function createForm() {
        var form = $('<form>', {
            action: "/shop/payment",
            method: "POST"
        });

        form.append($('<div>', {
            text: 'Comentarios:',
            class: 'comments-title',
        }));

        var commentInput = $('<textarea>', {
            id: 'comment',
            name: 'comment',
            rows: 3,
            cols: 78,
            placeholder: 'Escribe tu comentario aquí...',
        });

        form.append(commentInput);
        return form;
    }

    // Función para manejar la solicitud AJAX para obtener los datos del pedido
    function getOrderData() {
        $.ajax({
            url: "/shop/cart/getcurrentsaleorder",
            type: "GET",
            dataType: "text",
            success: function (result) {
                var responseText = result || '';
                updateCommentInput(responseText);
            },
            error: function (xhr, status, error) {
                console.error('Error in AJAX request:', error);
            }
        });
    }

    // Función para actualizar el valor del campo de comentario
    function updateCommentInput(value) {
        commentInput.val(value);
    }

    // Agregar event listener para actualizar el valor oculto con el valor del comentario
    commentInput.on('input', function () {
        console.log('Texto en el cuadro de entrada:', commentInput.val());
        saveCommentValue(commentInput.val());
    });

    // Función para guardar el valor del comentario utilizando la solicitud AJAX con el token CSRF
    function saveCommentValue(value) {
        $.ajax({
            url: "/shop/payment",
            type: "POST",
            data: {
                'comment_hidden': value,
                'csrf_token': core.csrf_token,
            },
            success: function (result) {
                // Si es necesario, navegar manualmente al enlace href después de procesar
                console.log('Request successful:', result);
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
            },
        });
    }

    // Inicializar el formulario y agregar el event listener al botón "Pagar ahora"
    $(document).ready(function () {
        initializeForm();
        pagarAhoraButton.on('click', function (event) {
            event.preventDefault();
            window.location.href = pagarAhoraButton.attr('href');
        });
    });
});
