###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    agents_name = fields.Char(
        string="Agents", compute="_compute_agents_name", store=True
    )

    @api.depends("line_ids.agent_ids")
    def _compute_agents_name(self):
        agent_list = [
            ag.agent_id.name for line in self.line_ids for ag in line.agent_ids
        ]
        self.agents_name = ", ".join(list(set(agent_list)))
