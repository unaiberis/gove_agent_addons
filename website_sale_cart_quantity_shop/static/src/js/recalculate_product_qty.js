odoo.define("website_sale_cart_quantity_shop.recalculate_product_qty", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleUtils = require("website_sale.utils");
    const ajax = require('web.ajax');

    $(document).ready(function () {
        $("input.form-control.quantity").each(function () {
            var newValue = parseInt($(this).val().replace(',', '.')) || 0;
            $(this).val(newValue);
            $(this).data('oldValue', newValue);
        });
    });

    publicWidget.registry.WebsiteSale.include({
        custom_add_qty: 0,
        changeTriggeredByButton: false,
        modifiedInputField: null,

        start: function () {
            this._super.apply(this, arguments);

            var self = this;

            $(".fa.fa-plus").parent().click(function (event) {
                event.preventDefault();
                var inputField = $(this).parent().siblings("input.form-control.quantity");
                self.modifiedInputField = inputField;

                var oldValue = parseInt(inputField.val()) || 0;
                var newValue = oldValue + 1;
                inputField.data('oldValue', newValue);
                self.custom_add_qty = 1;
                self._onClickAdd(event);
            });

            $(".fa.fa-minus").parent().click(function (event) {
                event.preventDefault();
                var inputField = $(this).parent().siblings("input.form-control.quantity");
                self.modifiedInputField = inputField;

                var oldValue = parseInt(inputField.val()) || 0;
                var newValue = Math.max(oldValue - 1, 0);
                inputField.data('oldValue', newValue);
                self.custom_add_qty = -1;
                self._onClickAdd(event);
            });

            $("input.form-control.quantity").on("change", function (event) {
                self.modifiedInputField = $(this);

                if (!self.changeTriggeredByButton) {
                    var oldValue = $(this).data('oldValue') || 0;
                    var newValue = parseInt($(this).val().replace(',', '.')) || 0;

                    if (newValue < 0 || isNaN(newValue)) {
                        newValue = 0;
                    }

                    $(this).val(newValue);
                    $(this).data('oldValue', newValue);

                    self.custom_add_qty = newValue - oldValue;
                    self._onClickAdd(event);
                } else {
                    self.changeTriggeredByButton = false;
                }
            });
        },

        _onClickAdd: function (ev) {
            this.isDynamic = true;
            this.pageType = $(ev.currentTarget).data("page-type");
            this.targetEl = $(ev.currentTarget);
            return this._super.apply(this, arguments);
        },

        _submitForm: function () {
            const pageType = this.pageType;
            const params = this.rootProduct;
            params.add_qty = this.custom_add_qty;

            var $inputField = this.modifiedInputField;

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
                route: "/shop/cart/update_json_from_shop",
                params: params,
            }).then((data) => {
                var currentQuantity = parseInt(data.product_cart_qty) || 0;
                $inputField.val(currentQuantity);
                self.changeTriggeredByButton = true;

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
            }).catch((error) => {
                console.error("Error occurred during RPC call:", error);
            });
        },
    });
});
