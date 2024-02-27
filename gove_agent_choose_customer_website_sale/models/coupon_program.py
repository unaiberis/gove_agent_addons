from odoo import api, fields, models, _
from odoo.http import request


class CouponProgram(models.Model):
    _inherit = "coupon.program"

    def _keep_only_most_interesting_auto_applied_global_discount_program(self, extra_computation=False, order=None):
        # Check if order is already passed, otherwise fetch it
        
        if extra_computation or True:
            order = order or self._get_order()

            if order:
                agent_partner = self._get_agent_partner()

                if agent_partner.customer_id_chosen_by_agent:
                    order.partner_id = agent_partner.customer_id_chosen_by_agent

                groups = self._filter_groups(order)
                applicable_programs = self._get_applicable_programs(groups, order)

                return applicable_programs

        return super(CouponProgram, self)._keep_only_most_interesting_auto_applied_global_discount_program()

    def _get_order(self):
        website = request and getattr(request, "website", None)
        return website.sale_get_order_without_updating_pricelist() if website else None

    def _get_agent_partner(self):
        agent_id = request.env.user.sudo().partner_id.id
        return request.env["agent.partner"].search([("agent_id", "=", agent_id)], limit=1)

    def _filter_groups(self, order):
        groups = self.env["coupon.program.group"].search([("apply_always", "=", True)])

        return groups.filtered(
            lambda g: any(categ.id in g.partner_category_ids.ids for categ in order.partner_id.category_id)
        )

    def _get_applicable_programs(self, groups, order):
        no_group_programs = self.filtered(
            lambda p: p._is_global_discount_program()
            and p.promo_code_usage == "no_code_needed"
            and p not in groups.mapped("coupon_programs")
            and p.apply_always
        )

        applicable_programs = no_group_programs
        for group in groups:
            for program in group.coupon_programs.sorted(
                lambda p: (p.rule_min_quantity, p.rule_minimum_amount), reverse=True
            ):
                error = program._check_group_promo_code(order, False, group)
                if not error:
                    applicable_programs = applicable_programs + program
                    break

        return applicable_programs
