import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class CouponProgram(models.Model):
    _inherit = "coupon.program"

    def _keep_only_most_interesting_auto_applied_global_discount_program(
        self, order=None
    ):
        groups = self.env["coupon.program.group"].search(
            [
                ("apply_always", "=", True),
            ]
        )
        no_group_programs = self.filtered(
            lambda p: p._is_global_discount_program()
            and p.promo_code_usage == "no_code_needed"
            and p not in groups.mapped("coupon_programs")
            and p.apply_always
        )

        if not order and (groups or no_group_programs):
            website = request and getattr(request, "website", None)
            order = (
                website.sale_get_order_without_updating_pricelist() if website else None
            )
            if not order:
                ctx = self.env.context
                params = ctx.get("params") if ctx else None
                if params and params.get("model") == "sale.order":
                    order_id = params.get("id")
                    order = self.env["sale.order"].browse(order_id)
        if order:
            # Check if partner has parent company.
            # If yes, use parent company's category ("parent's discounts")
            if order.partner_id.parent_id:
                groups = groups.filtered(
                    lambda g: any(
                        categ.id in g.partner_category_ids.ids
                        for categ in order.partner_id.parent_id.category_id
                    )
                )
            # Otherwise use partner's category
            else:
                groups = groups.filtered(
                    lambda g: any(
                        categ.id in g.partner_category_ids.ids
                        for categ in order.partner_id.category_id
                    )
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
        return (
            super()._keep_only_most_interesting_auto_applied_global_discount_program()
        )
