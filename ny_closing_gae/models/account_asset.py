from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    gae_dest_type = fields.Selection([('direct', 'Direct to ORG'), ('indirect', 'Indirect through GAE Distribution')], 
        string='GAE Distribution Method')
    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')
    plantation_varieties_ids = fields.Many2many('plant.varieties', 'asset_varieties_rel', string='Distribution ORG')

    gae_direct_activity_id = fields.Many2one('lhm.activity', string='Direct GAE Activity', domain="[('type_id.code','in',['FC','PJ'])]")
    gae_expense_depre_account_id = fields.Many2one('account.account', string='GAE Expense Depreciation Account')

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        move_vals = super(AccountAssetDepreciationLine, self)._prepare_move(line)
        asset_id = line[0].asset_id
        
        category_id = line.asset_id.category_id
        analytic_distribution = line.asset_id.analytic_distribution
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        
        if asset_id.gae_dest_type == 'direct' and asset_id.plantation_varieties_ids:
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_distribution': analytic_distribution,
                'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                'amount_currency': - 1.0 * line.amount
            }
            move_vals['line_ids'] = [(0,0, move_line_1)]

            remaining_amount = amount
            count_org = len(asset_id.plantation_varieties_ids.ids) - 1
            total_ha = sum(asset_id.plantation_varieties_ids.mapped('plant_block_ids.planted'))
            for org in asset_id.plantation_varieties_ids:
                if not total_ha:
                    continue
                total_ha_2 = sum(org.plant_block_ids.mapped('planted'))
                if not count_org:
                    org_amount = remaining_amount
                else:
                    org_amount = round(amount * total_ha_2 / total_ha)
                
                depr_tm_amount = 0.0
                block_remaining_amt = org_amount
                count_block = len(org.plant_block_ids.ids) - 1
                count_org -= 1
                for block in org.plant_block_ids.sorted(key=lambda r: r.status):
                    if not count_block:
                        dest_amount = block_remaining_amt
                    else:
                        dest_amount = round(org_amount * block.planted / total_ha_2, 2)
                    if block.status=='tm':
                        depr_tm_amount += dest_amount
                        count_block -= 1
                        continue
                    if not block.planted:
                        count_block -= 1
                        continue
                    
                    move_line_2 = {
                        'name': asset_name,
                        'plantation_varieties_id': block.varieties_id.id,
                        # 'plantation_location_id': block.location_id.id,
                        # 'account_id': block.tbm_account_id.id,
                        'plantation_location_type_id': block.location_id.type_id.id,
                        'plantation_location_id': block.location_id.id,
                        # 'plantation_activity_id': block.activity_id.id,
                        'plantation_activity_id': line.asset_id.gae_direct_activity_id.id,
                        # 'account_id': block.activity_id.account_id.id,
                        'account_id': line.asset_id.gae_direct_activity_id.account_id.id,

                        'credit': 0.0 if float_compare(dest_amount, 0.0, precision_digits=prec) > 0 else -dest_amount,
                        'debit': dest_amount if float_compare(dest_amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'partner_id': line.asset_id.partner_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                        'amount_currency': dest_amount,
                    }
                    move_vals['line_ids'].append((0,0, move_line_2))
                    count_block -= 1
                    block_remaining_amt -= dest_amount
                    print(":::::::::::::::::::::", asset_id.name, move_line_2['debit'], move_line_2['credit'])
                
                print(".......SISA UNTUK TM........", block_remaining_amt, depr_tm_amount)
                if depr_tm_amount:
                    move_line_3 = {
                        'name': asset_name,
                        'plantation_varieties_id': block.varieties_id.id,
                        # 'account_id': category_id.account_depreciation_expense_id.id,
                        'account_id': line.asset_id.gae_direct_activity_id.cost_account_id.id,
                        
                        'credit': 0.0 if float_compare(depr_tm_amount, 0.0, precision_digits=prec) > 0 else -depr_tm_amount,
                        'debit': depr_tm_amount if float_compare(depr_tm_amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'partner_id': line.asset_id.partner_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                        'amount_currency': dest_amount,
                    }
                    print(":::::::::::::::::::::::::", asset_id.name, move_line_3['debit'], move_line_3['credit'])
                    move_vals['line_ids'].append((0,0, move_line_3))
        elif asset_id.gae_dest_type=='indirect' and  asset_id.gae_distribution_id:
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_distribution': analytic_distribution,
                'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                'amount_currency': - 1.0 * line.amount
            }
            move_vals['line_ids'] = [(0,0, move_line_1)]

            remaining_amount = amount
            last_line = len(asset_id.gae_distribution_id.line_ids)
            for dist_plan in asset_id.gae_distribution_id.line_ids:
                if not last_line:
                    dist_amount = remaining_amount
                else:
                    dist_amount = amount * dist_plan.distribution_percentage / 100
                
                move_line_2 = {
                    'name': asset_name,
                    'plantation_varieties_id': dist_plan.varieties_id.id,
                    # 'account_id': category_id.account_depreciation_expense_id.id,
                    'account_id': line.asset_id.gae_expense_depre_account_id.id,
                    'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'partner_id': line.asset_id.partner_id.id,
                    # 'analytic_distribution': analytic_distribution,
                    'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                    'amount_currency': dist_amount,
                }
                move_vals['line_ids'].append((0,0, move_line_2))
                last_line -= 1
                remaining_amount -= dist_amount
        return move_vals
