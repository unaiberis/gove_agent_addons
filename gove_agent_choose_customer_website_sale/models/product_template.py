from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_on_offer = fields.Boolean(string="On Offer", default=False, store=True)

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1, pricelist=False, **kwargs
    ):

        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            **kwargs
        )
        product_template_id = combination_info["product_template_id"]
        product_template = self.env["product.template"].browse(product_template_id)
        product_template_PVP = product_template.list_price

        combination_info.update({"PVP": product_template_PVP})

        return combination_info
