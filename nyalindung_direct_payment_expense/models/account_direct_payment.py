from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DirectPayment(models.Model):
    _inherit = 'account.direct.payment'

    settelement_date = fields.Date('Settelement Date', required=True)

    def employee_submit(self):
        res = super().employee_submit()
        self.validation_settlement_date_by_date()
        return res

    def validation_settlement_date_by_date(self):
        for record in self:
            if record.settelement_date < record.date:
                raise ValidationError("Settlement Date cannot be less than Date")
            
    def validation_setteled(self):
        for record in self:
            setteled = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('payment_state', '!=', 'not_paid'),
            ], limit=1, order='settelement_date desc')
            
            if setteled and record.date > setteled.settelement_date:
                raise ValidationError("You can't request direct payment if the date is more than the your direct payment that not setteled")

    @api.model
    def create(self, vals):
        record = super(DirectPayment, self).create(vals)
        record.validation_setteled()
        return record

    def write(self, vals):
        res = super(DirectPayment, self).write(vals)
        self.validation_setteled()
        return res

class DirectPaymentLine(models.Model):
    _inherit = 'account.direct.payment.line'

    plantation_location_type_id = fields.Many2one(comodel_name="lhm.location.type", string="Tipe Lokasi", ondelete="restrict")
    plantation_location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi", ondelete="restrict")
    plantation_activity_id = fields.Many2one(comodel_name="lhm.activity", string="Aktivitas", ondelete="restrict")    

    @api.onchange('plantation_location_type_id')
    def _onchange_plantation_location_type_id(self):
        if self.plantation_location_type_id:
            self.plantation_location_id = False
            self.plantation_activity_id = False
            # if self.plantation_location_type_id.no_line and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
            #     self.account_id = False
            # else:
            #     self.account_id = self.plantation_location_type_id.account_id.id if self.plantation_location_type_id.account_id else False

    @api.onchange('plantation_location_id')
    def _onchange_plantation_location_id(self):
        if self.plantation_location_id:
            self.plantation_activity_id = False

    # @api.onchange('plantation_activity_id')
    # def _onchange_plantation_activity_id(self):
    #     if self.plantation_activity_id and (self.plantation_location_type_id.general_charge or self.plantation_location_type_id.indirect):
    #         self.account_id = self.plantation_activity_id.account_id.id if self.plantation_activity_id.account_id else False