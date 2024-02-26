from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_finished = fields.Boolean(
        string="Finished Purchase", compute="_compute_purchase_finished", store=True
    )

    @api.depends('website_id', 'access_token')
    def _compute_purchase_finished(self):
        for order in self:
            if order.website_id.id == 1 and not order.access_token:
                order.purchase_finished = False
            else:
                order.purchase_finished = True
                

    @api.depends('woo_status')
    def _canceled_completed_orders_from_woo(self):
        for order in self:
            if order.woo_status:
                domain = ['|', ('state', 'not in', ['draft', 'sent', 'sale']), ('id', '=', False)]
                negated_domain = ['!', domain]
                
                orders_to_cancel = order.search(negated_domain)
                orders_to_cancel._action_cancel()
