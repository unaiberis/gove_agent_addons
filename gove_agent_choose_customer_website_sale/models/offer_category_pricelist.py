from odoo import models, fields, api

class OfferCategoryPricelist(models.Model):
    _name = 'offer.category.pricelist'
    _description = 'Offer per Category and Pricelist'

    category_id = fields.Many2one('product.public.category', string='Product Category', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)

    offer_html = fields.Html(string='HTML text', translate=True)

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_combination', 'unique(category_id, pricelist_id)', 'An entry with this combination already exists.'),
    ]
