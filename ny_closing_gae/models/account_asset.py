from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    # boolean penanda 
    gae_distribution_id = fields.Many2one('gae.plan', string='GAE Distribution')


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        move_vals = super(AccountAssetDepreciationLine, self)._prepare_move(line)
        asset_id = line[0].asset_id
        
        if asset_id.gae_distribution_id:
            category_id = line.asset_id.category_id
            analytic_distribution = line.asset_id.analytic_distribution
            depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            prec = company_currency.decimal_places
            amount = current_currency._convert(
                line.amount, company_currency, line.asset_id.company_id, depreciation_date)
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
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
                    'account_id': category_id.account_depreciation_expense_id.id,
                    'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'partner_id': line.asset_id.partner_id.id,
                    'analytic_distribution': analytic_distribution,
                    'currency_id': company_currency != current_currency and current_currency.id or company_currency.id,
                    'amount_currency': dist_amount,
                }
                move_vals['line_ids'].append((0,0, move_line_2))
                last_line -= 1
                remaining_amount -= dist_amount

        return move_vals
