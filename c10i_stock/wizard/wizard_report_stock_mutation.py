from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardReportStockMutation(models.TransientModel):
    _name           = 'wizard.report.stock.mutation'
    _description    = 'Wizard Report Stock Mutation'
    
    from_date       = fields.Date('From Date')
    to_date         = fields.Date('To Date')
    location_id     = fields.Many2one('stock.location', string='Location')
    username        = fields.Char('Username', default=lambda self: self.env.user.name)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    show_value      = fields.Selection([
                        ('cost', 'With Value'),
                        ('no', 'Just Stock Mutation'),
                    ], string='Show Value')
    
    product_ids = fields.Many2many('product.product', string='Product')

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Mutasi !"))
        
        query = """
            SELECT 
                sm.product_id, 
                pt.name, 
                sm.location_id, 
                sl.name AS location_name,
                sm.date, 
                sm.product_qty, 
                sm.price_unit
            FROM stock_move sm
            LEFT JOIN product_product pp ON sm.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN stock_location sl ON sm.location_id = sl.id
            WHERE sm.date >= %s
            AND sm.date <= %s
            AND sm.location_id = %s
        """
        params = (
            self.from_date,
            self.to_date,
            self.location_id.id,
        )

        self.env.cr.execute(query, params)
        stock_moves = self.env.cr.fetchall()

        print(f"===== {stock_moves}")
        print(f"===== {ss}")

        data = {
            'from_date'     : self.from_date,
            'to_date'       : self.to_date,
            'location_id'   : self.location_id.id,
            'company_id'    : self.company_id.id,
            'product_ids'   : self.product_ids.ids,
            'show_value'    : self.show_value,
            'stock_moves'   : stock_moves,
        }
        
        return self.env.ref('c10i_stock.action_stock_mutation_report_xlsx').report_action(self, data=data)