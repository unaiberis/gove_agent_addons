from odoo import models, fields, api

class AutoCancelOrderServer(models.Model):
    _name = 'auto.cancel.order.server'

    @api.model
    def _auto_cancel_woocommerce_orders(self):
        orders_to_cancel = self.env['sale.order'].search([('woo_status', '!=', False), ('state', 'in', ['draft', 'sent', 'sale'])])
        orders_to_cancel.action_cancel()
