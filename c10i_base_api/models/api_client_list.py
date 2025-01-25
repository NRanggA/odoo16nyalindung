from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class APIClientList(models.Model):
    _name = 'c10i_base_api.client.list'
    _description = "Client Whitelist"

    name = fields.Char('IP Address')
    number_of_error_half_hour_allowed = fields.Integer('Number of Error Allowed per 30 Minutes', default=30)
    next_temp_blacklist_reset = fields.Datetime('Next Reset')
    number_of_error_allowed = fields.Integer('Number of Error Allowed', default=100)
    blacklist = fields.Boolean('Blacklisted')

    def write(self, update_vals):
        # if 'number_of_error_allowed' in update_vals.keys():
        #     if update_vals['number_of_error_allowed'] > 20:
        #         update_vals.update({'blacklist': True})
        if 'number_of_error_half_hour_allowed' in update_vals.keys() and 'number_of_error_allowed' in update_vals.keys():
            if update_vals['number_of_error_allowed']<=0:
                update_vals.update({'blacklist': True})
            elif update_vals['number_of_error_half_hour_allowed']<=0 and update_vals['number_of_error_allowed']>0:
                update_vals.update({'next_temp_blacklist_reset': fields.Datetime.now() + relativedelta(minutes=30)})
        
        if 'blacklist' in update_vals.keys() and update_vals['blacklist']==False:
            update_vals.update({
                'number_of_error_half_hour_allowed': 30,
                'number_of_error_allowed': 100,
            })
        return super().write(update_vals)