# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from odoo import http
from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.website_sale.controllers.main import WebsiteSale as BaseWebsiteSale

from odoo.http import route, request

_logger = logging.getLogger(__name__)

class Home(PortalHome):

    @http.route('/')
    def index(self, **kw):
        # Comprobar si el usuario está autenticado
        if request.env.user._is_public():
            _logger.info("\n\nIntento de acceso a la página principal por un usuario no autenticado\n\n")
            return http.local_redirect('/web/login', query=request.params, keep_hash=True)
        return super().index(**kw)

    # Sobreescribir el método de redirección de inicio de sesión
    def _login_redirect(self, uid, redirect=None):
        return super()._login_redirect(uid, redirect="/")
    
class WebsiteSale(BaseWebsiteSale):

    # Sobreescribir el método para manejar solicitudes a URLs que contienen /shop/
    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        # Comprobar si el usuario está autenticado
        if request.env.user._is_public():
            _logger.info("\n\nIntento de acceso a la tienda por un usuario no autenticado\n\n")
            return http.local_redirect('/web/login', query=request.params, keep_hash=True)
        _logger.info("\n\nReturn 2\n\n")
        return super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)

