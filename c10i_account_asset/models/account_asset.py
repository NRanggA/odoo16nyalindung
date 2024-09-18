from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'
    # _inherit = 'account.account.asset'

    asset_acquisition_id = fields.Many2one("asset.acquisition", string="Origin")
    disposal_id = fields.Many2one('account.asset.disposal', string="Sell / Disposal")
    sell_account_move_id = fields.Many2one('account.move', 'Sell Account Move', related="disposal_id.sell_account_move_id")
    reason = fields.Text(string="Sell/Dispose Reason", related="disposal_id.reason")
    acquisition_date = fields.Date('Acquisition Date')
    gain_account_id = fields.Many2one('account.account', string='Gain Account on Sales')
    loss_account_id = fields.Many2one('account.account', string='Loss Account on Sales')  

    @api.onchange('category_id')
    def _set_gain_and_loss_account(self):
        if self.category_id:
            try:
                self.gain_account_id = self.category_id.gain_account_id.id
                self.loss_account_id = self.category_id.loss_account_id.id
            except:
                self.gain_account_id = False
                self.loss_account_id = False
    
    def validate(self):
        res = super(AccountAsset, self).validate()
        for record in self:
            if not record.category_id:
                raise UserError("Asset Category must be filled")
        return res

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'
    _description = 'Asset depreciation line'

    ref = fields.Char('ref')

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    gain_account_id = fields.Many2one('account.account', string='Gain Account on Sales')
    loss_account_id = fields.Many2one('account.account', string='Loss Account on Sales')    