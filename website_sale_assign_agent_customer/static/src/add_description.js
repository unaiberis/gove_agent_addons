odoo.define('website_sale_assign_agent_customer.add_description', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');

    // Function to initialize the form
    function initializeForm() {
        var isCartPage = window.location.pathname.indexOf('/shop/cart') !== -1;
        var cartProductsTable = $('#cart_products');

        if (isCartPage) {
            var form = createForm();
            cartProductsTable.after(form);
            // Use standard AJAX request to get order data when the page loads
            getOrderData();
        }


    }

    // Function to create the form element
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

    // Function to handle AJAX request for order data
    function getOrderData() {
        $.ajax({
            url: "/shop/cart/getcurrentsaleorder",
            type: "GET",
            dataType: "text",
            success: function (result) {
                console.log('Response from get_current_saleorder:', result);

                // Check if result is defined and has responseText property
                var responseText = result || '';

                // Update the comment input
                updateCommentInput(responseText);
            },
            error: function (xhr, status, error) {
                console.error('Error in AJAX request:', error);
            }
        });
    }


    // Function to update the comment input value
    function updateCommentInput(value) {
        var commentInput = $('#comment');
        commentInput.val(value);
    }

    $(document).ready(function () {
        initializeForm();

        // Find the "Pagar ahora" button by its class
        var pagarAhoraButton = $('.btn.btn-primary.float-right.d-none.d-xl-inline-block');

        // Add event listener to the "Pagar ahora" button
        pagarAhoraButton.on('click', function (event) {
            // Prevent the default link navigation
            event.preventDefault();

            // Log what is being written
            var commentInput = $('#comment');
            console.log('Texto en el cuadro de entrada:', commentInput.val());

            // Save the value using an AJAX request with CSRF token
            saveCommentValue(commentInput.val());
        });

        // Add event listener to update the hidden input with the comment value
        $('#comment').on('input', function () {
            var commentInput = $('#comment');
            console.log('Texto en el cuadro de entrada:', commentInput.val());
        });

        // Function to save the comment value using AJAX request with CSRF token
        function saveCommentValue(value) {
            console.log(value)
            $.ajax({
                url: "/shop/payment",
                type: "POST",
                data: {
                    'comment_hidden': value,
                    'csrf_token': core.csrf_token,
                },
                success: function (result) {
                    // console.log('Request successful:', result);
                    // If needed, manually navigate to the link href after processing
                    window.location.href = pagarAhoraButton.attr('href');
                },
                error: function (xhr, status, error) {
                    // console.error('Error:', error);

                },
            });
        }
    });
});
