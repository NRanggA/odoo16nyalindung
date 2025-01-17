from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mydaya_user_login = fields.Char(groups="hr.group_hr_user")
    mydaya_user_pwd = fields.Char(groups="hr.group_hr_user")
    # lat_acuan = fields.Char()
    # long_acuan = fields.Char()
    # value_jarak = fields.Char()


    def _check_unique_mydaya_user_login(self):
        for record in self:
            if record.mydaya_user_login:
                existing_user = self.search([
                    ('mydaya_user_login', '=', record.mydaya_user_login),
                    ('id', '!=', record.id)
                ], limit=1)
                
                if existing_user:
                    raise ValidationError(_(f"User login {record.mydaya_user_login} sudah ada pada karyawan lain. Harus unik jika diisi."))

    @api.model
    def create(self, vals):
        record = super(HrEmployee, self).create(vals)
        record._check_unique_mydaya_user_login()
        return record

    def write(self, vals):
        result = super(HrEmployee, self).write(vals)
        self._check_unique_mydaya_user_login()
        return result