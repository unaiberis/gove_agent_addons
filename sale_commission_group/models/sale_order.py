###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agents_name = fields.Char(
        string="Agents Name", compute="_compute_agents_name", store=True
    )

    @api.depends("order_line.agent_ids")
    def _compute_agents_name(self):
        self.agents_name = ", ".join(
            list({ag.agent_id.name for line in self.order_line for ag in line.agent_ids})
        )
