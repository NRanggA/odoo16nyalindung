from odoo import models, fields, api

class PlantationLockDateWizard(models.TransientModel):
    _name = 'plantation.lock.date.wizard'
    _description = 'Wizard untuk Set Plantation Lock Date'

    lock_date = fields.Date(string='Lock Date', required=True)

    @api.model
    def default_get(self, fields):
        res = super(PlantationLockDateWizard, self).default_get(fields)
        company = self.env.company
        res.update({'lock_date': company.plantation_lock_date})
        return res

    def action_set_lock_date(self):
        company = self.env.company
        company.sudo().write({'plantation_lock_date': self.lock_date})