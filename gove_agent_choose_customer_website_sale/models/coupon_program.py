import logging

from odoo import api, fields, models, _
from odoo.http import request
_logger = logging.getLogger(__name__)


class CouponProgram(models.Model):
    _inherit = "coupon.program"

    def _keep_only_most_interesting_auto_applied_global_discount_program(self, order=None):
#        if request.env.user.partner_id.extra_computation_enabled:
        groups = self.env['coupon.program.group'].search([
            ('apply_always', '=', True),
        ])
        no_group_programs = self.filtered(
            lambda p: p._is_global_discount_program()
                        and p.promo_code_usage == 'no_code_needed'
                        and p not in groups.mapped('coupon_programs')
                        and p.apply_always)

        if order:
            groups = groups.filtered(lambda g: any(categ.id in g.partner_category_ids.ids for categ in order.partner_id.category_id))
            applicable_programs = no_group_programs
            for group in groups:
                for program in group.coupon_programs.sorted(
                        lambda p: (p.rule_min_quantity, p.rule_minimum_amount),
                        reverse=True):
                    error = program._check_group_promo_code(order, False, group)
                    if not error:
                        applicable_programs = applicable_programs + program
                        break
            return applicable_programs
        return super(CouponProgram, self)._keep_only_most_interesting_auto_applied_global_discount_program()

