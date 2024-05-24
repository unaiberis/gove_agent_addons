from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_finished = fields.Boolean(
        string="Finished Purchase", compute="_compute_purchase_finished", store=True
    )
    woo_import_already_reset = fields.Boolean(
        string="Already Reset Once with Planned Action", default=False, store=True
    )
    
    @api.depends('website_id', 'access_token')
    def _compute_purchase_finished(self):
        for order in self:
            if order.website_id.id == 1 and not order.access_token:
                order.purchase_finished = False
            else:
                order.purchase_finished = True

    
    # Change the method to correct tha partner invoice id, pricelist and partner shipping id
    # when a company contact is the client and we need to use the company info instead of the 
    # contact info
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)
        
        # If partner has a parent, then it must be a salesperson
        # We need to use parent company's address instead of contact's
        # address and parents pricelist instead of contact's
        if self.partner_id.parent_id:
            addr = self.partner_id.parent_id.address_get(['delivery', 'invoice'])
            partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
            values = {
                'pricelist_id': self.partner_id.parent_id.property_product_pricelist and self.partner_id.parent_id.property_product_pricelist.id or False,
                'payment_term_id': self.partner_id.parent_id.property_payment_term_id and self.partner_id.parent_id.property_payment_term_id.id or False,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
            }
            user_id = partner_user.id
            if not self.env.context.get('not_self_saleperson'):
                user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
            if user_id and self.user_id.id != user_id:
                values['user_id'] = user_id

            if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
                values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
            if not self.env.context.get('not_self_saleperson') or not self.team_id:
                values['team_id'] = self.env['crm.team'].with_context(
                    default_team_id=self.partner_id.team_id.id
                )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
            self.update(values)
            
        # Normal functioning 
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice'])
            partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
            values = {
                'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
                'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
            }
            user_id = partner_user.id
            if not self.env.context.get('not_self_saleperson'):
                user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
            if user_id and self.user_id.id != user_id:
                values['user_id'] = user_id

            if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
                values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
            if not self.env.context.get('not_self_saleperson') or not self.team_id:
                values['team_id'] = self.env['crm.team'].with_context(
                    default_team_id=self.partner_id.team_id.id
                )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
            self.update(values)
