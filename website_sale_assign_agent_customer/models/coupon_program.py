from odoo import api, fields, models, _
from odoo.http import request


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

<<<<<<< HEAD
            if not order and (groups or no_group_programs):
                website = request and getattr(request, 'website', None)
                
                
                
                # GET CUSTOMER PRICELIST
                agent_customers = request.env.user.sudo().partner_id.agent_customers
                # Get the pricelist and partner based on the agent_customer_id

                _agent_customer_id = request.env['agent.partner'].sudo().search([], limit=1).customer_id_chosen_by_agent
                if _agent_customer_id and _agent_customer_id in agent_customers.ids:
                    partner = request.env['res.partner'].browse(_agent_customer_id)
                    property_name = 'property_product_pricelist'

                    ir_property = request.env['ir.property'].sudo().search([
                        ('name', '=', property_name),
                        ('res_id', '=', f'res.partner,{partner.id}'),
                    ], limit=1)

                    if ir_property and ir_property.value_reference:
                        # Parse the value_reference to get the pricelist number
                        pricelist_number = int(ir_property.value_reference.split(',')[1])
                        pricelist = request.env['product.pricelist'].browse(pricelist_number)
                        _pricelist = pricelist
                
                order = website.sale_get_order(force_pricelist=_pricelist.id,update_pricelist=True) if website and _pricelist else None
                if not order:
                    ctx = self.env.context
                    params = ctx.get('params') if ctx and _pricelist else None
                    if params and params.get('model') == 'sale.order':
                        order_id = params.get('id')
                        order = self.env['sale.order'].browse(order_id)
            if order:
                if request.env['agent.partner'].search([]).customer_id_chosen_by_agent:
                    order.partner_id = request.env['agent.partner'].search([]).customer_id_chosen_by_agent
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
=======
        if not order and (groups or no_group_programs):
            website = request and getattr(request, "website", None)
            order = website.sale_get_order() if website else None
            if not order:
                ctx = self.env.context
                params = ctx.get("params") if ctx else None
                if params and params.get("model") == "sale.order":
                    order_id = params.get("id")
                    order = self.env["sale.order"].browse(order_id)
        if order:
            if (
                request.env["agent.partner"]
                .search(
                    [("agent_id", "=", request.env.user.sudo().partner_id.id)], limit=1
                )
                .customer_id_chosen_by_agent
            ):
                order.partner_id = (
                    request.env["agent.partner"]
                    .search(
                        [("agent_id", "=", request.env.user.sudo().partner_id.id)],
                        limit=1,
                    )
                    .customer_id_chosen_by_agent
                )
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
        return super(
            CouponProgram, self
        )._keep_only_most_interesting_auto_applied_global_discount_program()
>>>>>>> cart_automatikoki_borrau_pruebie
