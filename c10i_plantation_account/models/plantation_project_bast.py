from odoo import models, api


class PlantationProjectBast(models.Model):
    _inherit = 'plantation.project.bast'

    @api.onchange('date')
    def onchange_date(self):
        if not self.date:
            return
        cost_allocation_id = self.project_id.cost_center_id.type_id.id
        cost_center_id = self.project_id.cost_center_id.id
        account_id = self.project_id.category_id.cip_account_id.id
        date_start = str(self.project_id.plan_date_start)
        date_end = str(self.date)
        find_cost_query = """SELECT balance
FROM account_move_line
WHERE account_id = %d
	AND cost_allocation_id = %d
	AND cost_center_id = %d
	AND cost_activity_id = %d
	AND parent_state = 'posted'
	AND date BETWEEN '%s' AND '%s';"""
        for line in self.line_ids:
            self._cr.execute(find_cost_query% (account_id, cost_allocation_id, cost_center_id, line.cost_activity_id.id, date_start, date_end))
            move_line_balances_lst = self._cr.fetchall()
            move_line_balance = 0.0
            if move_line_balances_lst:
                move_line_balance = sum([tup[0] for tup in move_line_balances_lst])
            line.actual_cost = move_line_balance
