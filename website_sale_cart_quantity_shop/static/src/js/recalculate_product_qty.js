// Copyright 2024 Unai Beristain - AvanzOSC
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
        modifiedInputField: null, // Declare modifiedInputField outside the start function
        oldValue: 0,
        newValue: 0,

        start: function () {
            this._super.apply(this, arguments);

            var self = this;

            $(".fa.fa-plus").parent().click(function (event) {
                // Evitar el comportamiento predeterminado del enlace
                event.preventDefault();
                var inputField = $(this).parent().siblings("input.form-control.quantity");
                self.modifiedInputField = inputField;

                self.oldValue = parseInt(inputField.val()) || 0;
                self.newValue = self.oldValue + 1;
                //inputField.val(newValue);
                inputField.data('oldValue', self.newValue);
                self.custom_add_qty = 1; // Asignar 1 para el botón de más
                self.changeTriggeredByButton = true; // Establecer la bandera como verdadera

                // Llamar a _onClickAdd con el botón como argumento
                self._onClickAdd(event);
            });

            // Modificar el evento click del botón .fa.fa-minus
            $(".fa.fa-minus").parent().click(function (event) {
                // Evitar el comportamiento predeterminado del enlace
                event.preventDefault();
                var inputField = $(this).parent().siblings("input.form-control.quantity");
                self.modifiedInputField = inputField;

                self.oldValue = parseInt(inputField.val()) || 0;
                self.newValue = Math.max(self.oldValue - 1, 0);
                //inputField.val(newValue);
                inputField.data('oldValue', self.newValue);
                self.custom_add_qty = -1; // Asignar -1 para el botón de menos
                self.changeTriggeredByButton = true; // Establecer la bandera como verdadera

                console.log("Minus Button Clicked4:");
                console.log("Old Value4:", self.oldValue);
                console.log("New Value4:", self.newValue);
                console.log("Custom Add Qty4:", self.custom_add_qty);
                console.log("Change Triggered By Button4:", self.changeTriggeredByButton);

                // Llamar a _onClickAdd con el botón como argumento
                self._onClickAdd(event);
            });


            $("input.form-control.quantity").on("change", function (event) {
                // Almacenar una referencia al campo de entrada modificado
                self.modifiedInputField = $(this);

                if (!self.changeTriggeredByButton) {
                    self.oldValue = $(this).data('oldValue') || 0;
                    self.newValue = parseInt($(this).val().replace(',', '.')) || 0;

                    if (self.newValue < 0 || isNaN(self.newValue)) {
                        self.newValue = 0;
                    }

                    $(this).val(self.newValue);

                    console.log("Old Value5: " + self.oldValue);
                    console.log("New Value5: " + self.newValue);

                    $(this).data('oldValue', self.newValue);

                    self.custom_add_qty = self.newValue - self.oldValue; // Calcular la cantidad personalizada

                    console.log("Custom Add Qty5: " + self.custom_add_qty);

                    // Llamar a _onClickAdd con el botón como argumento
                    self._onClickAdd(event);
                } else {
                    self.changeTriggeredByButton = false; // Restablecer la bandera a falso para futuros cambios
                }
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

            var $inputField = this.modifiedInputField; // Usar la variable modifiedInputField


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

                self.oldValue = parseInt($inputField.val()) || 0;
                self.newValue = parseInt(data.product_cart_qty) || 0;
                $inputField.data('oldValue', self.newValue);

                $inputField.val(self.newValue);
                self.changeTriggeredByButton = true; // It is needed not to enter in the !self.changeTriggeredByButton if

                if (data.product_cart_qty == data.product_available_qty && data.product_cart_qty != 0) {
                    $inputField.css({
                        "color": "white",
                        "background-color": "black",
                        "font-weight": "bold"
                    });
                }
                else {
                    $inputField.css({
                        "color": "black",
                        "background-color": "white",
                        "font-weight": "normal"
                    });
                }

                console.log("Input Field6:", $inputField);
                console.log("Current Quantity6:", self.newValue);

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
                wSaleUtils.animateClone($navButton, el, 25, 40);
            }).catch((error) => {
                console.error("Error occurred during RPC call:", error);
            });
        },
    });
});