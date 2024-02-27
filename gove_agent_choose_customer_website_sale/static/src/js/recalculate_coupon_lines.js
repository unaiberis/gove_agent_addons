odoo.define('gove_agent_choose_customer_website_sale.recalculate_coupon_lines', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {
        'use strict';

        $("button#o_payment_form_pay").bind("click", function(ev) {
            // Llama a la función de Python recompute_coupon_lines()
            ajax.jsonRpc("/recompute_coupon_lines_checkout", 'call', {
                method: 'recompute_coupon_lines',
                // Puedes enviar parámetros si es necesario
                // params: {
                //     // tus parámetros aquí
                // }
            }).then(function(result) {
                // Maneja la respuesta si es necesario
                console.log(result);
            });
        });
    });
});