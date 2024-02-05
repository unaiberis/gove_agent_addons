from odoo.addons.portal.controllers.web import Home
from odoo.http import request
from odoo import http, models, fields, _


class Website(Home):

    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        return http.redirect_with_hash('/shop?agent_customer_id=0')
