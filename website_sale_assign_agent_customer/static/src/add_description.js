odoo.define('website_sale_assign_agent_customer.add_description', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');

    $(document).ready(function () {
        // Check if the current URL contains /shop/cart
        var isCartPage = window.location.pathname.indexOf('/shop/cart') !== -1;

        // Output the current URL to the console
        console.log('Current URL:', window.location.pathname);

        // Create the title div element
        var titleDiv = $('<div>', {
            text: 'Comentarios:',
            class: 'comments-title',
        });

        // Create the input element with a default value and placeholder
        var commentInput = $('<textarea>', {
            id: 'comment',
            name: 'comment',
            rows: 3,  // Set the number of visible rows
            cols: 78, // Set the number of visible columns
        });
        
        // Set the placeholder using the prop method
        commentInput.prop('placeholder', 'Escribe tu comentario aquí...');
        
        // Find the table with id 'cart_products'
        var cartProductsTable = $('#cart_products');

        // Create a form element
        var form = $('<form>', {
            action: "/shop/payment",
            method: "POST"
        });

        // Append the title div element to the form
        form.append(titleDiv);

        // Append the input element to the form
        form.append(commentInput);

        // Append the form just behind the 'cart_products' table if on a cart page
        if (isCartPage) {
            cartProductsTable.after(form);
        }

        // Find the "Pagar ahora" button by its class
        var pagarAhoraButton = $('.btn.btn-primary.float-right.d-none.d-xl-inline-block');

        // Add event listener to the "Pagar ahora" button
        pagarAhoraButton.on('click', function (event) {
            // Prevent the default link navigation
            event.preventDefault();
            
            // Log what is being written
            console.log('Texto en el cuadro de entrada:', commentInput.val());

            // Save the value using an AJAX request with CSRF token
            $.ajax({
                url: "/shop/payment",
                type: "POST",
                data: {
                    'comment_hidden': commentInput.val(),
                    'csrf_token': core.csrf_token,
                },
                success: function (result) {
                    // Handle success if needed
                    console.log('Request successful:', result);
                    
                    // If needed, manually navigate to the link href after processing
                    window.location.href = pagarAhoraButton.attr('href');
                },
                error: function (xhr, status, error) {
                    // Handle error if needed
                    console.error('Error:', error);
                },
            });
        });

        // Add event listener to update the hidden input with the comment value
        commentInput.on('input', function () {
            console.log('Texto en el cuadro de entrada:', commentInput.val());
        });
    });
});
