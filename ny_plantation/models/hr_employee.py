from odoo import models, api, fields, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mandor_id           = fields.Many2one(comodel_name="hr.employee", string="Mandor", ondelete="restrict",
                                related='kemandoran_id.mandor_id', readonly=True, store=True)