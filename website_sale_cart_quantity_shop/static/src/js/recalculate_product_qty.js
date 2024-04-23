// Copyright 2024 Unai Beristain - AvanzOSC
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
odoo.define("website_sale_cart_quantity_shop.recalculate_product_qty", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleUtils = require("website_sale.utils");

    // Define a flag to track if an RPC call is in progress
    let rpcInProgress = false;

    function isCategoryPage() {
        const url = window.location.href;
        return url.includes("/category/") || (url.includes("/shop") && !url.includes("/shop/")) || url.includes("/shop/page/");
    }

    if (isCategoryPage()) {
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
            oldValue: 0,
            newValue: 0,

            start: function () {
                this._super.apply(this, arguments);
                var self = this;

                function debounce(func, delay) {
                    let timeoutId;
                    return function (...args) {
                        clearTimeout(timeoutId);
                        timeoutId = setTimeout(() => {
                            func.apply(this, args);
                        }, delay);
                    };
                }


                // Variables para acumular los incrementos y decrementos
                var totalIncrement = 0;
                var totalDecrement = 0;

                // Debounce function for handleButtonClick
                const debounceHandleButtonClick = debounce(function (inputField, increment, event) {
                    self.modifiedInputField = inputField;
                    self.oldValue = parseInt(inputField.val()) || 0;
                    self.newValue = Math.max(self.oldValue + increment, 0);
                    inputField.data('oldValue', self.newValue);
                    self.custom_add_qty = increment;
                    self.changeTriggeredByButton = true;
                    self._onClickAdd(event);

                    // Reset totalIncrement and totalDecrement to zero after handling the click
                    totalIncrement = 0;
                    totalDecrement = 0;
                }, 300);

                // Click event handler for the plus button
                $(".fa.fa-plus").parent().click(function (event) {
                    event.preventDefault();
                    totalIncrement += 1;
                    const inputField = $(this).parent().siblings("input.form-control.quantity");
                    debounceHandleButtonClick(inputField, totalIncrement - totalDecrement, event);
                });

                // Click event handler for the minus button
                $(".fa.fa-minus").parent().click(function (event) {
                    event.preventDefault();
                    totalDecrement += 1;
                    const inputField = $(this).parent().siblings("input.form-control.quantity");
                    debounceHandleButtonClick(inputField, totalIncrement - totalDecrement, event);
                });

                $("input.form-control.quantity").on("change", function (event) {
                    self.modifiedInputField = $(this);

                    if (!self.changeTriggeredByButton) {
                        self.oldValue = $(this).data('oldValue') || 0;
                        self.newValue = parseInt($(this).val().replace(',', '.')) || 0;

                        if (self.newValue < 0 || isNaN(self.newValue)) {
                            self.newValue = 0;
                        }

                        $(this).val(self.newValue);
                        $(this).data('oldValue', self.newValue);
                        self.custom_add_qty = self.newValue - self.oldValue;
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
                this._super.apply(this, arguments);
            },

            _submitForm: function () {
                if (rpcInProgress) {
                    console.log("An RPC call is already in progress. Skipping this call.");
                    return Promise.resolve();
                }

                rpcInProgress = true;

                const self = this;
                const params = this.rootProduct;
                params.add_qty = this.custom_add_qty;

                const $inputField = this.modifiedInputField;

                params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
                params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);

                if (this.isBuyNow) {
                    params.express = true;
                }

                return this._rpc({
                    route: "/shop/cart/update_json_from_shop",
                    params: params,
                }).then((data) => {
                    self.oldValue = parseInt($inputField.val()) || 0;
                    self.newValue = parseInt(data.product_cart_qty) || 0;
                    $inputField.data('oldValue', self.newValue);
                    $inputField.val(self.newValue);
                    self.changeTriggeredByButton = false;

                    if (data.product_cart_qty == data.product_available_qty && data.product_cart_qty != 0) {
                        $inputField.css({
                            "color": "white",
                            "background-color": "black",
                            "font-weight": "bold",
                        });
                    } else {
                        $inputField.css({
                            "color": "black",
                            "background-color": "white",
                            "font-weight": "normal"
                        });
                    }

                    wSaleUtils.updateCartNavBar(data);
                    const $navButton = $("header .o_wsale_my_cart").parent();
                    let el = $();
                    if (self.pageType === "product") {
                        el = $("#o-carousel-product");
                    }
                    if (self.pageType === "products") {
                        el = self.targetEl.parents(".o_wsale_product_grid_wrapper");
                    }
                    wSaleUtils.animateClone($navButton, el, 25, 40);

                    rpcInProgress = false;
                }).catch((error) => {
                    console.error("Error occurred during RPC call:", error);
                    rpcInProgress = false;
                });
            },
        });
    }
});
