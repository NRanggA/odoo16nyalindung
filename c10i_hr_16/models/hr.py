
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
    # work_location_company   = fields.Char('Lokasi Pekerjaan', groups="hr.group_hr_user") ##sudah ada tapi berubah menjadi work_location_id
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
    street                  = fields.Char(string="Alamat 1", groups="hr.group_hr_user")
    street2                 = fields.Char(string="Alamat 2", groups="hr.group_hr_user")
    zip                     = fields.Char(string="Kode Pos", groups="hr.group_hr_user")
    country_id              = fields.Many2one('res.country', 'Negara', groups="hr.group_hr_user")
    state_id                = fields.Many2one('res.country.state', 'Provinsi', domain="[('country_id', '=', country_id)]", groups="hr.group_hr_user")
    city_id                 = fields.Many2one('res.city', 'Kota/ Kabupaten', domain="[('state_id', '=', state_id),('country_id', '=', country_id)]", groups="hr.group_hr_user")
    nationality_id          = fields.Many2one('res.country', 'Kewarganegaraan', groups="hr.group_hr_user")
    no_induk                = fields.Char('NIK', groups="hr.group_hr_user")
    npwp                    = fields.Char('NPWP', groups="hr.group_hr_user")
    
    bpjs_kesehatan          = fields.Char('BPJS Kesehatan', groups="hr.group_hr_user")
    bpjs_kesehatan_add_person = fields.Integer("Tanggungan BPJS Kesehatan")
    bpjs_ketenagakerjaan    = fields.Char('BPJS Ketenagakerjaan', groups="hr.group_hr_user")
    ptkp_id                 = fields.Many2one(comodel_name='hr.ptkp', string="PTKP", tracking=True, groups="hr.group_hr_user")
    religion                = fields.Many2one(comodel_name='hr.employee.religion', string="Agama", groups="hr.group_hr_user")
    education_ids           = fields.One2many('hr.employee.education.line','employee_id', string="Jenjang Pendidikan", groups="hr.group_hr_user")
    license_ids             = fields.One2many('hr.employee.driving.license.line', 'employee_id', string="SIM", )
    experinece_ids          = fields.One2many('hr.employee.experience.line', 'employee_id', string="Pengalaman Kerja", groups="hr.group_hr_user")
    ptkp_history_ids        = fields.One2many('hr.ptkp.history', 'employee_id', string="PTKP History", groups="hr.group_hr_user")
    calendar_id             = fields.Many2one('resource.calendar', string="Jam Kerja", groups="hr.group_hr_user")
    pensiun                 = fields.Boolean(string='Pensiun', default=False, groups="hr.group_hr_user")
    place_of_birth          = fields.Char('Tempat Lahir', groups="hr.group_hr_user")

    def name_get(self):
        result = []        
        for rec in self:
            if rec.no_induk:
                result.append((rec.id, '%s - %s' % (rec.name,rec.no_induk)))
            else:
                result.append((rec.id, rec.name))
        return result

    @api.constrains('no_induk')
    def _check_unique_no_induk(self):
        for record in self:
            if record.no_induk:
                # Cek jika ada karyawan lain dengan no_induk yang sama
                existing_employee = self.search([('no_induk', '=', record.no_induk), ('id', '!=', record.id)], limit=1)
                if existing_employee:
                    raise ValidationError(f"NIK {record.no_induk} sudah digunakan oleh karyawan {existing_employee.name}.")

    @api.model
    def create(self, values):
        res =super(hr_employee, self).create(values)
        if res.ptkp_id:
            self.env['hr.ptkp.history'].sudo().create({
                'name'          : res.name,
                'employee_id'   : res.id,
                'ptkp_id'       : res.ptkp_id and res.ptkp_id.id,
                'date'          : datetime.datetime.now().strftime('%Y-%m-%d')
            })
        return res

    def write(self, values):
        if values.get('ptkp_id'):
            self.env['hr.ptkp.history'].sudo().create({
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
    pp58_tier_type = fields.Selection([('tier_a','Tier A'),('tier_b','Tier B'),('tier_c','Tier C')], string='Kategori Tier PP 58')
    children        = fields.Integer('Jumlah Anak')
    value           = fields.Float('Nilai', required=True)
    # company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
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