from odoo import api, fields, models, _

class EmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    work_start_date = fields.Date(groups="hr.group_hr_user")
    termination_date = fields.Date(groups="hr.group_hr_user")

    ##################################################
    #                     HELPER                     #
    ##################################################
    def _get_biaya_jabatan2(self, yearly_income):
        # TODO : incase this variable is dynamic and you want to put it on the configuration form view
        # then you should override this module to get the result form that field
        return (yearly_income*5.0/100.0) if (yearly_income*5.0/100.0) < 6000000.0 else 6000000.0

    def _get_percent_denda(self):
        # TODO : incase this variable is dynamic and you want to put it on the configuration form view
        # then you should override this module to get the result form that field
        return 20.0/100.0

    def _check_npwp(self):
        if not self.npwp:
            return False
        elif self.npwp:
            # check_digit = list(set(self.npwp.replace('.','').replace('-','')))
            # if len(check_digit) == 1 and check_digit[0]=='0' or self.npwp=='False':
            #     return False
            check_npwp = self.npwp.replace(' ','').replace('.','').replace('-','').replace('0','')
            if not check_npwp or check_npwp=='False':
                return False
            else:
                return True