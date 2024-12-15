from odoo import models, api, fields

class Block(models.Model):
    _inherit = 'lhm.plant.block'

    with_ongkos_pikul = fields.Boolean()
    payroll_gc_dest_activity_id = fields.Many2one('lhm.activity', string='Default Payroll GC to Block Activity')