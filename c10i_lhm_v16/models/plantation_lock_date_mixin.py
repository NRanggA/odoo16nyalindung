from odoo import models, fields, api

class LockDateMixin(models.AbstractModel):
    _name = 'lock.date.mixin'
    _description = 'Mixin untuk Validasi Lock Date'

    # @api.model
    # def create(self, vals):
    #     self._check_lock_date(vals.get('date') if vals.get('date') else vals.get('date_nap'))
    #     return super().create(vals)

    # def write(self, vals):
    #     if 'date' in vals:
    #         self._check_lock_date(vals['date'])
    #     return super().write(vals)

    @api.model
    def create(self, vals):
        date_values = [vals[field] for field in ['date', 'date_nap', 'date_start', 'date_end'] if vals.get(field)]
        for date in date_values:
            self._check_lock_date(date)
        return super().create(vals)

    def write(self, vals):
        if any(field in vals for field in ['date', 'date_nap', 'date_start', 'date_end']):
            date_values = [
                vals.get('date', self.date if hasattr(self, 'date') else False),
                vals.get('date_nap', self.date_nap if hasattr(self, 'date_nap') else False),
                vals.get('date_start', self.date_start if hasattr(self, 'date_start') else False),
                vals.get('date_end', self.date_end if hasattr(self, 'date_end') else False),
            ]
            for date in date_values:
                if date:
                    self._check_lock_date(date)

        return super().write(vals)

    
    def _check_lock_date(self, date):
        if date:
            lock_date = self.env.company.plantation_lock_date
            date = fields.Date.from_string(date) if isinstance(date, str) else date
            lock_date = fields.Date.from_string(lock_date) if isinstance(lock_date, str) else lock_date
            
            # if date <= lock_date:
            #     raise models.ValidationError("Tidak dapat membuat transaksi di periode yang telah di tutup.")
            if lock_date and date <= lock_date:
                raise models.ValidationError("Tidak dapat membuat transaksi di periode yang telah ditutup.")

