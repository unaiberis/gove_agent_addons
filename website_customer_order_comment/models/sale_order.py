# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models


class SaleOrder(models.Model):
    """Adds the fields for options of the customer order comment"""

    _inherit = "sale.order"

    _description = "Sale Order"

    customer_comment = fields.Text("Customer Order Comment", default="")

    @api.model
    def fields_view_get(
        self, view_id=None, view_type=False, toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False
        )
        if res:
            doc = etree.XML(res["arch"])
            if view_type == "form":
                search_websites = self.env["website"].search([("id", "!=", False)])

                for setting in search_websites:
                    if setting.is_customer_comment_features:
                        pass

                res["arch"] = etree.tostring(doc)
        return res
