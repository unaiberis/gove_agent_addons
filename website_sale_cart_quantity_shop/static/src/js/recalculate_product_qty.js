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
                params.express = true;
            }
            this._rpc({
                route: "/shop/cart/ajaxify_update_json",
                params: params,
            }).then((data) => {
                wSaleUtils.updateCartNavBar(data);
                const $navButton = $("header .o_wsale_my_cart").parent();
                let el = $();
                if (pageType === "product") {
                    el = $("#o-carousel-product");
                }
                if (pageType === "products") {
                    el = this.targetEl.parents(".o_wsale_product_grid_wrapper");
                }
                wSaleUtils.animateClone($navButton, el, 25, 40);
            });
        },
    });
});
