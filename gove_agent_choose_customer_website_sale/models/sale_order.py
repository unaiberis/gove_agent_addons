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

    # Add a method to force recomputation
    def force_recompute_purchase_finished(self):
        for order in self:
            order.purchase_finished = order._compute_purchase_finished()

# Usage example:
# Call the force_recompute_purchase_finished method on the records you want to recompute
orders_to_recompute = self.env['sale.order'].search([])
orders_to_recompute.force_recompute_purchase_finished()
