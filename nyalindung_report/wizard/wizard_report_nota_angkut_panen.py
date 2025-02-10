# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WizardReportNotaAngkutPanen(models.TransientModel):
    _name = 'wizard.report.nota.angkut.panen'
    _description = _('Wizard Report Nota Angkut Panen')

    date_start = fields.Date('Date Start',required=True)
    date_end = fields.Date('Date End',required=True)
    # product_id = fields.Many2one('product.product', string='Product',required=True)

    product_ids = fields.Many2many('product.product', string='Product')



    def action_print_report(self):
        return self.env.ref('nyalindung_report.action_nota_angkut_panen_report_xlsx').report_action(self)
