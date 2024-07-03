from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    outbound_direct_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Outbound Direct Payment",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'payable')]",
        help='Please complete the help')
    # ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_payable').id,
    inbound_direct_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Inbound Direct Payment",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'receivable')]",
        help='Please complete the help')
    # ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_receivable').id,