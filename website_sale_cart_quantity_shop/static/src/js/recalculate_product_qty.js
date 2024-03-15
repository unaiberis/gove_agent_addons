odoo.define("website_sale_cart_quantity_shop.recalculate_product_qty", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleUtils = require("website_sale.utils");
    const ajax = require('web.ajax');

    $(document).ready(function () {
        $("input.form-control.quantity").each(function () {
            var newValue = parseInt($(this).val().replace(',', '.')) || 0;
            $(this).val(newValue);
            $(this).data('oldValue', newValue); // Guardar el valor inicial como oldValue
        });
    });

    publicWidget.registry.WebsiteSale.include({
        custom_add_qty: 0, // Definir custom_add_qty como propiedad de WebsiteSale
        changeTriggeredByButton: false, // Bandera para indicar si el cambio fue provocado por los botones

        start: function () {
            this._super.apply(this, arguments);

            var self = this;

            var modifiedInputField; // Definir una variable para almacenar el campo de entrada modificado


            $(".fa.fa-plus, .fa.fa-minus, input.form-control.quantity").on("change", function (event) {
                if ($(this).hasClass("quantity")) { // Verificar si el cambio ocurrió en el campo de cantidad
                    modifiedInputField = $(this); // Almacenar una referencia al campo de entrada modificado
                } else { // Si no es el campo de cantidad, puede ser fa-plus o fa-minus
                    var inputField = $(this).parent().siblings("input.form-control.quantity");
                    modifiedInputField = inputField;
                }
                $(".fa.fa-plus").parent().click(function (event) {
                    // Evitar el comportamiento predeterminado del enlace
                    event.preventDefault();
                    var inputField = $(this).parent().siblings("input.form-control.quantity");
                    var oldValue = inputField.data('oldValue') || 0;
                    var newValue = oldValue + 1;
                    inputField.val(newValue);
                    inputField.data('oldValue', newValue);
                    self.custom_add_qty = 1; // Asignar 1 para el botón de más
                    self.changeTriggeredByButton = true; // Establecer la bandera como verdadera

                    console.log("Plus Button Clicked:");
                    console.log("Old Value:", oldValue);
                    console.log("New Value:", newValue);
                    console.log("Custom Add Qty:", self.custom_add_qty);
                    console.log("Change Triggered By Button:", self.changeTriggeredByButton);

                    // Llamar a _onClickAdd con el botón como argumento
                    self._onClickAdd(event);
                });

                // Modificar el evento click del botón .fa.fa-minus
                $(".fa.fa-minus").parent().click(function (event) {
                    // Evitar el comportamiento predeterminado del enlace
                    event.preventDefault();
                    var inputField = $(this).parent().siblings("input.form-control.quantity");
                    var oldValue = inputField.data('oldValue') || 0;
                    var newValue = Math.max(oldValue - 1, 0);
                    inputField.val(newValue);
                    inputField.data('oldValue', newValue);
                    self.custom_add_qty = -1; // Asignar -1 para el botón de menos
                    self.changeTriggeredByButton = true; // Establecer la bandera como verdadera

                    console.log("Minus Button Clicked:");
                    console.log("Old Value:", oldValue);
                    console.log("New Value:", newValue);
                    console.log("Custom Add Qty:", self.custom_add_qty);
                    console.log("Change Triggered By Button:", self.changeTriggeredByButton);

                    // Llamar a _onClickAdd con el botón como argumento
                    self._onClickAdd(event);
                });


                $("input.form-control.quantity").change(function (event) {
                    if (!self.changeTriggeredByButton) { // Verificar si el cambio no fue provocado por los botones
                        var oldValue = $(this).data('oldValue') || 0;
                        var newValue = parseInt($(this).val().replace(',', '.')) || 0;

                        if (newValue < 0 || isNaN(newValue)) {
                            newValue = 0;
                        }

                        $(this).val(newValue);

                        console.log("Old Value: " + oldValue);
                        console.log("New Value: " + newValue);

                        $(this).data('oldValue', newValue);

                        self.custom_add_qty = newValue - oldValue; // Calcular la cantidad personalizada

                        console.log("Custom Add Qty: " + self.custom_add_qty);

                        // Llamar a _onClickAdd con el botón como argumento
                        self._onClickAdd(event);
                    } else {
                        self.changeTriggeredByButton = false; // Restablecer la bandera a falso para futuros cambios
                    }
                });
            });


        },

        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onClickAdd: function (ev) {
            this.isDynamic = true;
            this.pageType = $(ev.currentTarget).data("page-type");
            this.targetEl = $(ev.currentTarget);
            return this._super.apply(this, arguments);
        },

        /**
         * Add custom variant values and attribute values that do not generate variants
         * in the form data and trigger submit.
         *
         * @private
         * @returns {Promise} never resolved
         */
        _submitForm: function () {
            const pageType = this.pageType;
            const params = this.rootProduct;
            params.add_qty = this.custom_add_qty; // Utilizar this.custom_add_qty

            console.log("Params: " + JSON.stringify(params));

            params.product_custom_attribute_values = JSON.stringify(
                params.product_custom_attribute_values
            );
            params.no_variant_attribute_values = JSON.stringify(
                params.no_variant_attribute_values
            );

            if (this.isBuyNow) {
                console.log("Buy now is true.");
                params.express = true;
            }

            this._rpc({
                route: "/shop/cart/update_json_from_shop",
                params: params,
            }).then((data) => {
                console.log("Data received from RPC call:", data);

                var $inputField = modifiedInputField; // Usar la variable modifiedInputField
                var oldValue = parseInt($inputField.val().replace(',', '.')) || 0;
                var currentQuantity = parseInt(data.product_cart_qty) || 0;

                var newValue = Math.min(oldValue, currentQuantity);
                $inputField.val(newValue);

                console.log("Input Field:", $inputField);
                console.log("Old Value:", oldValue);
                console.log("Current Quantity:", currentQuantity);
                console.log("New Value:", newValue);

                wSaleUtils.updateCartNavBar(data);
                const $navButton = $("header .o_wsale_my_cart").parent();
                let el = $();
                if (pageType === "product") {
                    console.log("Page type is product.");
                    el = $("#o-carousel-product");
                }
                if (pageType === "products") {
                    console.log("Page type is products.");
                    el = this.targetEl.parents(".o_wsale_product_grid_wrapper");
                }
                console.log("Element selected:", el);
                wSaleUtils.animateClone($navButton, el, 25, 40);
            }).catch((error) => {
                console.error("Error occurred during RPC call:", error);
            });




        },
    });
});