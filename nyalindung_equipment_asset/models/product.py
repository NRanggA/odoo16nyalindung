from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_asset = fields.Boolean(related='categ_id.asset', store=True)

    def _get_product_accounts(self):
        """ Add the stock accounts related to product to the result of super()
        @return: dictionary which contains information regarding stock accounts and super (income+expense accounts)
        """
        accounts = super(ProductTemplate, self)._get_product_accounts()
        res = self._get_asset_accounts()
        accounts.update({
            'stock_input': res['stock_input'] or self.categ_id.property_stock_account_input_categ_id,
            'stock_output': res['stock_output'] or self.categ_id.property_stock_account_output_categ_id,
            'stock_valuation': self.categ_id.property_stock_valuation_account_id or False,
            'stock_asset': self.categ_id.asset_clearing_account_id or False,
        })
        return accounts


class ProductCategory(models.Model):
    _inherit = 'product.category'

    asset = fields.Boolean('Asset')
    asset_clearing_account_id = fields.Many2one('account.account', string='Asset Clearing Account')
    gain_on_asset_sales_account_id = fields.Many2one('account.account', string='Gain on Asset Sales Account')
    loss_on_asset_sales_account_id = fields.Many2one('account.account', string='Loss on Asset Sales Account')
    write_on_asset_sales_account_id = fields.Many2one('account.account', string='Write-Off Asset Account')
    asset_journal_id = fields.Many2one('account.journal', string='Asset Journal')