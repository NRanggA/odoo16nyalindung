from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    equip_register_id = fields.Many2one('equipment.register', string='Equip Register')
    acquisition_id = fields.Many2one('account.asset.acquisition', string='Acquisition')