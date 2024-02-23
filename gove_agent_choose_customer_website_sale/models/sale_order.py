from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_finished = fields.Boolean(
        string="Finished Purchase", compute="_compute_purchase_finished", store=True
    )

    @api.depends('website_id', 'access_token')
    def _compute_purchase_finished(self):
        for order in self:
            if order.website_id.id == 1 and not order.access_token:
                order.purchase_finished = False
                _logger.info("Purchase finished set to False - website_id: %s, access_token: %s", order.website_id, order.access_token)
            # elif order.website_id.id == 1 and order.access_token:
            #     order.purchase_finished = True
            else:
                order.purchase_finished = True
