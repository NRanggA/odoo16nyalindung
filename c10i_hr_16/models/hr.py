
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import time
import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class hr_employee(models.Model):
    _inherit        = 'hr.employee'
    _description    = 'Employee Management'

    work_phone_company      = fields.Char('No. Telephone Perusahaan', related='address_id.phone', readonly=True) #sudah ada
    mobile_phone_company    = fields.Char('No. Handphone Perusahaan', related='address_id.mobile', readonly=True) #sudah ada
    work_email_company      = fields.Char('Alamat Email Perusaahaan', related='address_id.email', readonly=True) #sudah ada
    work_location_company   = fields.Char('Lokasi Pekerjaan') ##sudah ada tapi berubah menjadi work_location_id
    # gender          = fields.Selection([
    #                     ('Laki-laki', 'Laki-laki'),
    #                     ('Perempuan', 'Perempuan'),
    #                     ('Lainnya', 'Lainnya')
    #                     ], string='Jenis Kelamin', groups='hr.group_hr_user') # Sudah ada
    # marital         = fields.Selection([
    #                     ('TK', 'Tidak Menikah'),
    #                     ('K', 'Menikah'),
    #                     ], string='Status Pernikahan', groups='hr.group_hr_user') #sudah ada

    #New Fields
    street                  = fields.Char(string="Alamat 1")
    street2                 = fields.Char(string="Alamat 2")
    zip                     = fields.Char(string="Kode Pos")
    country_id              = fields.Many2one('res.country', 'Negara')
    state_id                = fields.Many2one('res.country.state', 'Provinsi', domain="[('country_id', '=', country_id)]")
    city_id                 = fields.Many2one('res.city', 'Kota/ Kabupaten', domain="[('state_id', '=', state_id),('country_id', '=', country_id)]")
    nationality_id          = fields.Many2one('res.country', 'Kewarganegaraan')
    no_induk                = fields.Char('NIK',)
    npwp                    = fields.Char('NPWP', )
    bpjs_kesehatan          = fields.Char('BPJS Kesehatan', )
    bpjs_ketenagakerjaan    = fields.Char('BPJS Ketenagakerjaan', )
    ptkp_id                 = fields.Many2one(comodel_name='hr.ptkp', string="PTKP", tracking=True)
    religion                = fields.Many2one(comodel_name='hr.employee.religion', string="Agama")
    education_ids           = fields.One2many('hr.employee.education.line','employee_id', string="Jenjang Pendidikan", )
    license_ids             = fields.One2many('hr.employee.driving.license.line', 'employee_id', string="SIM", )
    experinece_ids          = fields.One2many('hr.employee.experience.line', 'employee_id', string="Pengalaman Kerja", )
    ptkp_history_ids        = fields.One2many('hr.ptkp.history', 'employee_id', string="PTKP History", )
    calendar_id             = fields.Many2one('resource.calendar', string="Jam Kerja")
    pensiun                 = fields.Boolean(string='Pensiun', default=False)
    place_of_birth          = fields.Char('Tempat Lahir')

    @api.model
    def create(self, values):
        res =super(hr_employee, self).create(values)
        if res.ptkp_id:
            self.env['hr.ptkp.history'].create({
                'name'          : res.name,
                'employee_id'   : res.id,
                'ptkp_id'       : res.ptkp_id and res.ptkp_id.id,
                'date'          : datetime.datetime.now().strftime('%Y-%m-%d')
            })
        return res

    def write(self, values):
        if values.get('ptkp_id'):
            self.env['hr.ptkp.history'].create({
                'name'          : self.name,
                'employee_id'   : self.id,
                'ptkp_id'       : self.ptkp_id and self.ptkp_id.id,
                'date'          : datetime.datetime.now().strftime('%Y-%m-%d')
            })
        return super(hr_employee, self).write(values)


class hr_ptkp(models.Model):
    _name           = 'hr.ptkp'
    _description    = 'C10i PTKP Management'

    name            = fields.Char('Status', required=True)
    code            = fields.Char('Kode', required=True)
    marital         = fields.Selection([
                        ('single', 'Tidak Menikah'),
                        ('married', 'Menikah'),
                        ], string='Status Pernikahan')
    children        = fields.Integer('Jumlah Anak')
    value           = fields.Float('Nilai', required=True)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    active          = fields.Boolean('Aktif', required=True, default=True)

class hr_ptkp_history(models.Model):
    _name           = 'hr.ptkp.history'
    _description    = 'C10i PTKP History'

    name            = fields.Char('Status', required=True)
    ptkp_id         = fields.Many2one('hr.ptkp', string='PTKP')
    employee_id     = fields.Many2one('hr.employee', string='Employee')
    date            = fields.Date("Change Date")
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

class hr_employee_religion(models.Model):
    _name           = 'hr.employee.religion'
    _description    = 'C10i Religion Management'

    name            = fields.Char('Agama', required=True)
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    active          = fields.Boolean('Aktif', required=True, default=True)


class hr_employee_education_line(models.Model):
    _name           = 'hr.employee.education.line'
    _description    = 'C10i Education Information'

    name            = fields.Char('Nama Sekolah', required=True)
    level           = fields.Selection([
                        ('Tidak Sekolah', 'Tidak Sekolah'),
                        ('TK', 'TK'),
                        ('SD', 'SD/MI'),
                        ('SMP', 'SMP/MTs'),
                        ('SMA', 'SMA/SMK/MA'),
                        ('D3', 'D3'),
                        ('D4', 'D4'),
                        ('S1', 'S1'),
                        ('S2', 'S2'),
                        ('S3', 'S3'),
                        ], string='Jenjang Pendidikan', required=True)
    major           = fields.Char('Jurusan', required=False)
    start_year      = fields.Integer('Tahun Masuk')
    end_year        = fields.Integer('Tahun Lulus')
    note            = fields.Char('Catatan', required=False)
    employee_id     = fields.Many2one(comodel_name="hr.employee", string="Employee")

class hr_employee_driving_license_line(models.Model):
    _name           = 'hr.employee.driving.license.line'
    _description    = 'C10i Driving Licence Information'

    name            = fields.Char('No. SIM', required=True)
    license_type    = fields.Selection([
                            ('SIM A', 'SIM A'),
                            ('SIM B1', 'SIM B1'),
                            ('SIM B2', 'SIM B2'),
                            ('SIM C', 'SIM C'),
                            ('SIM D', 'SIM D'),
                        ], string='Jenis SIM', required=True)
    expiry_date     = fields.Date("Tanggal Kadaluarsa")
    note            = fields.Char('Catatan', required=False)
    employee_id     = fields.Many2one(comodel_name="hr.employee", string="Employee")


class hr_employee_experience_line(models.Model):
    _name           = 'hr.employee.experience.line'
    _description    = 'C10i Experience Information'

    name            = fields.Char('Nama Perusahaan', required=True)
    job_name        = fields.Char("Nama Pekerjaan", required=True)
    start_date      = fields.Date("Tanggal Mulai")
    end_date        = fields.Date("Tanggal Selasai")
    note            = fields.Char("Catatan", required=False)
    employee_id     = fields.Many2one(comodel_name="hr.employee", string="Employee")