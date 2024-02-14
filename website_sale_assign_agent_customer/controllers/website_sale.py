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

from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute


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
        print("\n\nPAYMENT CONFIRMATION\n\n")
        res = super().payment_confirmation(**post)
        
        # We want always to go to the sale confirmation in the end
        # template = 'website_sale.confirmation'
        # location = '/es/shop/confirmation'
        # if res.qcontext.get('response_template') is None:
        #     res.qcontext['response_template'] = 'website_sale.confirmation'

        order = res.qcontext.get("order")

        # if not order:
#             return res
        if not request.env.user.partner_id.agent:
            last_order = (
                request.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", request.env.user.partner_id.id),
                    ],
                    order="id desc", #leno "date_order desc" zeon
                    limit=1,
                )
            )
            print("\nLast order etten", last_order, request.env.user.partner_id,"\n")
            if not order:
                order = last_order

                res.qcontext["order"] = last_order

                return request.render("website_sale.confirmation", {'order': order})
            else:
                return res

        _agent_customer = int(
            request.env["agent.partner"]
            .sudo()
            .search([("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1)
            .customer_id_chosen_by_agent
        )

        if order:
            order.agent_customer = _agent_customer
        
        if not request.env.user.partner_id.agent:

            order.partner_id = order.agent_customer.id
            order.onchange_partner_id()
            order.user_id = request.env.user.id

            # Check if follower exists becuase you cant create a new one with the same res_model, res_id and partner_id
            existing_follower = request.env["mail.followers"].search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order.id),
                    ("partner_id", "=", order.agent_customer.id),
                ]
            )

            print("\n\nExisting follower", existing_follower, order, "\n\n")

            if not existing_follower:
                # No existe, puedes crear el nuevo registro
                new_follower = request.env["mail.followers"].create(
                    {
                        "res_model": "sale.order",
                        "res_id": order.id,
                        "partner_id": order.agent_customer.id,
                    }
                )
                print("\n\n Etzun existitzen ta sortu da: ",new_follower," \n\n")
        
        elif request.env.user.sudo().partner_id.agent:
            user_id = request.env.user.id

            user = request.env["res.users"].sudo().browse(user_id)
            partner_id = user.partner_id.id

            
            # Find the last sale order for the given partner_id
            last_order = (
                request.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", partner_id),
                    ],
                    order="id desc", #leno "date_order desc" zeon
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
                    order="id desc", #leno "date_order desc" zeon
                    limit=1,
                )
            )
            if last_order and (not last_order_customer or last_order.id > last_order_customer.id):
                order = last_order
                print("\n\nAzkeneko order sortute", order, "\n\n")
                order.agent_customer = int(
                    request.env["agent.partner"]
                    .sudo()
                    .search(
                        [("agent_id", "=", request.env.user.sudo().partner_id.id)],
                        limit=1,
                    )
                    .customer_id_chosen_by_agent
                )
                order.partner_id = order.agent_customer.id
                print("\n\nOnchange partner aurretik\n\n")
                order.onchange_partner_id()
                order.user_id = request.env.user.id


                new_follower2 = request.env["mail.followers"].create(
                    {
                        "res_model": "sale.order",
                        "res_id": order.id,
                        "partner_id": order.agent_customer.id,
                    }
                )
                print("\n\n Etzun existitzen ta sortu da2: ",new_follower2," \n\n")
                res.qcontext["order"] = order
                
                return request.render("website_sale.confirmation", {'order': order})
                
            elif last_order_customer:
                res.qcontext["order"] = last_order_customer
                print("\n\nRES qcontext",res.qcontext["order"],"\n\n")
                return request.render("website_sale.confirmation", {'order': last_order_customer})


        print("\n\nAZKENEKO RES qcontext",res.qcontext["order"],"\n\n")
        return res

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
            elif request.env.user.sudo().partner_id.agent:
                user_id = request.env.user.id

                user = request.env["res.users"].sudo().browse(user_id)
                partner_id = user.partner_id.id

                # Find the last sale order for the given partner_id
                last_order = (
                    request.env["sale.order"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", partner_id),
                        ],
                        order="id desc", #leno "date_order desc" zeon
                        limit=1,
                    )
                )
                if last_order:
                    order = last_order
                    print("\n\nAzkeneko order sortute", order, "\n\n")
            
            elif not order:
                order = (
                    request.env["sale.order"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", request.env.user.sudo().partner_id.id),
                        ],
                        order="id desc", #leno "date_order desc" zeon
                        limit=1,
                    )
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

            self._set_pricelist_from_current_agent_customer(
                agent_customer_id, agent_customers
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

        # Retrieve the comment from the post data
        comment = post.get("comment_hidden")

        # Save the comment in the sale order if order_comments is empty
        sale_order = request.website.sale_get_order()
        if sale_order and post:  # and not sale_order.order_comments:
            sale_order.write({"order_comments": comment})

        return super().payment(**post)

    @http.route(
        "/shop/cart/getcurrentsaleorder",
        type="http",
        auth="public",
        website=True,
        csrf=False,
    )
    def _get_current_saleorder(self, **post):

        return request.website.sale_get_order().order_comments

    # PRUEBATAKO KONTROLADORIE
    # @http.route('/shop/cart/updatefromshop', type='http', auth="public", website=True)
    # def update_cart_from_shop(self, line_id, product_id, set_qty, csrf_token, **kwargs):
    #     """
    #     Update the cart based on the provided parameters.

    #     :param line_id: Line ID of the cart item to update.
    #     :param product_id: Product ID of the cart item.
    #     :param set_qty: New quantity for the cart item.
    #     :param csrf_token: CSRF token for security.
    #     :param kwargs: Additional parameters.

    #     :return: JSON response indicating the success or failure of the update.
    #     """
    #     # Ensure CSRF token is valid for security
    #     WebsiteSale()._check_csrf_token(csrf_token)

    #     # Convert IDs to integers
    #     line_id = int(line_id)
    #     product_id = int(product_id)
    #     set_qty = int(set_qty)

    #     # Get the cart and update the specified line
    #     order = request.website.sale_get_order()
    #     order_line = order.order_line.filtered(lambda line: line.id == line_id and line.product_id.id == product_id)

    #     if order_line:
    #         order_line.write({'product_uom_qty': set_qty})
    #         return {'success': True, 'message': 'Cart updated successfully'}
    #     else:
    #         return {'success': False, 'message': 'Cart item not found'}

    def _empty_cart_before_changing_customer(self):
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
