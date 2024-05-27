from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    resend_mail = fields.Boolean(string='Resend Email', default=False)

    def toggle_resend_mail(self):
        self.ensure_one()
        self.resend_mail = not self.resend_mail
