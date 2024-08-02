from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round

class AccountMove(models.Model):
    _inherit = 'account.move'

    # asset_acquisition_id = fields.Many2one("asset.acquisition", string="Origin")
    # disposal_id = fields.Many2one('account.asset.disposal', string="Sell / Disposal")
    # sell_account_move_id = fields.Many2one('account.move', 'Sell Account Move', related="disposal_id.sell_account_move_id")
    # reason = fields.Text(string="Sell/Dispose Reason", related="disposal_id.reason")
    acquisition_line_ids = fields.Many2many('account.asset.acquisition.line', 'acquisition_line_account_move_rel', 
                                'move_id', 'acquisition_line_id', string='Asset')