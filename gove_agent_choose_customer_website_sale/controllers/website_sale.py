# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.osv import expression

from odoo.addons.website_sale_assign_agent_customer.controllers.website_sale import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    def _check_payment_confirmation(
        self, order=None, create_mail_follower=False, **post
    ):
        if not request.env.user.partner_id.agent:
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
            # Tipo = Pedido Surf
            last_order.type_id = 2
            
            _logger.info(
                f"\n\n Last order en _check_payment_confirmation {last_order} {request.env.user.partner_id} {last_order.name} User Name: {request.env.user.sudo().partner_id.name}\n"
            )
            if not order or order and order.id < last_order.id:
                order = last_order

                request.session["sale_last_order_id"] = order.id

                _logger.info(
                    f"\n\n if not order siendo cliente _check_payment_confirmation {last_order} {last_order.name} {request.env.user.partner_id} User Name: {request.env.user.sudo().partner_id.name}\n"
                )

            else:
                _logger.info(
                    f"\n\n if not order else siendo cliente _check_payment_confirmation {order} {order.name} {request.env.user.partner_id} User Name: {request.env.user.sudo().partner_id.name}\n"
                )

        elif request.env.user.sudo().partner_id.agent:
            _agent_customer = int(
                request.env["agent.partner"]
                .sudo()
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                )
                .customer_id_chosen_by_agent
            )

            partner_id = request.env.user.partner_id.id

            # Find the last sale order for the given partner_id
            last_order = (
                request.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", partner_id),
                    ],
                    order="id desc",  # leno "date_order desc" zeon
                    limit=1,
                )
            )

            last_order_customer = (
                request.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", _agent_customer),
                    ],
                    order="id desc",  # leno "date_order desc" zeon
                    limit=1,
                )
            )
            if last_order and (
                not last_order_customer or last_order.id > last_order_customer.id
            ):
                order = last_order
                _logger.info(
                    f"\n\n AGENT LAST_ORDER (not last_order_customer or last_order.id > last_order_customer.id) {order} {order.name}  User Name: {request.env.user.sudo().partner_id.name}\n"
                )
                order.agent_customer = int(
                    request.env["agent.partner"]
                    .sudo()
                    .search(
                        [("agent_id", "=", request.env.user.sudo().partner_id.id)],
                        limit=1,
                    )
                    .customer_id_chosen_by_agent
                )
                request.session["sale_last_order_id"] = order.id
                _logger.info(
                    f"\n\n SALE LAST ORDER ID request.session['sale_last_order_id'] = {request.session.get('sale_last_order_id')}, Order Name: {request.env['sale.order'].sudo().browse(request.session.get('sale_last_order_id')).name} User Name: {request.env.user.sudo().partner_id.name}\n"
                )


                if create_mail_follower:
                    order.partner_id = order.agent_customer.id
                    _logger.info(f"\n\nONCHANGE antes del partner User Name: {request.env.user.sudo().partner_id.name}\n")
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
                            f"\n\n MAIL FOLLOWER Se ha creado asegurando que no existía: {new_follower} Comprador: {order.agent_customer.name} User Name: {request.env.user.sudo().partner_id.name}\n"
                        )

            elif last_order_customer:
                last_order_customer.agent_customer = _agent_customer

                _logger.info(f"\n\nlast_order_customer {last_order_customer} {last_order_customer.name} User Name: {request.env.user.sudo().partner_id.name}\n")