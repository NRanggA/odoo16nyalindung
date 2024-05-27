from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    outbound_direct_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.outbound_direct_payment_account_id', readonly=False,
        string="Outbound Direct Payment",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'payable'), \
            ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_payable').id,
        help='Please complete the help')
    inbound_direct_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.inbound_direct_payment_account_id', readonly=False,
        string="Inbound Direct Payment",
        domain=lambda self: "[('company_id', '=', company_id), ('deprecated','=',False),\
            ('internal_type', '=', 'receivable'), \
            ('user_type_id','=',%s)]"%self.env.ref('account.data_account_type_receivable').id,
        help='Please complete the help')