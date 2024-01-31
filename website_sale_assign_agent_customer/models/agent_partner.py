###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class AgentPartner(models.Model):
    _name = "agent.partner"
    _description = "Model used to save customer id to use in the cart and when confirming the order"

    customer_id_chosen_by_agent = fields.Integer(
        string="Agent Customer",
        default=True,
    )
    agent_id  = fields.Integer(
        string="Agent Id",
        default=True,
    )
