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

    _agent_customer_id = False
    _pricelist = False

    
    def check_field_validations(self, values):
        res = super().check_field_validations(values=values)
        order = request.website.sale_get_order(force_create=1)

        if request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent:
            order.agent_customer = int(request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent)
        else:
            res['error'] = True                   
        return res

    @http.route()
    def payment_confirmation(self, **post):
        res = super().payment_confirmation(**post)
        order = res.qcontext["order"]
        order.agent_customer = int(request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent)
        if not order or not request.env.user.partner_id.agent:
            return res
        if not order.agent_customer:
            return res
        order.partner_id = order.agent_customer.id
        order.onchange_partner_id()
        order.user_id = request.env.user.id
        request.env["mail.followers"].create(
            {
                "res_model": "sale.order",
                "res_id": order.id,
                "partner_id": order.agent_customer.id,
            }
        )
        return res

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
                  
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        agent_customer_id = False

        agent_customers = request.env.user.sudo().partner_id.agent_customers

        # There are items in the cart dont let changing agent customers because that't an error. It has to empty the cart
        # to be able to change the customer
        if post.get('agent_customer_id') and (
            (request.website.sale_get_order() and request.website.sale_get_order().cart_quantity == 0) or
            (not request.website.sale_get_order())
        ):

            agent_customer_id = int(post.get('agent_customer_id'))


            customer_id_chosen_by_agent_record = request.env['agent.partner'].sudo().search([], limit=1)

            if agent_customer_id and agent_customers and agent_customer_id in agent_customers.ids or agent_customer_id == 0:
                if customer_id_chosen_by_agent_record:
                    customer_id_chosen_by_agent_record.write({'customer_id_chosen_by_agent': agent_customer_id})
                else:
                    request.env['agent.partner'].sudo().create({'customer_id_chosen_by_agent': agent_customer_id})


            self._agent_customer_id = agent_customer_id


            partner = request.env.user.partner_id

            if 'customer_selected_by_agent' in partner:
                # Assuming 'self._agent_customer_id' is the desired value
                partner.write({'customer_selected_by_agent': self._agent_customer_id})

        # else:
        #     customer_id_chosen_by_agent_record = request.env['agent.partner'].sudo().search([], limit=1)

        #     if customer_id_chosen_by_agent_record:
        #         customer_id_chosen_by_agent_record.write({'customer_id_chosen_by_agent': 0})


        # Get the pricelist and partner based on the agent_customer_id
        if self._agent_customer_id and self._agent_customer_id in agent_customers.ids:
            partner = request.env['res.partner'].browse(self._agent_customer_id)
            property_name = 'property_product_pricelist'

            ir_property = request.env['ir.property'].sudo().search([
                ('name', '=', property_name),
                ('res_id', '=', f'res.partner,{partner.id}'),
            ], limit=1)

            if ir_property and ir_property.value_reference:
                # Parse the value_reference to get the pricelist number
                pricelist_number = int(ir_property.value_reference.split(',')[1])
                pricelist = request.env['product.pricelist'].browse(pricelist_number)
                self._pricelist = pricelist

                if partner and pricelist:
                    request.context = dict(request.context, pricelist=pricelist.id, partner=partner)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=5, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'order': post.get('order', ''),
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        
        # Get the selected customer object based on agent_customer_id
        selected_customer_id = request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent
        selected_customer = request.env['res.partner'].sudo().browse(selected_customer_id)
        # Update the values dictionary with the selected customer's name
        values['selected_customer'] = selected_customer
        
        website_sale_order = request.website.sale_get_order()
        if website_sale_order:
            values['website_sale_order'] = website_sale_order

        return request.render("website_sale.products", values)
    
    @http.route('/shop/update_customer', type='http', auth="public", website=True)
    def update_customer(self, **kw):
        # Retrieve the selected agent_customer value from the form data
        agent_customer_id = kw.get('agent_customer')

        redirect_url = '/shop?agent_customer_id=%s' % agent_customer_id

        return request.redirect(redirect_url)  
    
    @http.route()
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        
        # GET CUSTOMER PRICELIST
        agent_customers = request.env.user.sudo().partner_id.agent_customers
        # Get the pricelist and partner based on the agent_customer_id

        self._agent_customer_id = request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent
        if self._agent_customer_id and self._agent_customer_id in agent_customers.ids:
            partner = request.env['res.partner'].browse(self._agent_customer_id)
            property_name = 'property_product_pricelist'

            ir_property = request.env['ir.property'].sudo().search([
                ('name', '=', property_name),
                ('res_id', '=', f'res.partner,{partner.id}'),
            ], limit=1)

            if ir_property and ir_property.value_reference:
                # Parse the value_reference to get the pricelist number
                pricelist_number = int(ir_property.value_reference.split(',')[1])
                pricelist = request.env['product.pricelist'].browse(pricelist_number)
                self._pricelist = pricelist

        if self._pricelist:
            order = request.website.sale_get_order(force_pricelist=self._pricelist.id,update_pricelist=True)
        else:
            order = request.website.sale_get_order()

        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})
        

        selected_customer_id = request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
            'selected_customer': request.env['res.partner'].sudo().browse(selected_customer_id),

        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):

                _order = order.with_context(pricelist=self._pricelist)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.cart", values)
