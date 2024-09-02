from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_advance_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Employee Advance Account",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'other'), ('reconcile','=',True)",
        help='Please complete the help')

    contra_account_for_advance = fields.Many2one(
        comodel_name='account.account',
        string="Contra Account for Advance",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'other'), ('reconcile','=',True)",
        help='Please complete the help')
    
    employee_advance_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        help='Please complete the help')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employee_advance_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.employee_advance_account_id', readonly=False,
        string="Employee Advance Account",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('reconcile','=',True)]",
        help='Please complete the help')

    contra_account_for_advance = fields.Many2one(
        comodel_name='account.account',
        related='company_id.contra_account_for_advance', readonly=False,
        string="Contra Account for Advance",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('reconcile','=',True)]",
        help='Please complete the help')
    
    employee_advance_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.employee_advance_journal_id', readonly=False,
        string="Journal",
        help='Please complete the help')