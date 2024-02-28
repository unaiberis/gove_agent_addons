odoo.define('gove_agent_choose_customer_website_sale.recalculate_coupon_lines', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {
        'use strict';

        $("button#o_payment_form_pay").bind("click", function(ev) {
            // Llama al controlador correcto /enable/extra/coupon/computation
            ajax.jsonRpc("/enable/extra/coupon/computation", 'call', {
                method: 'enable_extra_coupon_computation',
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
