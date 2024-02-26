from odoo import models, api

class AutoCancelOrderServer(models.Model):
    _name = 'auto.cancel.order.server'
    _inherit = 'sale.order'

    @api.model
    def _auto_cancel_woocommerce_orders(self):
        orders_to_cancel = self.search([('woo_status', '!=', False), ('state', 'in', ['draft', 'sent', 'sale'])])
        orders_to_cancel._action_cancel()
