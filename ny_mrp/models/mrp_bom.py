from odoo import models, fields, api, _
from datetime import datetime

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sequence_id = fields.Many2one('ir.sequence', string='Reference Sequence')

    def create_sequence(self):
        for bom in self:
            # current_date = datetime.now()
            # month = current_date.strftime('%m')  
            # year = current_date.strftime('%Y') 
            if bom.code and not bom.sequence_id:
                sequence = self.env['ir.sequence'].create({
                    'name': f"Sequence {bom.code}",
                    'code': f"mrp.bom.{bom.code}",
                    'prefix': f"MO/{bom.code}/",
                    'padding': 3,
                    'company_id': bom.company_id.id
                })
                bom.sequence_id = sequence.id
                
    
    def create(self, vals):
        bom = super(MrpBom, self).create(vals)
        bom.create_sequence()
        return bom
    
    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        if vals.get('code'):
            self.create_sequence()
        return res
            