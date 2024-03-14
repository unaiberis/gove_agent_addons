odoo.define("website_sale_cart_quantity_shop.recalculate_product_qty", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleUtils = require("website_sale.utils");
    const ajax = require('web.ajax');

    $(document).ready(function () {
        $("input.form-control.quantity").each(function () {
            var newValue = parseInt($(this).val().replace(',', '.')) || 0;
            $(this).val(newValue);
        });

        $(".fa.fa-plus").parent().click(function () {
            console.log('Se ha hecho clic en el div con la clase "fa fa-plus"');
        });

        $(".fa.fa-minus").parent().click(function () {
            console.log('Se ha hecho clic en el div con la clase "fa fa-minus"');
        });

        $("input.form-control.quantity").change(function () {
            var oldValue = $(this).data('oldValue') || 0;
            var newValue = parseInt($(this).val().replace(',', '.')) || 0;

            if (newValue < 0 || isNaN(newValue)) {
                newValue = 0;
            }

            $(this).val(newValue);

            change_in_qty(oldValue, newValue);

            $(this).data('oldValue', newValue);
        });
    });

    function change_in_qty(oldValue, newValue) {
        console.log("Valor anterior: " + oldValue + ", Nuevo valor: " + newValue);
    }

    publicWidget.registry.WebsiteSale.include({
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onClickAdd: function (ev) {
            this.isDynamic = Boolean($(ev.currentTarget).data("is-dynamic"));
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
            if (!this.isDynamic) {
                return this._super.apply(this, arguments);
            }
            const pageType = this.pageType;
            const params = this.rootProduct;
            params.add_qty = params.quantity;

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
    // Obtener todos los elementos con la clase "fa fa-plus"
    const plusIcons = document.querySelectorAll(".fa.fa-plus");

    // Agregar un event listener a cada icono de más
    plusIcons.forEach(function (plusIcon) {
        plusIcon.addEventListener("click", _handleClick);
    });

});
