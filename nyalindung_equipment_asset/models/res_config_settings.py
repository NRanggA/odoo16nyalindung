from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    # gain_on_asset_sales_account_id = fields.Many2one('account.account', string='Gain on Asset Sales Account')
    # loss_on_asset_sales_account_id = fields.Many2one('account.account', string='Loss on Asset Sales Account')
    # write_on_asset_sales_account_id = fields.Many2one('account.account', string='Write-Off Asset Account')
    income_from_lva_sales_account_id = fields.Many2one('account.account', string='Income From LVA Sales Account')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    threshold = fields.Float('Threshold')
    # gain_on_asset_sales_account_id = fields.Many2one('account.account',string='Gain on Asset Sales Account',related='company_id.gain_on_asset_sales_account_id', readonly=False)
    # loss_on_asset_sales_account_id = fields.Many2one('account.account',string='Loss on Asset Sales Account',related='company_id.loss_on_asset_sales_account_id', readonly=False)
    # write_on_asset_sales_account_id = fields.Many2one('account.account',string='Write-Off Asset Account',related='company_id.write_on_asset_sales_account_id', readonly=False)
    income_from_lva_sales_account_id = fields.Many2one('account.account', string='Income From LVA Sales Account',related='company_id.income_from_lva_sales_account_id', readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # self.env.company.gain_on_asset_sales_account_id = self.gain_on_asset_sales_account_id
        # self.env.company.loss_on_asset_sales_account_id = self.loss_on_asset_sales_account_id
        # self.env.company.write_on_asset_sales_account_id = self.write_on_asset_sales_account_id
        self.env.company.income_from_lva_sales_account_id = self.income_from_lva_sales_account_id
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('ny_equipment.threshold', self.threshold or 0.0)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'threshold': float(params.get_param('ny_equipment.threshold', default=0.0)),
        })
        return res
