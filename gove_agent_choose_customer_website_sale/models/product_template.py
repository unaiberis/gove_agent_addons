import time
from odoo import fields, models, api

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


"""
class UpdateResPartner(models.Model):
    _name = "update.res.partner"

    def update_partner_properties(self):
        start_time = time.time()
        # Define the domain to filter res partners
        domain = [
            ["create_uid", "=", 2],
            ["aeat_anonymous_cash_customer", "=", False]
        ]
        # Retrieve res partners based on the domain
        partners = self.env['res.partner'].search(domain)

        # Update the 'aeat_anonymous_cash_customer' attribute for each partner
        for partner in partners:
            partner.aeat_anonymous_cash_customer = True

        # Commit the changes to the database
        self.env.cr.commit()

        # Now, update the ir_property records as mentioned in the previous script
        self.update_partner_ir_properties(start_time)

    def update_partner_ir_properties(self, start_time):
        # Define the domain to filter res partners
        domain = [["create_uid", "=", 2]]

        # Retrieve res partners based on the domain
        partners = self.env['res.partner'].search(domain)
        i=0
        # Define the field values to update for each partner
        property_values = [
            {"name": "property_account_payable_id", "fields_id": 3252, "value_reference": "account.account,175"},
            {"name": "property_payment_term_id", "fields_id": 3255, "value_reference": "account.payment.term,9"},
            {"name": "property_product_pricelist", "fields_id": 3056, "value_reference": "product.pricelist,7"},
            {"name": "sale_type", "fields_id": 11694, "value_reference": "sale.order.type,2"},
            {"name": "property_account_position_id", "fields_id": 3254, "value_reference": "account.fiscal.position,1"},
        ]
        for partner in partners:
            for prop_values in property_values:
                # Create or update records in ir_property table
                prop_name = prop_values["name"]
                fields_id = prop_values["fields_id"]
                value_reference = prop_values["value_reference"]
                i+=1
                prop_record = self.env['ir.property'].search([
                    ('name', '=', prop_name),
                    ('res_id', '=', f"res.partner,{partner.id}"),
                    ('fields_id', '=', fields_id),
                ])
                if not prop_record:
                    self.env['ir.property'].create({
                        'name': prop_name,
                        'res_id': f"res.partner,{partner.id}",
                        'company_id': 1,  # Update with the actual company ID
                        'fields_id': fields_id,
                        'value_reference': value_reference,
                    })
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total Elapsed Time: {round(elapsed_time, 2)} seconds")        # Commit the changes to the database
        self.env.cr.commit()
"""