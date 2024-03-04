from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    extra_computation_enabled = fields.Boolean(
        string="Extra Coupon Computation enabler",
        store=True, default=False
    )
