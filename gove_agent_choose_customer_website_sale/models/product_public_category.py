from odoo import models, fields

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    pricelist_ids = fields.Many2many(
        'product.pricelist', 
        'category_id',
        string='Pricelists'
    )
