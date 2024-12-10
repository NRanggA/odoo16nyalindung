from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_consume_ids = fields.One2many('mrp.manual.consume', 'component_consume_production_id', string='Manual Consumed')

    # def action_draft(self):
    #     for production in self:
    #         production.state = 'draft'
    #         # production.reservation_state = False
    #         # production.consumption = 'flexible'

    @api.model
    def create(self, vals):
        current_date = datetime.today().strftime("%Y-%m-%d")

        sequence_count = self.env['mrp.production'].search_count([
            ('create_date', '>=', f"{current_date} 00:00:00"),
            ('create_date', '<=', f"{current_date} 23:59:59")
        ]) + 1

        sequence_str = f"{sequence_count:02d}"

        vals['name'] = f"MO/{current_date}/{sequence_str}"

        return super(MrpProduction, self).create(vals)

    def action_draft(self):
        for production in self:
            for move in production.move_raw_ids | production.move_finished_ids:
                move.state = 'draft'
                move.quantity_done = 0.0
            for workorder in production.workorder_ids:
                workorder.state = 'pending'
            production.state = 'draft'
    
    def get_target_production(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_mrp.wizard_mrp_sheet_to_produce_action")
        action['context'] = {'default_mrp_id': self.id,
                             'default_product_latex_id': self.bom_id.bom_line_ids.filtered(lambda x: x.product_id.name=='Latex').product_id.id,
                             'default_bom_id': self.bom_id.id}
        return action
