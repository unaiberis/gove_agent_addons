# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _needs_ref(self, vals=None):
        super()._needs_ref(vals)
        _logger.info(f"\n\n _logger_gove NEEDS REF {vals}\n")
        if self.customer_from_woo:
            _logger.info(f"\n\n _logger_gove CUSTOMER FROM WOOCOMMERCE {self}\n")
            return True
        return False
