###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    agents_name = fields.Char(
        string="Agents", compute="_compute_agents_name", store=True
    )
    customers_count = fields.Integer(
        compute="_compute_customers",
    )
    agent_customers = fields.Many2many(
        compute="_compute_agent_customers",
        comodel_name="res.partner",
        relation="agent2customers_rel",
        column1="agent_id",
        column2="customer_id",
    )

    @api.depends("agent_ids")
    def _compute_agents_name(self):
        self.agents_name = ", ".join(list({ag.name for ag in self.agent_ids}))

    def _get_customers_domain(self):
        return [("is_company", "=", True), ("agent_ids", "in", self.ids)]

    @api.depends("agent_customers")
    def _compute_customers(self):
        for agent in self:
            agent.customers_count = len(agent.agent_customers)

    @api.depends("agent_ids")
    def _compute_agent_customers(self):
        for agent in self:
            agent_customers = self.env["res.partner"].search(
                self._get_customers_domain(), order="name ASC"
            )
            if agent_customers:
                agent.agent_customers = [(6, 0, agent_customers.ids)]
            else:
                agent.agent_customers = False

    def action_view_customers(self):
        form_view = self.env.ref("base.view_partner_form")
        tree_view = self.env.ref("base.view_partner_tree")
        search_view = self.env.ref("base.view_res_partner_filter")
        return {
            "name": _("Associated customers"),
            "domain": self._get_customers_domain(),
            "res_model": "res.partner",
            "type": "ir.actions.act_window",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "view_mode": "tree,form",
            "search_view_id": search_view.id,
            "view_type": "form",
        }
