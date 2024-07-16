from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.web import Home


class Website(Home):
    # In the moment we don't want this redirect
    @http.route("/", type="http", auth="public", website=True, sitemap=True)
    def index(self, **kw):
        super().index(**kw)
        if request.env.user.sudo().partner_id.agent:
            return http.redirect_with_hash("/shop?agent_customer_id=0")
        else:
            return http.redirect_with_hash("/shop")
