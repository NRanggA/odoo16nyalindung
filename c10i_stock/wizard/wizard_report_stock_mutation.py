from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardReportStockMutation(models.TransientModel):
    _name           = 'wizard.report.stock.mutation'
    _description    = 'Wizard Report Stock Mutation'
    
    from_date       = fields.Date('From Date', required=True)
    to_date         = fields.Date('To Date', required=True)
    location_id     = fields.Many2one('stock.location', string='Location', required=True)
    username        = fields.Char('Username', default=lambda self: self.env.user.name)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    show_value      = fields.Selection([
                        ('cost', 'With Value'),
                        ('no', 'Just Stock Mutation'),
                    ], string='Show Value', default='no')

    exclude_exhaust = fields.Boolean('Exclude Exhaust Product', default=False)

    product_ids     = fields.Many2many('product.product', string='Product')

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Mutasi !"))

        return self.env.ref('c10i_stock.action_stock_mutation_report_xlsx').report_action(self)