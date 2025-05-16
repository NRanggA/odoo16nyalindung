from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round

class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    # asset_acquisition_id = fields.Many2one("asset.acquisition", string="Origin")
    # disposal_id = fields.Many2one('account.asset.disposal', string="Sell / Disposal")
    # sell_account_move_id = fields.Many2one('account.move', 'Sell Account Move', related="disposal_id.sell_account_move_id")
    # reason = fields.Text(string="Sell/Dispose Reason", related="disposal_id.reason")
    acquisition_line_ids = fields.Many2many('account.asset.acquisition.line', 'acquisition_line_account_asset_rel', 
                                'asset_id', 'acquisition_line_id', string='Asset')
    parent_id = fields.Many2one('account.asset.asset', string='Parent Asset', ondelete='restrict')
    child_ids = fields.One2many('account.asset.asset', 'parent_id', string='Child Assets')
    child_count = fields.Integer(compute='_count_child', string='# Child Assets')

    def _count_child(self):
        for asset in self:
            asset.child_count = self.search_count([('parent_id','=',asset.id)])

    @api.depends('depreciation_line_ids.move_id', 'depreciation_line_ids.child_depr_ids.move_id')
    def _entry_count(self):
        asset_with_parent = self.filtered(lambda a: a.parent_id)
        super(AccountAsset, asset_with_parent)._entry_count()
        for asset in self - asset_with_parent:
            count = self.env['account.asset.depreciation.line'].search_count([
                ('asset_id', '=', asset.id), 
                ('move_check', '=', True)])
            asset.entry_count = count or 0
    
    @api.depends('value', 
                 'salvage_value', 
                 'depreciation_line_ids', 
                 'depreciation_line_ids.move_check', 
                 'depreciation_line_ids.amount')
    def _amount_residual(self):
        for rec in self:
            total_amount = 0.0
            for line in rec.depreciation_line_ids:
                if line.move_check:
                    total_amount += line.amount
            rec.value_residual = rec.value - total_amount - rec.salvage_value

    def open_entries(self):
        self.ensure_one()
        if not self.child_ids:
            res = super(AccountAsset, self).open_entries()
        move_ids = []
        for depreciation_line in self.depreciation_line_ids.child_depr_ids:
            if depreciation_line.move_id:
                move_ids.append(depreciation_line.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }
    
    def open_child(self):
        self.ensure_one()
        if not self.child_ids:
            raise UserError(_('No child assets found.'))
        action = self.env["ir.actions.actions"]._for_xml_id("om_account_asset.action_account_asset_asset_form")
        action['domain'] = [('id', 'in', self.child_ids.ids)]
        action['context'] = {
            'create': False,
            'edit': False,
            'delete': False,
            # 'search_default_parent_id': self.id,
            # 'search_default_child_ids': True,
        }
        return action

    def open_parent(self):
        self.ensure_one()
        if not self.parent_id:
            raise UserError(_('No Parent asset found.'))
        action = self.env["ir.actions.actions"]._for_xml_id("om_account_asset.action_account_asset_asset_form")
        action['res_id'] = self.parent_id.id
        action['views'] = [(self.env.ref('om_account_asset.view_account_asset_asset_form').id, 'form')]
        action['context'] = {
            'create': False,
            'edit': False,
            'delete': False,
            # 'search_default_parent_id': self.id,
            # 'search_default_child_ids': True,
        }
        return action
    
    def compute_parent_depreciation_board(self):
        for parent in self:
            query = """
                SELECT
                    dummy.date,
                    array_agg(dummy.parent_depr_id) as parent_depr_id,
                    array_agg(dummy.depre_id) as depre_ids,
                    SUM(dummy.amount) as amount,
                    SUM(dummy.remaining_value) as remaining_value
                FROM
                    ((SELECT
                        board1.depreciation_date as date,
                        board1.id as parent_depr_id,
                        NULL as depre_id,
                        0 as amount,
                        0 as remaining_value
                    FROM
                        account_asset_depreciation_line board1
                    WHERE board1.asset_id = %s)
                    UNION ALL
                    (SELECT
                        board2.depreciation_date as date,
                        NULL as parent_depr_id,
                        board2.id as depre_id,
                        board2.amount,
                        board2.remaining_value
                    FROM
                        account_asset_depreciation_line board2
                    WHERE board2.asset_id%s)) dummy
                GROUP BY dummy.date
            """
            query = query % (str(parent.id), 
                             f" in {str(tuple(parent.child_ids.ids))}" if len(parent.child_ids.ids)>1 else f"={parent.child_ids.id}"
                             )
            self.env.cr.execute(query)
            seq = 1
            depreciated_value = 0.0
            depr_to_write = []
            depr_to_create = []
            for grouped in self.env.cr.dictfetchall():
                parent_depr_ids = list(set([x for x in grouped['parent_depr_id'] if x is not None]))
                depreciated_value += grouped['amount']
                if parent_depr_ids:
                    parent_depr_line = self.env['account.asset.depreciation.line'].browse(parent_depr_ids)
                    seq += parent_depr_line.sequence
                    # parent_depr_line.write({
                    #     'amount': grouped['amount'],
                    #     'remaining_value': grouped['remaining_value'],
                    #     'depreciated_value': depreciated_value,
                    #     'child_depr_ids': [(6, 0, list(set(grouped['depre_ids'])))],
                    # })
                    depr_to_write.append((1, parent_depr_line.id, {
                        'amount': grouped['amount'],
                        'remaining_value': grouped['remaining_value'],
                        'depreciated_value': depreciated_value,
                        'child_depr_ids': [(6, 0, list(set(grouped['depre_ids'])))],
                    }))
                else:
                    # self.env['account.asset.depreciation.line'].create({
                    #     'sequence': seq,
                    #     'name': f"/{seq}",
                    #     'asset_id': parent.id,
                    #     'depreciation_date': grouped['date'],
                    #     'amount': grouped['amount'],
                    #     'remaining_value': grouped['remaining_value'],
                    #     'depreciated_value': depreciated_value,
                    #     'child_depr_ids': [(6, 0, list(set(grouped['depre_ids'])))],
                    # })
                    depr_to_create.append((0,0,{
                        'sequence': seq,
                        'name': f"/{seq}",
                        'asset_id': parent.id,
                        'depreciation_date': grouped['date'],
                        'amount': grouped['amount'],
                        'remaining_value': grouped['remaining_value'],
                        'depreciated_value': depreciated_value,
                        'child_depr_ids': [(6, 0, list(set(grouped['depre_ids'])))],
                    }))
                seq += 1
            
            parent.write({
                'value': sum(parent.child_ids.mapped('value')),
                'beginning_balance': any([x.beginning_balance==True for x in parent.child_ids]),
                'accumulated_depreciation': sum(parent.child_ids.mapped('accumulated_depreciation')),
                'depreciation_line_ids': depr_to_write + depr_to_create,
            })
        return True

    def compute_depreciation_board(self):
        self.ensure_one()
        if self.child_ids:
            res = self.compute_parent_depreciation_board()
        else:
            res = super(AccountAsset, self).compute_depreciation_board()
            if self.parent_id:
                self.parent_id.compute_parent_depreciation_board()
        return res
    
    def _compute_entries(self, date, group_entries=False):
        asset_with_child = self.filtered(lambda a: a.child_count)

        created_moves = super(AccountAsset, self - asset_with_child)._compute_entries(date=date, group_entries=False)

        return created_moves
    
class DepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    parent_depr_id = fields.Many2one('account.asset.depreciation.line', string='Parent Deprec', ondelete='restrict')
    child_depr_ids = fields.One2many('account.asset.depreciation.line', 'parent_depr_id', string='Child Depreciations')
    count_child_depr = fields.Integer(compute='_count_depr_childs', store=True, string='# Child Depreciations')

    @api.depends('child_depr_ids')
    def _count_depr_childs(self):
        for line in self:
            line.count_child_depr = self.search_count([('parent_depr_id','=',line.id)])

    @api.depends('move_id', 'child_depr_ids.move_id', 'asset_id.state')
    def _get_move_check(self):
        depr_with_child = self.filtered(lambda d: d.child_depr_ids)
        super(DepreciationLine, self - depr_with_child)._get_move_check()
        for line in depr_with_child:
            line.move_check = all([bool(x.move_id) for x in line.child_depr_ids])