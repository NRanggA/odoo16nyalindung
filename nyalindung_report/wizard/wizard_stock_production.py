from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class WizardStockProduction(models.TransientModel):
    _name = 'wizard.stock.production'
    _description = 'Wizard Mutasi Stock Produksi'
    
    from_date = fields.Date('From Date', required=True,
            default=lambda self: fields.Date.today().replace(day=1))
    to_date = fields.Date('To Date', required=True,
            default=lambda self: fields.Date.today())
    def print_excel(self):
        return self.env.ref('nyalindung_report.action_report_stock_report_production_xlsx').report_action(self)