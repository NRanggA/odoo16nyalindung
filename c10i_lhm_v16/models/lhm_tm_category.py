from odoo import models, fields, api, _



class LhmTmCategory(models.Model):
    _name        = 'lhm.tm.category'
    _description = 'LHM TM Category'

    name        = fields.Char('Category')
    min_age     = fields.Integer('Min Age')
    max_age     = fields.Integer('Max Age')