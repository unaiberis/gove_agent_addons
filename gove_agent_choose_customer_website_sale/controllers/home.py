from odoo.addons.portal.controllers.web import Home

class Home(Home):
    def _login_redirect(self, uid, redirect=None):
        return super()._login_redirect(uid, redirect="/")


