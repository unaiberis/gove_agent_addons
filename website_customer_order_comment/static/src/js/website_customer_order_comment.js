odoo.define("website_customer_order_comment.payment", function (require) {
  "use strict";

  var ajax = require("web.ajax");

  $(document).ready(function () {
    $("button#o_payment_form_pay").bind("click", function () {
      var customer_comment = $("#customer_comment").val();
      ajax.jsonRpc("/shop/customer_comment/", "call", {
        comment: customer_comment,
      });
    });
  });
});
