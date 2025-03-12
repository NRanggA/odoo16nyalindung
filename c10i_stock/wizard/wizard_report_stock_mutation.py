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
    product_ids     = fields.Many2many('product.product', string='Product',  compute="_compute_product_ids", store=True)

    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Sercive'),
        ('product', 'Storable Product'),
    ], string='Product Type')

    inventory_valuation = fields.Selection([
        ('manual_periodic', 'Manual'),
        ('real_time', 'Automated'),
    ], string='Inventory Valuation')

    # @api.onchange('inventory_valuation', 'product_type')
    # def _onchange_inventory_valuation(self):
    #     domain = []

    #     if self.inventory_valuation:
    #         domain.append(('categ_id.property_valuation', '=', self.inventory_valuation))

    #     if self.product_type:
    #         domain.append(('detailed_type', '=', self.product_type))

    #     return {'domain': {'product_ids': domain}}
    @api.depends('inventory_valuation', 'product_type')
    def _compute_product_ids(self):
        for record in self:
            if not record.product_type and not record.inventory_valuation:
                record.product_ids = [(5, 0, 0)] 
                continue
            
            domain = []
            
            if record.product_type:
                domain.append(('detailed_type', '=', record.product_type))
            
            if record.inventory_valuation:
                domain.append(('categ_id.property_valuation', '=', record.inventory_valuation))
            
            if record.product_ids:
                domain.append(('id', 'in', record.product_ids.ids))
            
            record.product_ids = self.env['product.product'].search(domain) if domain else [(5, 0, 0)]

    def create_report(self):
        if not self.from_date or not self.to_date:
            raise UserError(_("Masukkan Tanggal untuk memfilter Laporan Mutasi !"))

        return self.env.ref('c10i_stock.action_stock_mutation_report_xlsx').report_action(self)