from odoo import models, fields, api, _

class NyAttendanceLog(models.Model):
    _name = 'ny.attendance.log'
    _description = 'My Daya Attendance Log'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    longitude = fields.Char()
    latitude = fields.Char()
    waktu = fields.Datetime() # 2024-09-19 14:53:53 
    # version = fields.Char()
    foto = fields.Binary()
    keterangan = fields.Text()
    statusmasuk = fields.Char() # WFO// isi dengan WFO,WFH