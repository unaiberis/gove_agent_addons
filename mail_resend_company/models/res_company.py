from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    resend_mail = fields.Boolean(
        string="Resend Email",
        default=False,
        help="Field to resend B2B online purchase emails to agents and to info@surflogic.com.",
    )

    def toggle_resend_mail(self):
        self.ensure_one()
        self.resend_mail = not self.resend_mail
