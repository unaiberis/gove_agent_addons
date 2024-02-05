odoo.define('your_module_name.create_cart_line_from_shop', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var websiteSale = require('website_sale');

    websiteSale.include({
        events: _.extend({}, websiteSale.events, {
            'click a.js_add_cart_json': '_onClickAddCartJson',
        }),

        // Function to handle the click event for quantity buttons
        _onClickAddCartJson: function (ev) {
            ev.preventDefault();

            var $button = $(ev.currentTarget);
            var sign = $button.data('sign');
            var productID = $button.data('product-id');

            var $quantityInput = $button.siblings('.js_quantity');
            var quantity = parseInt($quantityInput.text().trim());

            // Adjust the quantity based on the sign (plus or minus)
            if (sign === 'plus') {
                quantity += 1;
            } else if (sign === 'minus' && quantity > 0) {
                quantity -= 1;
            }

            // Update the quantity input
            $quantityInput.text(quantity);

            // Log the data before making the POST request
            console.log('POST Data:', {
                'line_id': $quantityInput.data('line-id'),
                'product_id': productID,
                'set_qty': quantity,
                'csrf_token': core.csrf_token,
            });

            // Make a POST request to update the cart
            $.post('/shop/cart/update', {
                'line_id': $quantityInput.data('line-id'),
                'product_id': productID,
                'set_qty': quantity,
                'csrf_token': core.csrf_token, // Include CSRF token in the request
            }).done(function (data) {
                // Handle the response if needed
                console.log('Cart updated successfully:', data);
            }).fail(function (xhr, status, error) {
                // Handle the error if needed
                console.error('Error updating cart:', error);
            });
        },
    });

});
