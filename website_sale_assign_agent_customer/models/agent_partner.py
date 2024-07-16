###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class AgentPartner(models.Model):
    _name = "agent.partner"
    _description = "Chosen Customer by Agent"

    customer_id_chosen_by_agent = fields.Integer(
        string="Agent Customer",
        default=0,
    )
    agent_id = fields.Integer()
