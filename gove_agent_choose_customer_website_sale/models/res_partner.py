from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    extra_computation_enabled = fields.Boolean(
        string="Extra Coupon Computation enabler", compute='_compute_extra_computation_enabled',
        store=True, default=False
    )

    # @api.depends('sale_order_ids.purchase_finished')
    # def _compute_extra_computation_enabled(self):
    #     for partner in self:
    #         partner.extra_computation_enabled = not any(partner.sale_order_ids.filtered(lambda order: not order.purchase_finished))
