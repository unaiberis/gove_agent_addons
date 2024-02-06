odoo.define('custom_cart_module.create_cart_line_from_shop', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');

    // The rest of your code remains unchanged
    $(document).ready(function () {
        // Attach click event to your custom buttons
        $(document).on('click', '.js_add_cart_json', function (ev) {
            ev.preventDefault();

            var $button = $(ev.currentTarget);
            var sign = $button.data('sign');
            var productID = $button.data('product-id');
            var lineID = $button.data('line-id');
            var csrfToken = core.csrf_token;

            // Find the corresponding quantity input
            var $quantityInput = $('.js_quantity[data-line-id="' + lineID + '"]');

            var quantity = parseInt($quantityInput.text().trim());

            // Adjust the quantity based on the sign (plus or minus)
            if (sign === 'plus') {
                quantity += 1;
            } else if (sign === 'minus' && quantity > 0) {
                quantity -= 1;
            }

            console.log('lineID:', lineID);
            console.log('productID:', productID);
            console.log('quantity:', quantity);


            // Update the quantity input
            $quantityInput.text(quantity);

            // Log the data before making the POST request
            console.log('POST Data:', {
                'line_id': lineID,
                'product_id': productID,
                'set_qty': quantity,
                'csrf_token': csrfToken,
            });

            // Make a POST request to update the cart
            $.ajax({
                type: "POST",
                url: "/shop/cart/updatefromshop",
                data: {
                    'line_id': lineID,
                    'product_id': productID,
                    'set_qty': quantity,
                    'csrf_token': core.csrf_token,
                },
                dataType: 'json',
                success: function (data) {
                    console.log('Cart updated successfully:', data);
                },
                error: function (xhr, status, error) {
                    console.error('Error updating cart:', error);
                },
            });

        });

        // Attach click event to handle quantity buttons
        $(document).on('click', '.css_quantity .js_add_cart_json', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.css_quantity').find('.js_quantity');
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.text() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
            if (newQty !== previousQty) {
                $input.text(newQty).trigger('input');  // Trigger input event
            }
            return false;
        });

        // Attach input event to update the quantity input
        $(document).on('input', '.js_quantity', function () {
            var $quantityInput = $(this);
            var lineID = $quantityInput.data('line-id');
            var productID = $quantityInput.data('product-id');
            var quantity = parseInt($quantityInput.text().trim());

            // Log the updated quantity
            console.log('Updated Quantity:', quantity);

            // You can perform additional actions if needed
        });
    });

});
