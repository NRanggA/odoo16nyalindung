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
    foreman_id_1        = fields.Many2one('hr.employee', string="Mandor Besar", ondelete="restrict")
    foreman_id          = fields.Many2one('hr.employee', string="Mandor", ondelete="restrict")
    admin_id_1          = fields.Many2one('hr.employee', string="Kerani 1", ondelete="restrict")
    admin_id            = fields.Many2one('hr.employee', string="Kerani", ondelete="restrict")
    nik_mandor_1        = fields.Char("NIK Mandor Besar", related='foreman_id_1.no_induk', readonly=True)
    nik_mandor          = fields.Char("NIK Mandor", related='foreman_id.no_induk', readonly=True)
    nik_kerani_1        = fields.Char("NIK Kerani 1", related='admin_id_1.no_induk', readonly=True)
    nik_kerani          = fields.Char("NIK Kerani", related='admin_id.no_induk', readonly=True)
    user_input_id       = fields.Many2one('res.users', string="Kerani Inputer")
    active              = fields.Boolean("Active", default=True)
    afdeling_id         = fields.Many2one('res.afdeling', string="Afdeling", ondelete="restrict")
    department_id       = fields.Many2one('hr.department', string="Departemen", ondelete="restrict")
    division_id         = fields.Many2one('hr.division', string="Divisi", ondelete="restrict")
    notes               = fields.Text("Catatan")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    employee_ids        = fields.One2many('hr.employee', 'kemandoran_id', string="Daftar Karyawan")
    
    plantation_varieties_id = fields.Many2one('plant.varieties', string='Varietas Payroll')
    plantation_location_type_id = fields.Many2one('lhm.location.type', 'Tipe Lokasi Payroll')
    plantation_location_id = fields.Many2one('lhm.location', 'Lokasi Payroll')
    plantation_activity_id = fields.Many2one('lhm.activity', 'Aktifitas Payroll')
    plantation_activity_bpjs_tk_id = fields.Many2one('lhm.activity', 'BPJS Tenaga Kerja')
    plantation_activity_bpjs_kes_id = fields.Many2one('lhm.activity', 'BPJS Kesehatan')

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
    leave_type_id   = fields.Many2one('hr.leave.type', string="Time off type")

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

    def button_time_off(self):
        if self.leave_type_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Time Off Type',
                'res_model': 'hr.leave.type',
                'view_mode': 'form',
                'res_id': self.leave_type_id.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Time Off Type',
                'res_model': 'hr.leave.type',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_attendance_type_id': self.id},
            }

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
    plantation_varieties_id = fields.Many2one('plant.varieties', string='Varietas Payroll')
    plantation_location_type_id = fields.Many2one('lhm.location.type', 'Tipe Lokasi Payroll')
    plantation_location_id = fields.Many2one('lhm.location', 'Lokasi Payroll')
    plantation_activity_id = fields.Many2one('lhm.activity', 'Aktifitas Payroll')
    plantation_activity_bpjs_tk_id = fields.Many2one('lhm.activity', 'BPJS Tenaga Kerja')
    plantation_activity_bpjs_kes_id = fields.Many2one('lhm.activity', 'BPJS Kesehatan')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    def _default_religion(self):
        religion = self.env['hr.employee.religion'].search([], limit=1)
        return religion and religion.id or False

    def _default_ptkp(self):
        ptkp = self.env['hr.ptkp'].search([('marital','=','TK')], limit=1)
        return ptkp and ptkp.id or False

    # no_induk    = fields.Char('NIK', default="/")
    # gender      = fields.Selection(selection_add=[
    #                 ('Laki-laki', 'Laki-laki'),
    #                 ('Perempuan', 'Perempuan'),
    #                 ('Lainnya', 'Lainnya')
    #             ], default="Lainnya", string='Jenis Kelamin')
    # marital     = fields.Selection(selection_add=[
    #                 ('TK', 'Tidak Menikah'),
    #                 ('K', 'Menikah'),
    #             ], default="TK", string='Status Pernikahan')
    ptkp_id     = fields.Many2one(comodel_name='hr.ptkp', string="PTKP", default=_default_ptkp)
    religion    = fields.Many2one(comodel_name='hr.employee.religion', string="Agama", default=_default_religion)
    birthday    = fields.Date('Date of Birth', default=fields.Date.today())
    identification_id   = fields.Char(string='Identification No')
    passport_id         = fields.Char('Passport No')
    bank_account_id     = fields.Many2one('res.partner.bank', string='Bank Account Number', domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account')
    children            = fields.Integer(string='Number of Children')

    contract_type = fields.Many2one(comodel_name='hr.contract.type', string='Jenis Kontrak', ondelete="restrict", groups="hr.group_hr_user")
    contract_id = fields.Many2one(
        'hr.contract', string='Current Contract', groups="hr.group_hr_user,c10i_lhm_v16.group_plantation_operator",
        domain="[('company_id', '=', company_id), ('employee_id', '=', id)]", help='Current contract of the employee', copy=False)
    
    start_date_contract = fields.Date(string="Mulai Kontrak", groups="hr.group_hr_user")
    end_date_contract   = fields.Date(string="Selesai Kontrak", groups="hr.group_hr_user")
    mandor              = fields.Boolean("Mandor", help="Centang jika dia adalah mandor", groups="hr.group_hr_user")
    master              = fields.Boolean("Master", help="Centang jika dia adalah master", groups="hr.group_hr_user")
    kerani              = fields.Boolean("Kerani", help="Centang jika dia adalah kerani", groups="hr.group_hr_user")
    is_lhm              = fields.Boolean("LHM", help="Data Karyawan LHM", groups="hr.group_hr_user")
    is_npwp             = fields.Boolean("NPWP", help="Have NPWP", groups="hr.group_hr_user")
    kesehatan           = fields.Boolean("Kesehatan", help="Have BPJS Kesehatan", groups="hr.group_hr_user")
    bpjs_kes_date_start = fields.Date("Tanggal Daftar", help="Tanggal Daftar dan mulai dikenakan BPJS Kesehatan", groups="hr.group_hr_user")
    ketenagakerjaan     = fields.Boolean("Ketenagakerjaan", help="Have BPJS Ketenagakerjaan", groups="hr.group_hr_user")
    bpjs_tk_date_start  = fields.Date("Tanggal Daftar", help="Tanggal Daftar dan mulai dikenakan BPJS Ketenagakerjaan", groups="hr.group_hr_user")
    sub_department_id   = fields.Many2one(comodel_name="hr.sub.department", string="Pangkat", ondelete="restrict", groups="hr.group_hr_user")
    type_id             = fields.Many2one(comodel_name="hr.employee.type", string='Tipe Karyawan', ondelete="restrict", required=True, groups="hr.group_hr_user")
    afdeling_id         = fields.Many2one(comodel_name="res.afdeling", string="Afdeling", ondelete="restrict", groups="hr.group_hr_user")
    cost_center_id      = fields.Many2one(comodel_name="account.cost.center", string="Cost Center", ondelete="restrict", groups="hr.group_hr_user")
    division_id         = fields.Many2one(comodel_name="hr.division", string="Divisi", ondelete="restrict", groups="hr.group_hr_user")
    custom_nik          = fields.Boolean("NIK Manual", groups="hr.group_hr_user")
    auto_generate       = fields.Boolean("NIK Automatic", groups="hr.group_hr_user")
    noedit_foreman      = fields.Boolean("No Edit Foreman", groups="hr.group_hr_user")
    appointment_date    = fields.Date("Tanggal Pengangkatan", groups="hr.group_hr_user")
    work_start_date     = fields.Date("Tanggal Masuk", groups="hr.group_hr_user")
    work_end_date       = fields.Date("Tanggal Keluar", groups="hr.group_hr_user")
    basic_salary_type   = fields.Selection(selection=[('employee','Karyawan'), ('employee_type','Tipe Karyawan')],
                                         string="Acuan Gaji Pokok", default="employee_type", groups="hr.group_hr_user")
    kemandoran_id       = fields.Many2one(comodel_name='hr.foreman', string='Kemandoran', ondelete="restrict", groups="hr.group_hr_user")
    mandor_id           = fields.Many2one(comodel_name="hr.employee", string="Mandor", ondelete="restrict",
                                related='kemandoran_id.foreman_id', readonly=True, groups="hr.group_hr_user")
    move_state          = fields.Selection(selection=[('cancel','Dibatalkan'),('ongoing','Dalam Proses'),('moved','Sudah Pindah')],
                                   string='Move Status', readonly=True, groups="hr.group_hr_user")
    movement_ids        = fields.One2many(comodel_name="hr.foreman.movement", inverse_name="employee_id", string="History Movement", groups="hr.group_hr_user")
    umr_ids             = fields.One2many(comodel_name="hr.minimum.wage", inverse_name="employee_id", string="History UMR", groups="hr.group_hr_user")
    plantation_varieties_id = fields.Many2one('plant.varieties', string='Varietas Payroll', groups="hr.group_hr_user")
    plantation_location_type_id = fields.Many2one('lhm.location.type', 'Tipe Lokasi Payroll', groups="hr.group_hr_user")
    plantation_location_id = fields.Many2one('lhm.location', 'Lokasi Payroll', groups="hr.group_hr_user")
    plantation_activity_id = fields.Many2one('lhm.activity', 'Aktifitas Payroll', groups="hr.group_hr_user")
    plantation_activity_hkne_id = fields.Many2one('lhm.activity', 'HKNE', groups="hr.group_hr_user")
    plantation_activity_natura_id = fields.Many2one('lhm.activity', 'Natura', groups="hr.group_hr_user")
    plantation_activity_bpjs_tk_id = fields.Many2one('lhm.activity', 'BPJS Tenaga Kerja', groups="hr.group_hr_user")
    plantation_activity_bpjs_kes_id = fields.Many2one('lhm.activity', 'BPJS Kesehatan', groups="hr.group_hr_user")

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

    def _get_running_contract(self, type_id, basic_salary_type):
        """
        Fungsi untuk mendapatkan kontrak yang sedang berjalan berdasarkan type_id.
        """
        if not type_id:
            return False

        if type_id and basic_salary_type == 'employee_type':
            # Cari kontrak yang sedang berjalan untuk tipe karyawan
            running_contract = self.env['hr.contract'].sudo().search([
                ('employee_type_id', '=', type_id),
                ('state', '=', 'open')
            ], limit=1)
        
        if type_id and basic_salary_type == 'employee':
            running_contract = self.env['hr.contract'].sudo().search([
                ('employee_id', '=', self.id),
                ('state', '=', 'open')
            ], limit=1)

        return running_contract
    
    @api.model
    def create(self, values):
        if values.get('type_id', False) and not values.get('custom_nik', False):
            employee_type = self.env['hr.employee.type'].browse(values['type_id'])
            sequence_id = employee_type.sequence_id
            if sequence_id:
                sequence_number = sequence_id.next_by_id()
                values['no_induk'] = sequence_number
                values['auto_generate'] = True
        
        type_id = values.get('type_id')
        basic_salary_type = values.get('basic_salary_type')

        if basic_salary_type == 'employee' and 'id' in values:
            running_contract = self._get_running_contract(values['id'], basic_salary_type)
        elif basic_salary_type == 'employee_type' and type_id:
            running_contract = self._get_running_contract(type_id, basic_salary_type)
        else:
            running_contract = False
        
        if running_contract:
            values['contract_id'] = running_contract.id
        else:
            values['contract_id'] = False

        values['noedit_foreman'] = True
        employee = super(HrEmployee, self).create(values)
        return employee

    def write(self, values):
        if 'custom_nik' in values:
            if values['custom_nik'] == self.custom_nik:
                del values['custom_nik']

        if 'type_id' in values:
            new_type_id = values['type_id']
            if new_type_id != self.type_id.id:
                employee_type = self.env['hr.employee.type'].browse(new_type_id)
                sequence_id = employee_type.sequence_id
                if sequence_id:
                    sequence_number = sequence_id.next_by_id()
                    values['no_induk'] = sequence_number
                    values['auto_generate'] = True

                running_contract = self._get_running_contract(new_type_id, 'employee_type')
                if running_contract:
                    values['contract_id'] = running_contract.id
                else:
                    values['contract_id'] = False

        if 'basic_salary_type' in values:
            basic_salary_type = values['basic_salary_type']
            if basic_salary_type:
                running_contract = self._get_running_contract(
                    self.type_id.id if 'type_id' not in values else values['type_id'],
                    basic_salary_type
                )
                if running_contract:
                    values['contract_id'] = running_contract.id
                else:
                    values['contract_id'] = False

        res = super(HrEmployee, self).write(values)
        return res



    # def write(self, values):
    #     # Jika custom_nik tidak berubah, hapus dari values
    #     if 'custom_nik' in values:
    #         if values['custom_nik'] == self.custom_nik:
    #             del values['custom_nik']

    #     # Jika tipe karyawan diubah, cek kontrak yang sedang berjalan
    #     if 'type_id' in values:
    #         new_type_id = values['type_id']
    #         if new_type_id != self.type_id.id:
    #             employee_type = self.env['hr.employee.type'].browse(new_type_id)
    #             sequence_id = employee_type.sequence_id
    #             if sequence_id:
    #                 sequence_number = sequence_id.next_by_id()
    #                 values['no_induk'] = sequence_number
    #                 values['auto_generate'] = True

    #             # Cari kontrak yang sedang berjalan untuk tipe baru
    #             running_contract = self._get_running_contract(new_type_id)
    #             if running_contract:
    #                 values['contract_id'] = running_contract.id
        
    #     if 'basic_salary_type' in values:
    #         values['contract_id'] = False

    #     res = super(HrEmployee, self).write(values)
    #     return res

    def get_default_location_activity_payroll(self):
        self.ensure_one()
        res = {
            'plantation_varieties_id': False,
            'plantation_location_type_id': False,
            'plantation_location_id': False,
            'plantation_activity_id': False,
            'plantation_account_id': False,
            'plantation_activity_bpjs_tk_id': False,
            'plantation_account_bpjs_tk_id': False,
            'plantation_activity_bpjs_kes_id': False,
            'plantation_account_bpjs_kes_id': False,
        }
        if self.plantation_location_id and self.plantation_activity_id:
            res.update({
                'plantation_varieties_id': self.plantation_varieties_id.id,
                'plantation_location_type_id': self.plantation_location_type_id.id,
                'plantation_location_id': self.plantation_location_id.id,
                'plantation_activity_id': self.plantation_activity_id.id,
                'plantation_activity_bpjs_tk_id': self.plantation_activity_bpjs_tk_id.id,
                'plantation_activity_bpjs_kes_id': self.plantation_activity_bpjs_kes_id.id,
                'plantation_account_id': self.plantation_activity_id.account_id.id,
                'plantation_account_bpjs_tk_id': self.plantation_activity_bpjs_tk_id.account_id.id,
                'plantation_account_bpjs_kes_id': self.plantation_activity_bpjs_kes_id.account_id.id,

            })
        elif self.kemandoran_id and self.kemandoran_id.plantation_location_id and self.kemandoran_id.plantation_activity_id:
            res.update({
                'plantation_varieties_id': self.kemandoran_id.plantation_varieties_id.id,
                'plantation_location_type_id': self.kemandoran_id.plantation_location_type_id.id,
                'plantation_location_id': self.kemandoran_id.plantation_location_id.id,
                'plantation_activity_id': self.kemandoran_id.plantation_activity_id.id,
                'plantation_activity_bpjs_tk_id': self.kemandoran_id.plantation_activity_bpjs_tk_id.id,
                'plantation_activity_bpjs_kes_id': self.kemandoran_id.plantation_activity_bpjs_kes_id.id,
                'plantation_account_id': self.kemandoran_id.plantation_activity_id.account_id.id,
                'plantation_account_bpjs_tk_id': self.kemandoran_id.plantation_activity_bpjs_tk_id.account_id.id,
                'plantation_account_bpjs_kes_id': self.kemandoran_id.plantation_activity_bpjs_kes_id.account_id.id,
            })
        elif self.department_id and self.department_id.plantation_location_id and self.department_id.plantation_activity_id:
            res.update({
                'plantation_varieties_id': self.department_id.plantation_varieties_id.id,
                'plantation_location_type_id': self.department_id.plantation_location_type_id.id,
                'plantation_location_id': self.department_id.plantation_location_id.id,
                'plantation_activity_id': self.department_id.plantation_activity_id.id,
                'plantation_activity_bpjs_tk_id': self.department_id.plantation_activity_bpjs_tk_id.id,
                'plantation_activity_bpjs_kes_id': self.department_id.plantation_activity_bpjs_kes_id.id,
                'plantation_account_id': self.department_id.plantation_activity_id.account_id.id,
                'plantation_account_bpjs_tk_id': self.department_id.plantation_activity_bpjs_tk_id.account_id.id,
                'plantation_account_bpjs_kes_id': self.department_id.plantation_activity_bpjs_kes_id.account_id.id,
            })
        return res