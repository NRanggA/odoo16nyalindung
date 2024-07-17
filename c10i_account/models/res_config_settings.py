# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_monthly_earning_accrual = fields.Boolean(related='company_id.create_monthly_earning_accrual', string='Create Monthly Earning', readonly=False)
    current_year_earning_account_id = fields.Many2one('account.account', related='company_id.current_year_earning_account_id', 
        string='Monthly Earning Account', readonly=False,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]") #('internal_type', '=', 'other'), 
    earning_account_id = fields.Many2one('account.account', related='company_id.earning_account_id', 
        string='Retained Earning Account', readonly=False,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]") #('internal_type', '=', 'other'), 
    counterpart_earning_account_id = fields.Many2one('account.account', related='company_id.counterpart_earning_account_id', 
        string='Counter-part Earning Account', readonly=False,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]") #('internal_type', '=', 'other'), 