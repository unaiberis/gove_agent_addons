from odoo import fields, models
from odoo.addons.website_sale_stock.models.website import Website

class Website(Website):

    def get_current_pricelist(self):
        pl = super().get_current_pricelist()
        return pl
    

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, **kwargs):
        
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            **kwargs
        )
        product_template_id = combination_info['product_template_id']
        product_template = self.env['product.template'].browse(product_template_id)
        product_template_PVP = product_template.list_price 

        combination_info.update({'PVP': product_template_PVP})

        return combination_info
