from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class ClosingProcess(models.Model):
    _inherit = 'closing.process'

    state = fields.Selection(selection_add=[('closing_gae', 'Closing GAE')], ondelete={'closing_gae': 'set default'})

    mark_closing_gae_is_done = fields.Boolean('Mark Closing GAE as Done')
    closing_gae_ids = fields.One2many('closing.gae', 'closing_process_id', string='Closing GAE')

    def get_gae(self):
        for rec in self:
            if not rec.date_from or not rec.date_to:
                raise ValidationError("Silahkan isi 'Date From' dan 'Date To' terlebih dahulu untuk mendapatkan data GAE")
            existing_gae = self.env['closing.gae'].search([
                ('closing_process_id', '=', rec.id),
                ('date_from', '=', rec.date_from),
                ('date_to', '=', rec.date_to),
            ], limit=1)
            domain = [('gae_distribution_id', '!=', False),('date', '>=', rec.date_from), ('date', '<=', rec.date_to), ('parent_state', '=', 'posted')]
            if existing_gae:
                if len(existing_gae.ids)==1:
                    domain.append(('gae_distribution_id', '=', existing_gae.gae_distribution_id.id))
                else:
                    domain.append(('gae_distribution_id', 'not in', existing_gae.gae_distribution_id.ids))
            
            account_move_lines = self.env['account.move.line'].search(domain)
            to_create = []
            for line in account_move_lines.mapped('gae_distribution_id'):
                to_create.append((0, 0, {
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'gae_distribution_id': line.id,
                }))
            if to_create:
                self.env['closing.gae'].create(to_create)


    def button_continue_to_closing_gae(self):
        for rec in self:
            if not rec.mark_closing_nursery_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_gae()
            rec.write({'state': 'closing_gae'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def summerize_gae_cost(self):
        for rec in self:
            rec.closing_gae_ids.summarize_move_line()
    
    def create_account_move_gae(self):
        for rec in self:
            rec.closing_gae_ids.create_account_move()
            rec.closing_gae_ids.closing_move_id._post(soft=False)
    
    def button_continue_to_closing_plantation(self):
        for rec in self:
            # if not rec.mark_closing_laboratory_is_done:
            if not rec.mark_closing_gae_is_done:
                raise ValidationError(f"Silahkan centang 'Mark as Done' atas proses '{rec.state.replace('_',' ')}' terlebih dahulu untuk melanjutkan ke proses berikutnya") 
            rec.get_plantation()
            rec.write({'state': 'closing_plantation'})
            # rec.compute_initial_and_cost_fg2()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    SELECTION = [('draft','New'),
        ('running_workshop', 'Running Workshop'),
        ('running_vehicle', 'Running Vehicle'),
        ('running_machine', 'Running Machine'),
        ('closing_laboratory', 'Closing Laboratory'),
        ('closing_project', 'Closing Project'),
        ('closing_nursery', 'Closing Nursery'),
        ('closing_gae', 'Closing GAE'),
        ('closing_plantation', 'Closing Plantation'),
        ('closing_production', 'Closing Production'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]
    
    def button_back(self):
        selection_key = list(map(lambda x: x[0], self.SELECTION))
        for rec in self:
            index_state = selection_key.index(rec.state)
            if rec.state=='closing_laboratory':
                rec.closing_laboratory_ids.action_cancel()
            elif rec.state=='closing_project':
                rec.closing_project_ids.action_cancel()
            elif rec.state=='closing_nursery':
                rec.closing_nursery_ids.action_cancel()
            elif rec.state=='closing_gae':
                rec.closing_gae_ids.action_cancel()
            elif rec.state=='closing_plantation':
                rec.closing_plantation_ids.action_cancel()
            elif rec.state=='closing_production':
                rec.closing_plantation_ids.action_cancel()
            
            if index_state:
                rec.write({'state': selection_key[index_state-1],
                    f"mark_{selection_key[index_state-1]}_is_done": False})