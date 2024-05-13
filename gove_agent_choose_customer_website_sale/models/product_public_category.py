from odoo import models, fields

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    pricelist_ids = fields.One2many(
        'product.pricelist', 
        string='Pricelists'
    )
