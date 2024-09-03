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

class ResCompany(models.Model):
    _inherit        = 'res.company'

    create_monthly_earning_accrual = fields.Boolean("Monthly Earning")
    current_year_earning_account_id = fields.Many2one('account.account', 'Monthly Earning Account')
    earning_account_id = fields.Many2one('account.account', 'Retained Earning Account')
    counterpart_earning_account_id = fields.Many2one('account.account', 'Counter-part Earning Account')

    write_off_default_journal_id    = fields.Many2one(comodel_name='account.journal', string="Journal", help='Please complete the help')
    account_write_off               = fields.Many2one('account.account', 'Account Write Off')