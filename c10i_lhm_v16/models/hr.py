from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from datetime import datetime



class HrMinimumWage(models.Model):
    _inherit = 'hr.minimum.wage'
    _description = 'C10i Minimum Wage Management Inherit Plantation'

    basic_salary_type = fields.Selection(
        selection=[('employee', 'Karyawan'), ('employee_type', 'Tipe Karyawan')],
        string="Acuan Gaji Pokok"
    )
    umr_day                         = fields.Float(string="UMR(Hari)", compute='_compute_worked_hours', store=True, readonly=True)
    work_day                        = fields.Integer(string="Hari Kerja", default=25)
    employee_id                     = fields.Many2one('hr.employee', string="Karyawan", ondelete="restrict")
    employee_type_id                = fields.Many2one('hr.employee.type', string="Type Karyawan", ondelete="restrict")
    premi_mandor_lebih_panen_per_kg = fields.Float()
    premi_mandor_panen_per_kg       = fields.Float()

    @api.depends('umr_month', 'work_day')
    def _compute_worked_hours(self):
        for umr in self:
            if umr.umr_month > 0 and umr.work_day > 0:
                umr.umr_day = umr.umr_month / umr.work_day

    @api.onchange('year', 'date_from', 'date_to', 'employee_id', 'employee_type_id', 'basic_salary_type')
    def onchange_date_and_year(self):
        domain = [('year', '=', self.year), ('basic_salary_type', '=', False)]
        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
        elif self.employee_type_id:
            domain.append(('employee_type_id', '=', self.employee_type_id.id))
        
        if self.id:
            domain.append(('id', '!=', self.id))
        
        other_ids = self.env['hr.minimum.wage'].search(domain, order="date_to asc", limit=1)
        
        if other_ids:
            other_ids = other_ids[-1]
        else:
            other_ids = False
        
        if self.basic_salary_type == 'employee':
            self.employee_type_id = False
        elif self.basic_salary_type == 'employee_type':
            self.employee_id = False

        if self.date_to and (self.employee_id or self.employee_type_id):
            if self.date_to <= self.date_from:
                raise UserError(_('Kesalahan Input Data: Tanggal Berakhir Harus Lebih Besar dari Tanggal Mulai'))
            elif self.date_to.year != self.year:
                self.date_to = datetime(self.year, 12, 31)
                raise UserError(_("Tanggal %s tidak dalam tahun: %s.") % (self.date_to, self.year))

        if self.year:
            if other_ids and other_ids.date_to == datetime(self.year, 12, 31) and (self.employee_id or self.employee_type_id):
                raise UserError(_("Semua range tanggal pada tahun %s sudah didefinisikan") % self.year)
            elif other_ids:
                self.date_from = other_ids.date_to + relativedelta(days=1)
            else:
                self.date_from = datetime(self.year, 1, 1)
                self.date_to = datetime(self.year, 12, 31)


class HrForeman(models.Model):
    _name = 'hr.foreman'
    _description = 'Master Data Kemandoran'

    name                = fields.Char("Name")
    code                = fields.Char("Code")
    foreman_id_1        = fields.Many2one('hr.employee', string="Mandor 1", ondelete="restrict")
    foreman_id          = fields.Many2one('hr.employee', string="Mandor", ondelete="restrict")
    admin_id_1          = fields.Many2one('hr.employee', string="Kerani 1", ondelete="restrict")
    admin_id            = fields.Many2one('hr.employee', string="Kerani", ondelete="restrict")
    nik_mandor_1        = fields.Char("NIK Mandor 1", related='foreman_id_1.no_induk', readonly=True)
    nik_mandor          = fields.Char("NIK Mandor", related='foreman_id.no_induk', readonly=True)
    nik_kerani_1        = fields.Char("NIK Kerani", related='admin_id_1.no_induk', readonly=True)
    nik_kerani          = fields.Char("NIK Kerani", related='admin_id.no_induk', readonly=True)
    user_input_id       = fields.Many2one('res.users', string="Kerani Inputer")
    active              = fields.Boolean("Active", default=True)
    afdeling_id         = fields.Many2one('res.afdeling', string="Afdeling", ondelete="restrict")
    department_id       = fields.Many2one('hr.department', string="Departemen", ondelete="restrict")
    division_id         = fields.Many2one('hr.division', string="Divisi", ondelete="restrict")
    notes               = fields.Text("Catatan")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    employee_ids        = fields.One2many('hr.employee', 'kemandoran_id', string="Daftar Karyawan")
    

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, f"{record.code} - {record.name}"))
            elif record.name:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        foremen = self.search(domain + args, limit=limit)
        return foremen.name_get()

class HrForemanMovement(models.Model):
    _name = 'hr.foreman.movement'
    _description = 'Plantation Moving Employee'

    name                = fields.Char("Name")
    date                = fields.Date("Tanggal Pengajuan Pindah")
    moved_date          = fields.Date("Tanggal Pindah")
    employee_id         = fields.Many2one(comodel_name="hr.employee", string="Karyawan", ondelete="restrict")
    src_foreman_id      = fields.Many2one(comodel_name="hr.foreman", string="Kemandoran Asal", ondelete="restrict")
    dest_foreman_id     = fields.Many2one(comodel_name="hr.foreman", string="Kemandoran Tujuan", ondelete="restrict")
    note                = fields.Text("Catatan")
    user_id             = fields.Many2one('res.users', string='Penanggung Jawab', default=lambda self: self.env.user)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    state               = fields.Selection(selection=[('cancel', 'Dibatalkan'), ('ongoing', 'Dalam Proses'), ('moved', 'Sudah Pindah')], string='Status', default='ongoing', readonly=True)

    @api.model
    def cron_move_employee(self):
        self.scheduler_auto_move_employee()

    @api.model
    def scheduler_auto_move_employee(self):
        all_movement_ids = self.search([('state', '=', 'ongoing')])
        if all_movement_ids:
            for move in all_movement_ids:
                if move.employee_id:
                    move.employee_id.write({
                        'kemandoran_id': move.dest_foreman_id.id,
                        'move_state': 'moved'
                    })
                    move.write({
                        'state': 'moved',
                        'moved_date': fields.Date.today()
                    })

class hr_employee_status(models.Model):
    _name           = 'hr.employee.status'
    _description    = 'Employee Status'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    active          = fields.Boolean("Active", default=True)
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)


class hr_employee_foreman_transfer(models.Model):
    _name           = 'hr.employee.foreman.transfer'
    _description    = 'Daftar Transfer Kemandoran'

    name                = fields.Char("LHM Name")
    date                = fields.Date("Tanggal")
    lhm_id              = fields.Many2one(comodel_name="lhm.transaction", string="LHM")
    lhm_line_id         = fields.Many2one(comodel_name="lhm.transaction.line", string="LHM Line")
    other_lhm_id        = fields.Many2one(comodel_name="lhm.transaction", string="Other LHM")
    other_lhm_line_id   = fields.Many2one(comodel_name="lhm.transaction.line", string="Other LHM Line")
    employee_id         = fields.Many2one(comodel_name="hr.employee", string="Nama Karyawan", ondelete="restrict")
    kemandoran_from_id  = fields.Many2one(comodel_name="hr.foreman", string="Asal Kemandoran")
    kemandoran_to_id    = fields.Many2one(comodel_name="hr.foreman", string="Tujuan Kemandoran")
    type                = fields.Selection([('in', 'Masuk'), ('out', 'Keluar')], string='Type')


class hr_attendance_type(models.Model):
    _name           = 'hr.attendance.type'
    _description    = 'Employee Attendance Type'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    special         = fields.Boolean("Spesial")
    type            = fields.Selection([('in', 'Masuk'), ('out', 'Keluar'), ('na', 'N/A'), ('kj', 'KJ')], string='Type')
    type_hk         = fields.Selection([('hke', 'HKE'), ('hkne', 'HKNE')], string='HK Type')
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active          = fields.Boolean("Active", default=True)

    @api.onchange('special')
    def _onchange_special(self):
        if self.special:
            pass
        else:
            self.type = False

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + " - " + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        hr_attendance_type = self.search(domain + args, limit=limit)
        return hr_attendance_type._name_get()


class hr_employee_type(models.Model):
    _name           = 'hr.employee.type'
    _description    = 'Employee Type'

    name                = fields.Char("Name")
    code                = fields.Char("Code")
    status_id           = fields.Many2one(comodel_name="hr.employee.status", string="Status", ondelete="restrict")
    sequence_id         = fields.Many2one(comodel_name="ir.sequence", string="Sequence", ondelete="restrict")
    overtime_calc       = fields.Boolean("Calculate Overtime", default=False)
    monthly_employee    = fields.Boolean("Monthly Employee", default=False)
    sku_employee        = fields.Boolean("SKU Employee", default=False)
    bhl_employee        = fields.Boolean("BHL Employee", default=False)
    contract_employee   = fields.Boolean("Contract Employee", default=False)
    other_employee      = fields.Boolean("Other Employee", default=False)
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active              = fields.Boolean("Active", default=True)
    umr_ids             = fields.One2many(comodel_name="hr.minimum.wage", inverse_name="employee_type_id", string="History UMR")

class hr_sub_department(models.Model):
    _name           = 'hr.sub.department'
    _description    = 'Employee Sub Departemen'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active          = fields.Boolean("Active", default=True)

class hr_division(models.Model):
    _name           = 'hr.division'
    _description    = 'Employee Division'

    name            = fields.Char("Name")
    code            = fields.Char("Code")
    company_id      = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    active          = fields.Boolean("Active", default=True)

class hr_job(models.Model):
    _inherit        = 'hr.job'
    _description    = 'HR Jobs LHM'

    is_lhm              = fields.Boolean("Data LHM")
    active              = fields.Boolean("Active", default=True)

    _sql_constraints = [('name_company_uniq', 'CHECK(1=1)', 'Nama Jabatan tidak boleh sama!'),]

class hr_department(models.Model):
    _inherit        = 'hr.department'
    _description    = 'HR Department LHM'

    is_lhm          = fields.Boolean("Data LHM")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    def _default_religion(self):
        religion = self.env['hr.employee.religion'].search([], limit=1)
        return religion and religion.id or False

    def _default_ptkp(self):
        ptkp = self.env['hr.ptkp'].search([('marital','=','TK')], limit=1)
        return ptkp and ptkp.id or False

    no_induk    = fields.Char('NIK', default="/")
    gender      = fields.Selection(selection_add=[
                    ('Laki-laki', 'Laki-laki'),
                    ('Perempuan', 'Perempuan'),
                    ('Lainnya', 'Lainnya')
                ], default="Lainnya", string='Jenis Kelamin')
    marital     = fields.Selection(selection_add=[
                    ('TK', 'Tidak Menikah'),
                    ('K', 'Menikah'),
                ], default="TK", string='Status Pernikahan')
    ptkp_id     = fields.Many2one(comodel_name='hr.ptkp', string="PTKP", default=_default_ptkp)
    religion    = fields.Many2one(comodel_name='hr.employee.religion', string="Agama", default=_default_religion)
    birthday    = fields.Date('Date of Birth', default=fields.Date.today())
    identification_id   = fields.Char(string='Identification No')
    passport_id         = fields.Char('Passport No')
    bank_account_id     = fields.Many2one('res.partner.bank', string='Bank Account Number', domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account')
    place_of_birth      = fields.Char('Place of Birth')
    children            = fields.Integer(string='Number of Children')

    contract_type = fields.Many2one(comodel_name='hr.contract.type', string='Jenis Kontrak', ondelete="restrict")
    
    start_date_contract = fields.Date(string="Mulai Kontrak")
    end_date_contract   = fields.Date(string="Selesai Kontrak")
    mandor              = fields.Boolean("Mandor", help="Centang jika dia adalah mandor")
    master              = fields.Boolean("Master", help="Centang jika dia adalah master")
    kerani              = fields.Boolean("Kerani", help="Centang jika dia adalah kerani")
    is_lhm              = fields.Boolean("LHM", help="Data Karyawan LHM")
    is_npwp             = fields.Boolean("NPWP", help="Have NPWP")
    kesehatan           = fields.Boolean("Kesehatan", help="Have BPJS Kesehatan")
    bpjs_kes_date_start = fields.Date("Tanggal Daftar", help="Tanggal Daftar dan mulai dikenakan BPJS Kesehatan")
    ketenagakerjaan     = fields.Boolean("Ketenagakerjaan", help="Have BPJS Ketenagakerjaan")
    bpjs_tk_date_start  = fields.Date("Tanggal Daftar", help="Tanggal Daftar dan mulai dikenakan BPJS Ketenagakerjaan")
    sub_department_id   = fields.Many2one(comodel_name="hr.sub.department", string="Pangkat", ondelete="restrict")
    type_id             = fields.Many2one(comodel_name="hr.employee.type", string='Tipe Karyawan', ondelete="restrict")
    afdeling_id         = fields.Many2one(comodel_name="res.afdeling", string="Afdeling", ondelete="restrict")
    cost_center_id      = fields.Many2one(comodel_name="account.cost.center", string="Cost Center", ondelete="restrict")
    division_id         = fields.Many2one(comodel_name="hr.division", string="Divisi", ondelete="restrict")
    custom_nik          = fields.Boolean("NIK Manual")
    auto_generate       = fields.Boolean("NIK Automatic")
    noedit_foreman      = fields.Boolean("No Edit Foreman")
    appointment_date    = fields.Date("Tanggal Pengangkatan")
    work_start_date     = fields.Date("Tanggal Masuk")
    work_end_date       = fields.Date("Tanggal Keluar")
    basic_salary_type   = fields.Selection(selection=[('employee','Karyawan'), ('employee_type','Tipe Karyawan')],
                                         string="Acuan Gaji Pokok", default="employee_type")
    kemandoran_id       = fields.Many2one(comodel_name='hr.foreman', string='Kemandoran', ondelete="restrict")
    mandor_id           = fields.Many2one(comodel_name="hr.employee", string="Mandor", ondelete="restrict",
                                related='kemandoran_id.foreman_id', readonly=True)
    move_state          = fields.Selection(selection=[('cancel','Dibatalkan'),('ongoing','Dalam Proses'),('moved','Sudah Pindah')],
                                   string='Move Status', readonly=True)
    movement_ids        = fields.One2many(comodel_name="hr.foreman.movement", inverse_name="employee_id", string="History Movement")
    umr_ids             = fields.One2many(comodel_name="hr.minimum.wage", inverse_name="employee_id", string="History UMR")
    plantation_location_type_id     = fields.Many2one('lhm.location.type', 'Tipe Lokasi')
    plantation_location_id          = fields.Many2one('lhm.location', 'Lokasi')
    plantation_activity_hkne_id     = fields.Many2one('lhm.activity', 'HKNE')
    plantation_activity_natura_id   = fields.Many2one('lhm.activity', 'Natura')
    plantation_activity_bpjs_tk_id  = fields.Many2one('lhm.activity', 'BPJS Tenaga Kerja')
    plantation_activity_bpjs_kes_id = fields.Many2one('lhm.activity', 'BPJS Kesehatan')

    @api.onchange('kemandoran_id')
    def onchange_kemandoran_id(self):
        if self.kemandoran_id.division_id or self.kemandoran_id.afdeling_id:
            self.division_id = self.kemandoran_id.division_id
            self.afdeling_id = self.kemandoran_id.afdeling_id

    @api.onchange('ketenagakerjaan')
    def onchange_ketenagakerjaan(self):
        if self.ketenagakerjaan:
            self.bpjs_tk_date_start = fields.Date.today()
        else:
            self.bpjs_tk_date_start = False
    
    @api.onchange('kesehatan')
    def onchange_kesehatan(self):
        if self.kesehatan:
            self.bpjs_kes_date_start = fields.Date.today()
        else:
            self.bpjs_kes_date_start = False

    @api.model
    def create(self, values):
        if values.get('type_id', False) and not values.get('custom_nik', False):
            employee_type = self.env['hr.employee.type'].browse(values['type_id'])
            sequence_id = employee_type.sequence_id
            if sequence_id:
                sequence_number = sequence_id.next_by_id()
                values['no_induk'] = sequence_number
                values['auto_generate'] = True
        values['noedit_foreman'] = True
        employee = super(HrEmployee, self).create(values)
        return employee

    def write(self, values):
        if 'custom_nik' in values:
            if values['custom_nik'] == self.custom_nik:
                del values['custom_nik']

        if 'type_id' in values and values['type_id'] == self.type_id.id:
            employee_type = self.env['hr.employee.type'].browse(values['type_id'])
            sequence_id = employee_type.sequence_id
            if sequence_id and self.type_id.sequence_id.id != sequence_id.id:
                sequence_number = sequence_id.next_by_id()
                values['no_induk'] = sequence_number
                values['auto_generate'] = True

        res = super(HrEmployee, self).write(values)
        return res