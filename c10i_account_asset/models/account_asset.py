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