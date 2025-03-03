from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    # payroll_upah_account_id = fields.Many2one('account.account', string='Akun Upah', groups="hr.group_hr_user")
    # payroll_premi_produksi_account_id = fields.Many2one('account.account', string='Akun Premi Produksi', groups="hr.group_hr_user")
    # payroll_other_account_id = fields.Many2one('account.account', string='Akun Benefit Lainnya', groups="hr.group_hr_user")
    payroll_upah_activity_id = fields.Many2one('lhm.activity', string='GC Aktifitas Upah', groups="hr.group_hr_user")
    payroll_premi_produksi_activity_id = fields.Many2one('lhm.activity', string='GC Aktifitas Premi Produksi', groups="hr.group_hr_user")
    payroll_other_activity_id = fields.Many2one('lhm.activity', string='GC Aktifitas Benefit Lainnya', groups="hr.group_hr_user")