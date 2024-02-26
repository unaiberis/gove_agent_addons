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
