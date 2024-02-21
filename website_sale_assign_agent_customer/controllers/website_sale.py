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
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.addons.website_sale_coupon_delivery.controllers.main import WebsiteSaleCouponDelivery



from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute

_logger = logging.getLogger(__name__)

class WebsiteSaleDelivery(WebsiteSaleDelivery):

    # If this function is not changed it raises a problem with delivery method
    # when there is a pricelist and update_pricelist is True
    @http.route()
    def update_eshop_carrier(self, **post):
        _logger.info("\n\nUPDATE ESHOP CARRIER 1 User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")

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
        _logger.info("\n\nUPDATE ESHOP CARRIER 2  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")

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
    def check_field_validations(self, values):
        res = super().check_field_validations(values=values)
        order = request.website.sale_get_order(force_create=1)

        if (
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        ):
            order.agent_customer = int(
                request.env["agent.partner"]
                .sudo()
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                )
                .customer_id_chosen_by_agent
            )
        else:
            res["error"] = True
        return res

    @http.route()
    def payment_confirmation(self, **post):
        _logger.info("\n\nPAYMENT CONFIRMATION  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")
        self._check_payment_confirmation(create_mail_follower=True, **post)

        return super().payment_confirmation(**post)

    @http.route()
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and "sale_last_order_id" in request.session:
                # Retrieve the last known order from the session if the session key `sale_order_id`
                # was prematurely cleared. This is done to prevent the user from updating their cart
                # after payment in case they don't return from payment through this route.
                last_order_id = request.session["sale_last_order_id"]
                order = request.env["sale.order"].sudo().browse(last_order_id).exists()
                _logger.info("\n\nValidate funcionamiento normal  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")
            # Nik jarrite
            elif request.env.user.sudo().partner_id.agent:
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
                if last_order:
                    order = last_order
                    _logger.info(f"\n\nValidate Ultimo order creado {order}  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")

            elif not request.env.user.sudo().partner_id.agent:
                last_order_id = request.session["sale_last_order_id"]
                order = request.env["sale.order"].sudo().browse(last_order_id).exists()
                _logger.info(
                    "\n\nValidate elif not request.env.user.sudo().partner_id.agent:  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
                )

        else:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            assert order.id == request.session.get("sale_last_order_id")

        if transaction_id:
            tx = request.env["payment.transaction"].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect("/shop")

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == "draft":
            return request.redirect("/shop")

        PaymentProcessing.remove_payment_transaction(tx)
        return request.redirect("/shop/confirmation")

    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        add_qty = int(post.get("add_qty", 1))
        Category = request.env["product.public.category"]
        if category:
            category = Category.search([("id", "=", int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post["ppg"] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env["website"].get_current_website().shop_ppg or 20

        ppr = request.env["website"].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist("attrib")
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL(
            "/shop",
            category=category and int(category),
            search=search,
            attrib=attrib_list,
            order=post.get("order"),
        )

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(
            request.context, pricelist=pricelist.id, partner=request.env.user.partner_id
        )

        if request.env.user.sudo().partner_id.agent:
            agent_customer_id, agent_customers = self._get_agent_customer_from_url(
                **post
            )

            pricelist = (
                self._set_pricelist_from_current_agent_customer(
                    agent_customer_id, agent_customers
                )
                or pricelist
            )

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post["attrib"] = attrib_list

        Product = request.env["product.template"].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [("parent_id", "=", False)] + website_domain
        if search:
            search_categories = Category.search(
                [("product_tmpl_ids", "in", search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(("id", "in", search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=ppg, scope=5, url_args=post
        )
        offset = pager["offset"]
        products = search_product[offset : offset + ppg]

        ProductAttribute = request.env["product.attribute"]
        if products:
            # get all products without limit
            attributes = ProductAttribute.search(
                [("product_tmpl_ids", "in", search_product.ids)]
            )
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get("website_sale_shop_layout_mode")
        if not layout_mode:
            if request.website.viewref("website_sale.products_list_view").active:
                layout_mode = "list"
            else:
                layout_mode = "grid"

        values = {
            "search": search,
            "order": post.get("order", ""),
            "category": category,
            "attrib_values": attrib_values,
            "attrib_set": attrib_set,
            "pager": pager,
            "pricelist": pricelist,
            "add_qty": add_qty,
            "products": products,
            "search_count": product_count,  # common for all searchbox
            "bins": TableCompute().process(products, ppg, ppr),
            "ppg": ppg,
            "ppr": ppr,
            "categories": categs,
            "attributes": attributes,
            "keep": keep,
            "search_categories_ids": search_categories.ids,
            "layout_mode": layout_mode,
        }
        if category:
            values["main_object"] = category

        if pricelist:
            _logger.info("\n\n PRICELIST %s, PRICELIST NAME %s  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n", pricelist, pricelist.name)

        # Get the selected customer object based on agent_customer_id
        selected_customer_id = (
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        )
        selected_customer = (
            request.env["res.partner"].sudo().browse(selected_customer_id)
        )
        # Update the values dictionary with the selected customer's name
        values["selected_customer"] = selected_customer

        website_sale_order = request.website.sale_get_order()
        if website_sale_order:
            values["website_sale_order"] = website_sale_order

        return request.render("website_sale.products", values)

    @http.route("/shop/update_customer", type="http", auth="public", website=True)
    def update_customer(self, **kw):
        # Retrieve the selected agent_customer value from the form data
        agent_customer_id = kw.get("agent_customer")

        redirect_url = "/shop?agent_customer_id=%s" % agent_customer_id

        return request.redirect(redirect_url)

    @http.route()
    def cart(self, access_token=None, revive="", **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """

        # GET CUSTOMER PRICELIST
        agent_customers = request.env.user.sudo().partner_id.agent_customers
        pricelist = False

        # Get the pricelist and partner based on the agent_customer_id
        agent_customer_id = (
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        )
        if agent_customer_id and agent_customer_id in agent_customers.ids:
            partner = request.env["res.partner"].browse(agent_customer_id)
            property_name = "property_product_pricelist"

            ir_property = (
                request.env["ir.property"]
                .sudo()
                .search(
                    [
                        ("name", "=", property_name),
                        ("res_id", "=", f"res.partner,{partner.id}"),
                    ],
                    limit=1,
                )
            )

            if ir_property and ir_property.value_reference:
                # Parse the value_reference to get the pricelist number
                pricelist_number = int(ir_property.value_reference.split(",")[1])
                pricelist = request.env["product.pricelist"].browse(pricelist_number)

        if pricelist:
            order = request.website.sale_get_order(
                force_pricelist=pricelist.id, update_pricelist=True
            )
        else:
            order = request.website.sale_get_order()

        if order and order.state != "draft":
            request.session["sale_order_id"] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = (
                request.env["sale.order"]
                .sudo()
                .search([("access_token", "=", access_token)], limit=1)
            )
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != "draft":  # abandoned cart already finished
                values.update({"abandoned_proceed": True})
            elif revive == "squash" or (
                revive == "merge" and not request.session.get("sale_order_id")
            ):  # restore old cart or merge with unexistant
                request.session["sale_order_id"] = abandoned_order.id
                return request.redirect("/shop/cart")
            elif revive == "merge":
                abandoned_order.order_line.write(
                    {"order_id": request.session["sale_order_id"]}
                )
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get(
                "sale_order_id"
            ):  # abandoned cart found, user have to choose what to do
                values.update({"access_token": abandoned_order.access_token})

        # Nik jarrittekue
        selected_customer_id = (
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        )
        # Nik aldautekue
        values.update(
            {
                "website_sale_order": order,
                "date": fields.Date.today(),
                "suggested_products": [],
                "selected_customer": request.env["res.partner"]
                .sudo()
                .browse(selected_customer_id),
            }
        )
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get("pricelist"):
                _order = order.with_context(pricelist=pricelist)
            values["suggested_products"] = _order._cart_accessories()

        if post.get("type") == "popover":
            # force no-cache so IE11 doesn't cache this XHR
            return request.render(
                "website_sale.cart_popover",
                values,
                headers={"Cache-Control": "no-cache"},
            )

        return request.render("website_sale.cart", values)

    @http.route()
    def payment(self, **post):

        self._check_payment_confirmation(**post)

        return super().payment(**post)

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
            _logger.info(
                f"\n\n Last order en _check_payment_confirmation {last_order} {request.env.user.partner_id} {last_order.name} User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
            )
            if not order or order and order.id < last_order.id:
                order = last_order

                request.session["sale_last_order_id"] = order.id

                _logger.info(
                    f"\n\n if not order siendo cliente _check_payment_confirmation {last_order} {last_order.name} {request.env.user.partner_id} User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
                )

            else:
                _logger.info(
                    f"\n\n if not order else siendo cliente _check_payment_confirmation {order} {order.name} {request.env.user.partner_id} User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
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
                    f"\n\n AGENT LAST_ORDER (not last_order_customer or last_order.id > last_order_customer.id) {order} {order.name}  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
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
                    f"\n\n SALE LAST ORDER ID request.session['sale_last_order_id'] = {request.session.get('sale_last_order_id')}, Order Name: {request.env['sale.order'].sudo().browse(request.session.get('sale_last_order_id')).name} User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
                )


                if create_mail_follower:
                    order.partner_id = order.agent_customer.id
                    _logger.info("\n\nONCHANGE antes del partner User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")
                    order.onchange_partner_id()
                    order.user_id = request.env.user.id
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
                            f"\n\n MAIL FOLLOWER Se ha creado mail follower asegurando que no existía: {new_follower}  User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n"
                        )

            elif last_order_customer:
                last_order_customer.agent_customer = _agent_customer

                _logger.info(f"\n\nlast_order_customer {last_order_customer} {last_order_customer.name} User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")

    def _empty_cart_before_changing_customer(self):
        _logger.info("\n\nEMPTY CART hecho User Name: {request.env.user.sudo().partner_id.name if request.env.user.sudo().partner_id}\n")
        order = request.website.sale_get_order(force_create=1)
        order_line = request.env["sale.order.line"].sudo()
        line_ids = order_line.search([("order_id", "=", order.id)])
        for line in line_ids:
            line_obj = order_line.browse([int(line)])
            if line_obj:
                line_obj.unlink()

    def _get_agent_customer_from_url(self, **post):
        # Initialize variable to False
        agent_customer_id = False

        # Get the agent customers associated with the current user
        agent_customers = request.env.user.sudo().partner_id.agent_customers

        # Check if the agent is trying to change the customer
        if post.get("agent_customer_id") and (
            (request.website.sale_get_order())
            or (not request.website.sale_get_order())
            or int(post.get("agent_customer_id")) == 0
        ):
            # Get the chosen agent customer ID from the post data
            agent_customer_id = int(post.get("agent_customer_id"))

            # Get the agent partner record for the current user
            customer_id_chosen_by_agent_record = (
                request.env["agent.partner"]
                .sudo()
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                )
            )

            # Check if the chosen agent customer is valid
            if (
                agent_customer_id
                and agent_customers
                and agent_customer_id in agent_customers.ids
                or agent_customer_id == 0
            ):
                # Check if there is a record for the agent's chosen customer
                if customer_id_chosen_by_agent_record:
                    # If the customer chosen is different and the cart is not empty, empty it
                    if (
                        agent_customer_id
                        != customer_id_chosen_by_agent_record.customer_id_chosen_by_agent
                    ):
                        # Empty the cart before changing the customer
                        self._empty_cart_before_changing_customer()

                    # Update the agent's chosen customer in the record
                    customer_id_chosen_by_agent_record.write(
                        {
                            "agent_id": request.env.user.sudo().partner_id.id,
                            "customer_id_chosen_by_agent": agent_customer_id,
                        }
                    )
                else:
                    # If no record exists and the cart is empty, create a new record
                    if request.website.sale_get_order().cart_quantity != 0:
                        # If the cart is not empty, empty it
                        self._empty_cart_before_changing_customer()

                    request.env["agent.partner"].sudo().create(
                        {
                            "agent_id": request.env.user.sudo().partner_id.id,
                            "customer_id_chosen_by_agent": agent_customer_id,
                        }
                    )

        elif (
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1).exists()
        ):
            agent_customer_id = int(
                request.env["agent.partner"]
                .sudo()
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                ).customer_id_chosen_by_agent

            )

        # Return agent_customer_id and agent_customers
        return agent_customer_id, agent_customers

    def _set_pricelist_from_current_agent_customer(
        self, agent_customer_id, agent_customers
    ):
        # Get the partner associated with the current user
        partner = request.env.user.partner_id

        # Update the 'customer_selected_by_agent' field in the partner record
        if "customer_selected_by_agent" in partner:
            # Assuming 'agent_customer_id' is the desired value
            partner.write({"customer_selected_by_agent": agent_customer_id})

        # Get the pricelist and partner based on the agent_customer_id
        if agent_customer_id and agent_customer_id in agent_customers.ids:
            # Retrieve the partner using the agent_customer_id
            partner = request.env["res.partner"].browse(agent_customer_id)

            # Define the property name for the pricelist in partner's properties
            property_name = "property_product_pricelist"

            # Search for the property related to the pricelist in the partner's properties
            ir_property = (
                request.env["ir.property"]
                .sudo()
                .search(
                    [
                        ("name", "=", property_name),
                        ("res_id", "=", f"res.partner,{partner.id}"),
                    ],
                    limit=1,
                )
            )

            # Check if the ir_property exists and has a value_reference
            if ir_property and ir_property.value_reference:
                # Parse the value_reference to get the pricelist number
                pricelist_number = int(ir_property.value_reference.split(",")[1])

                # Retrieve the pricelist using the pricelist number
                pricelist = request.env["product.pricelist"].browse(pricelist_number)

                # Check if both partner and pricelist are available
                if partner and pricelist:
                    # Update the request context with the pricelist and partner information
                    request.context = dict(
                        request.context, pricelist=pricelist.id, partner=partner
                    )
                    return pricelist
