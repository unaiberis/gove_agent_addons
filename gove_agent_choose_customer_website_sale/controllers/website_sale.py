# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime

from odoo import fields, http
from odoo.http import request

from odoo.addons.website_sale_assign_agent_customer.controllers.website_sale import WebsiteSale
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.addons.website_sale_coupon_delivery.controllers.main import WebsiteSaleCouponDelivery


_logger = logging.getLogger(__name__)

class WebsiteSaleDelivery(WebsiteSaleDelivery):

    # If this function is not changed it raises a problem with delivery method
    # when there is a pricelist and update_pricelist is True
    @http.route()
    def update_eshop_carrier(self, **post):
        _logger.info(f"\n\nUPDATE ESHOP CARRIER 1 User Name: {request.env.user.sudo().partner_id.name}\n")

        order = request.website.sale_get_order_without_updating_pricelist()
        carrier_id = int(post['carrier_id'])
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
        return self._update_website_sale_delivery_return(order, **post)


class WebsiteSaleCouponDelivery(WebsiteSaleCouponDelivery):

    # If this function is not changed it raises a problem with delivery method
    # when there is a pricelist and update_pricelist is True
    @http.route()
    def update_eshop_carrier(self, **post):
        _logger.info(f"\n\nUPDATE ESHOP CARRIER 2  User Name: {request.env.user.sudo().partner_id.name}\n")

        Monetary = request.env['ir.qweb.field.monetary']
        result = super(WebsiteSaleCouponDelivery, self).update_eshop_carrier(**post)
        order = request.website.sale_get_order()
        free_shipping_lines = None

        if order:
            order.recompute_coupon_lines()
            order.validate_taxes_on_sales_order()
            free_shipping_lines = order._get_free_shipping_lines()

        if free_shipping_lines:
            currency = order.currency_id
            amount_free_shipping = sum(free_shipping_lines.mapped('price_subtotal'))
            result.update({
                'new_amount_delivery': Monetary.value_to_html(0.0, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'new_amount_order_discounted': Monetary.value_to_html(order.reward_amount - amount_free_shipping, {'display_currency': currency}),
            })
        return result



class WebsiteSale(WebsiteSale):
    
    @http.route()
    def payment_confirmation(self, **post):
        _logger.info(f"\n\nPAYMENT CONFIRMATION  User Name: {request.env.user.sudo().partner_id.name}\n")
        self._check_payment_confirmation(create_mail_follower=True, **post)

        res = super().payment_confirmation(**post)

        request.env.user.partner_id.extra_computation_enabled = False
        
        return res

    
    @http.route('/enable/extra/coupon/computation', type='json', auth='public')
    def enable_extra_coupon_computation(self, **kw):
        # Lógica para llamar a la función recompute_coupon_lines()
        request.env.user.partner_id.extra_computation_enabled = True
        _logger.info("\n\n RECOMPUTE COUPON LINES request.env.user.partner_id.extra_computation_enabled = True\n")

        return request.env.user.partner_id.extra_computation_enabled

    def _check_payment_confirmation(self, order=None, create_mail_follower=False, **post):
        is_agent = request.env.user.partner_id.agent
        _logger.info(f"\n\n CHECK PAYMENT CONFIRMATION is_agent: {is_agent}\n")

        if not is_agent:
            order = self._get_last_order_for_customer(order)

        elif is_agent:
            order = self._get_last_order_for_agent(order, create_mail_follower)

            if order and create_mail_follower:
                self._handle_mail_follower_creation(order)

        return order

    def _get_last_order_for_customer(self, order=None):
        last_order = (
            request.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", request.env.user.partner_id.id),
                    ("agent_customer", "=", False),
                ],
                order="id desc",
                limit=1,
            )
        )

        self._update_order_info(order, last_order)

        return order

    def _get_last_order_for_agent(self, order=None, create_mail_follower=False):
        agent_customer = int(
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        )

        partner_id = request.env.user.partner_id.id

        last_order = (
            request.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner_id),
                ],
                order="id desc",
                limit=1,
            )
        )

        last_order_customer = (
            request.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", agent_customer),
                ],
                order="id desc",
                limit=1,
            )
        )

        if last_order and (not last_order_customer or last_order.id > last_order_customer.id):
            order = self._update_order_info(order, last_order)
            order.agent_customer = int(
                request.env["agent.partner"]
                .sudo()
                .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
                .customer_id_chosen_by_agent
            )
            request.session["sale_last_order_id"] = order.id

            if create_mail_follower:
                self._handle_mail_follower_creation(order)

        elif last_order_customer:
            last_order_customer.agent_customer = agent_customer

            _logger.info(
                f"\n\n last_order_customer {last_order_customer} {last_order_customer.name} User Name: {request.env.user.sudo().partner_id.name}\n"
            )

        return order

    def _update_order_info(self, order, last_order):
        _logger.info(
            f"\n\n Last order in _check_payment_confirmation {last_order} {request.env.user.partner_id} {last_order.name} User Name: {request.env.user.sudo().partner_id.name}\n"
        )

        if not order or (order and order.id < last_order.id):
            order = last_order
            request.session["sale_last_order_id"] = order.id

        return order

    def _handle_mail_follower_creation(self, order):
        order.partner_id = order.agent_customer.id
        _logger.info(f"\n\nONCHANGE before partner User Name: {request.env.user.sudo().partner_id.name}\n")
        order.onchange_partner_id()
        order.user_id = request.env.user.id
        # Tipo = Pedido Surf
        order.type_id = 2

        existing_follower = request.env["mail.followers"].search(
            [
                ("res_model", "=", "sale.order"),
                ("res_id", "=", order.id),
                ("partner_id", "=", order.agent_customer.id),
            ]
        )

        if not existing_follower:
            new_follower = request.env["mail.followers"].create(
                {
                    "res_model": "sale.order",
                    "res_id": order.id,
                    "partner_id": order.agent_customer.id,
                }
            )

            _logger.info(
                f"\n\n MAIL FOLLOWER Created, ensuring it didn't exist: {new_follower} Buyer: {order.agent_customer.name} User Name: {request.env.user.sudo().partner_id.name}\n"
            )
