from odoo import fields, models, api
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



class UpdateResPartner(models.Model):
    _name = "update.res.partner"

    def update_partner_fields(self):
        # Define the domain to filter res partners
        domain = [["create_uid", "=", 2]]

        # Retrieve res partners based on the domain
        partners = self.env['res.partner'].search(domain)

        # Define the field values to update for each partner
        field_values = {
            'sale_incoterm_id': 'stock.incoterms,6',
            'property_payment_term_id': 'account.payment.term,9',
            'property_product_pricelist': 'product.pricelist,7',
            'sale_type': 'sale.order.type,2',
            'property_account_position_id': 'account.fiscal.position,1',
            'aeat_anonymous_cash_customer': 'True',
        }

        # Update the fields for each partner
        for partner in partners:
            for field_name, value in field_values.items():
                # Check if the field exists in the model
                if field_name in partner:
                    # Update the field with the reference value
                    partner[field_name] = value

        # Commit the changes to the database
        self.env.cr.commit()
