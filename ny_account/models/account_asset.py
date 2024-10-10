from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    # boolean penanda 
    charge_to_activity          = fields.Boolean('Charge To Activity', default=False)

    # data yang akan di isi ketika boolean bernilai true
    location_type_id            = fields.Many2one('lhm.location.type', string='Tipe Lokasi')
    location_id                 = fields.Many2one('lhm.location', string='Lokasi')
    activity_id                 = fields.Many2one('lhm.activity', string="Aktivitas")

    beginning_balance           = fields.Boolean('Beginning Balance', default=False)
    accumulated_depreciation    = fields.Monetary('Accumulated Depreciation')
    value_residual              = fields.Monetary(compute='_amount_residual', string='Residual Value')
    value                       = fields.Monetary(string='Gross Value', required=True, readonly=True, states={'draft': [('readonly', False)]})


    @api.depends('accumulated_depreciation', 'value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount')
    def _amount_residual(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.depreciation_line_ids:
                if line.move_check:
                    total_amount += line.amount
            if not rec.beginning_balance:
                rec.value_residual = rec.value - total_amount - rec.salvage_value
            else:
                rec.value_residual = rec.value - rec.accumulated_depreciation - total_amount - rec.salvage_value

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        move_vals = super(AccountAssetDepreciationLine, self)._prepare_move(line)
        asset_id = line[0].asset_id
        
        if asset_id.charge_to_activity:
            move_line_2                 = move_vals['line_ids'][1][2]
            move_line_2['account_id']   = asset_id.activity_id.account_id.id
            
            move_line_2['plantation_location_type_id']  = asset_id.location_type_id.id
            move_line_2['plantation_location_id']       = asset_id.location_id.id
            move_line_2['plantation_activity_id']       = asset_id.activity_id.id

        return move_vals
