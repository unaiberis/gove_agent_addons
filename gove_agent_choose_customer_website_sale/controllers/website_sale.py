# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale_assign_agent_customer.controllers.website_sale import WebsiteSale


_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):
    @http.route()
    def payment_confirmation(self, **post):
        order = request.website.sale_get_order()

        if order.agent_customer.id:
            order.partner_id = order.agent_customer.id

        _logger.info(
            f"\n\nPAYMENT CONFIRMATION  User Name: {request.env.user.sudo().partner_id.name}\n"
        )
        self._check_payment_confirmation(create_mail_follower=True, **post)

        res = super().payment_confirmation(**post)

        request.env.user.partner_id.extra_computation_enabled = False

        return res

    @http.route()
    def payment(self):
        request.env.user.partner_id.extra_computation_enabled = True
        _logger.info(
            "\n\n RECOMPUTE COUPON LINES request.env.user.partner_id.extra_computation_enabled = True\n"
        )
        order = request.website.sale_get_order()

        if order.agent_customer.id:
            order.partner_id = order.agent_customer.id

        order.recompute_coupon_lines()

        return super().payment()

    def _check_payment_confirmation(
        self, order=None, create_mail_follower=False, **post
    ):
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

        if last_order and (
            not last_order_customer or last_order.id > last_order_customer.id
        ):
            order = self._update_order_info(order, last_order)
            order.agent_customer = int(
                request.env["agent.partner"]
                .sudo()
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                )
                .customer_id_chosen_by_agent
            )
            order.partner_id = request.env["res.partner"].browse(order.agent_customer)
            request.session["sale_last_order_id"] = order.id

            if create_mail_follower:
                self._handle_mail_follower_creation(order)

        elif last_order_customer:
            last_order_customer.agent_customer = agent_customer
            order = last_order_customer
            order.partner_id = request.env["res.partner"].browse(agent_customer)

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
        _logger.info(
            f"\n\nONCHANGE before partner User Name: {request.env.user.sudo().partner_id.name}\n"
        )
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
