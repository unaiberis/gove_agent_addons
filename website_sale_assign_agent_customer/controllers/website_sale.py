###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route()
    def check_field_validations(self, values):
        res = super().check_field_validations(values=values)
        order = request.website.sale_get_order(force_create=1)
        if not order or "agent_customer" not in values:
            return res
        # order.agent_customer = int(values["agent_customer"])
        agent_customer_value = values["agent_customer"]

        if agent_customer_value:
            order.agent_customer = int(agent_customer_value)
        else:
            # Raise a UserError with a custom message
            raise UserError("Por favor, elija a un cliente antes de continuar.")
        return res

    @http.route()
    def payment_confirmation(self, **post):
        res = super().payment_confirmation(**post)
        order = res.qcontext["order"]
        if not order or not request.env.user.partner_id.agent:
            return res
        if not order.agent_customer:
            return res
        order.partner_id = order.agent_customer
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
    def shop(self, **post):

        partner = request.env.user.partner_id
        
        res_partner_id_string = 'res.partner,' + str(partner.id)

        property = request.env["ir.property"].sudo().search([('name', '=', 'property_product_pricelist'),('res_id', '=', res_partner_id_string)])

        pricelist = property.value_reference
    
        res = super().shop(**post)

    
        if pricelist:
            pricelist_number = int(pricelist.split(',')[1])

            partner.property_product_pricelist = pricelist_number

            public_pricelist = request.env['product.pricelist'].search([('id', '=', 1)])

            # Extract pricelist ID and store it in the session
            public_pricelist_id = public_pricelist.id
            request.session.update({'website_sale_current_pl': pricelist_number, 'public_pricelist_id': public_pricelist_id})


            # Update the context with additional variables
            res.qcontext.update({
                'public_pricelist_id': public_pricelist_id,
                # Add other variables if needed
            })

        return res


        # order = request.website.sale_get_order(force_create=1)        
