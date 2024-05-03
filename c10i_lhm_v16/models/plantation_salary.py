import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import base64
import xlrd

class PlantationSalary(models.Model):
    _name = 'plantation.salary'
    _description = 'Daftar Upah'

    name          = fields.Char('Nama', required=False)
    period_id     = fields.Many2one('account.period', string="Periode Upah", ondelete="restrict")
    from_date     = fields.Date("Tanggal Dari")
    to_date       = fields.Date("Tanggal Sd")
    company_id    = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    allowance_ids = fields.One2many('plantation.salary.allowance', 'salary_id', string="Daftar Tunjangan")
    natura_ids    = fields.One2many('plantation.salary.natura', 'salary_id', string="Daftar Natura")
    bpjs_ids      = fields.One2many('plantation.salary.bpjs', 'salary_id', string="Daftar BPJS")
    upah_ids      = fields.One2many('plantation.salary.daftar.upah', 'salary_id', string="Daftar Upah")
    state         = fields.Selection([
                    ('draft', 'New'),
                    ('cancel', 'Cancelled'),
                    ('confirmed', 'Confirmed'),
                    ('done', 'Done')],
                    string='Status',
                    copy=False,
                    default='draft',
                    index=True,
                    readonly=True,
                    help="* New: Dokumen Baru.\n"
                         "* Cancelled: Dokumen Telah Dibatalkan.\n"
                         "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                         "* Done: Dokumen Sudah Selesai Diproses. \n")
    invoice_ids   = fields.Many2many('account.move', string='Payroll Invoice')
    grade_ids     = fields.One2many('plantation.performa.grade', 'salary_id', string="Grade Penyadap")

    def unlink(self):
        for salary in self:
            if salary.state not in ['draft']:
                raise UserError(_('Status dokumen Daftar Upah dengan nomor %s adalah %s.\n'
                                  'Daftar Upah hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (salary.name, salary.state.title()))
        return super(PlantationSalary, self).unlink()

    @api.onchange('period_id')
    def _onchange_period_id(self):
        if self.period_id:
            period_ids = self.env['account.period'].search([('id', '=', self.period_id.id)])
            if len(period_ids) > 1:
                return {
                    'warning': {'title': _('Kesalahan (T.T)'),
                                'message': _("Period ada 2. Hubungi Administrator untuk perbaikan.") },
                }
            else:
                self.from_date  = period_ids[-1].date_start
                self.to_date    = period_ids[-1].date_stop

    def button_confirm(self):
        self.generate_data_upah()
        self.state = 'confirmed'

    def button_draft(self):
        if self.invoice_ids:
            raise UserError(_('Tagihan Penggajian telah terbuat dari dokumen ini. \n'
                  'Silahkan Hapus Invoice tersebut terlebih dahulu.'))
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('plantation.salary') or _('New')
        return super(PlantationSalary, self).create(values)
    
    def generate_data_upah(self):
      # Start BPJS*******************************************************************************
      if self.bpjs_ids:
          self.env.cr.execute("DELETE FROM plantation_salary_bpjs WHERE salary_id=%s", (self.id,))
      # Loop Data Karyawan Filter active=True
      # data_employee   = self.env['hr.employee'].search(['&', ('active', '=', True), '|', ('kesehatan', '=', True), ('ketenagakerjaan', '=', True)], order='no_induk',)
      data_employee   = self.env['hr.employee'].search(['|', ('kesehatan', '=', True), ('ketenagakerjaan', '=', True)], order='no_induk',)
      bpjs_tk         = self.env['hr.insurance'].search([('type', '=', 'ketenagakerjaan'), ("date_from", '<=', self.from_date), ("date_to", '>=', self.to_date)], order='date_to desc', limit=1)
      bpjs_pensiun    = self.env['hr.insurance'].search([('type', '=', 'pensiun'), ("date_from", '<=', self.from_date), ("date_to", '>=', self.to_date)], order='date_to desc', limit=1)
      bpjs_kesehatan  = self.env['hr.insurance'].search([('type', '=', 'kesehatan'), ("date_from", '<=', self.from_date), ("date_to", '>=', self.to_date)], order='date_to desc', limit=1)
      if data_employee:
          for employee in data_employee:
              min_wage = False
              if employee and employee.basic_salary_type == 'employee':
                  min_wage = self.env['hr.minimum.wage'].search([('employee_id', '=', employee.id), ('date_from', '<=', self.from_date), ('date_to', '>=', self.to_date)], limit=1)
              elif employee and employee.basic_salary_type == 'employee_type':
                  min_wage = self.env['hr.minimum.wage'].search([('employee_type_id', '=', employee.type_id.id), ('date_from', '<=', self.from_date), ('date_to', '>=', self.to_date)], limit=1)
              bpjs_tk_tunj        = 0
              bpjs_tk_pot         = 0
              bpjs_tk_setor       = 0
              bpjs_pensiun_tunj   = 0
              bpjs_pensiun_pot    = 0
              bpjs_pensiun_setor  = 0
              bpjs_kesehatan_tunj = 0
              bpjs_kesehatan_pot  = 0
              bpjs_kesehatan_setor= 0
              if employee.ketenagakerjaan:
                  bpjs_tk_tunj            = min_wage.umr_month * bpjs_tk.tunjangan/100
                  bpjs_tk_pot             = min_wage.umr_month * bpjs_tk.potongan/100
                  bpjs_tk_setor           = bpjs_tk_tunj+bpjs_tk_pot
                  bpjs_pensiun_tunj       = min_wage.umr_month * bpjs_pensiun.tunjangan/100
                  bpjs_pensiun_pot        = min_wage.umr_month * bpjs_pensiun.potongan/100
                  bpjs_pensiun_setor      = bpjs_pensiun_tunj+bpjs_pensiun_pot
              if employee.kesehatan:
                  bpjs_kesehatan_tunj     = min_wage.umr_month * bpjs_kesehatan.tunjangan/100
                  bpjs_kesehatan_pot      = min_wage.umr_month * bpjs_kesehatan.potongan/100
                  bpjs_kesehatan_setor    = bpjs_kesehatan_tunj+bpjs_kesehatan_pot
              new_lines = {
                  'employee_id'           : employee.id or False,
                  'employee_type_id'      : employee.type_id.id or False,
                  'no_induk'              : employee.no_induk or False,
                  'bpjs_tk_id'            : employee.bpjs_ketenagakerjaan.id or False,
                  'bpjs_tk_tunj'          : bpjs_tk_tunj or False,
                  'bpjs_tk_pot'           : bpjs_tk_pot or False,
                  'bpjs_tk_setor'         : bpjs_tk_setor or False,
                  'bpjs_pensiun_id'       : employee.bpjs_pensiun.id or False,
                  'bpjs_pensiun_tunj'     : bpjs_pensiun_tunj or False,
                  'bpjs_pensiun_pot'      : bpjs_pensiun_pot or False,
                  'bpjs_pensiun_setor'    : bpjs_pensiun_setor or False,
                  'bpjs_kesehatan_id'     : employee.bpjs_kesehatan.id or False,
                  'bpjs_kesehatan_tunj'   : bpjs_kesehatan_tunj or False,
                  'bpjs_kesehatan_pot'    : bpjs_kesehatan_pot or False,
                  'bpjs_kesehatan_setor'  : bpjs_kesehatan_setor or False,
                  'salary_id'             : self.id,
              }
              if new_lines:
                  self.env['plantation.salary.bpjs'].create(new_lines)

      # Start Natura*******************************************************************************
      if self.natura_ids:
          self.env.cr.execute("DELETE FROM plantation_salary_natura WHERE salary_id=%s", (self.id,))
      # Loop Data Lhm
      self.env.cr.execute("""
          SELECT he.id AS employee_id
          , het.id AS type_id
          , he.no_induk AS no_induk
          , hp.id AS ptkp_id
          , hn.nature AS natura_rp
          FROM lhm_transaction_line lhm2
          LEFT JOIN lhm_transaction lhm ON lhm.id=lhm2.lhm_id
          LEFT JOIN hr_attendance_type hat ON hat.id=lhm2.attendance_id
          LEFT JOIN hr_employee he ON lhm2.employee_id=he.id
          LEFT JOIN resource_resource rr ON he.resource_id=rr.id
          LEFT JOIN hr_employee_type het ON het.id=he.type_id
          LEFT JOIN hr_ptkp hp ON hp.id=he.ptkp_id
          LEFT JOIN hr_nature hn ON he.ptkp_id=hn.ptkp_id
          WHERE rr.company_id = %s 
          AND (het.monthly_employee = TRUE or het.sku_employee = TRUE or het.contract_employee = TRUE)
          AND lhm.date BETWEEN %s::DATE AND %s::DATE 
          GROUP BY he.no_induk, he.id, het.id, hp.id, hn.nature
          having SUM(lhm2.work_day) > 0
          order by he.no_induk
          """, (self.company_id.id, self.from_date, self.to_date))
      for natura in self.env.cr.fetchall():
          new_lines = {
              'employee_id'     : natura[0] or False,
              'employee_type_id': natura[1] or False,
              'no_induk'        : natura[2] or False,
              'ptkp_id'         : natura[3] or False,
              'natura_rp'       : natura[4],
              'salary_id'       : self.id,
          }
          if new_lines:
              self.env['plantation.salary.natura'].create(new_lines)
      # End Natura
      # Start Potongan Lain*******************************************************************************
      if self.allowance_ids:
          self.env.cr.execute("DELETE FROM plantation_salary_allowance WHERE salary_id=%s", (self.id,))
      # Loop Data Potongan
      self.env.cr.execute("""
              SELECT paol.employee_id, pat.id
              , CASE WHEN pat.potongan = TRUE THEN sum(paol.amount) ELSE 0 END AS potongan
              , CASE WHEN pat.tunjangan = TRUE THEN sum(paol.amount) ELSE 0 END AS tunjangan
              , CASE WHEN pat.koperasi = TRUE THEN sum(paol.amount) ELSE 0 END AS koperasi
              , CASE WHEN pat.rapel = TRUE THEN sum(paol.amount) ELSE 0 END AS rapel
              FROM plantation_allowance_other_line paol
              INNER JOIN plantation_allowance_other pao ON pao.id = paol.other_id
              INNER JOIN plantation_allowance_type pat ON pat.id = pao.allowance_type_id
              WHERE pao.company_id = %s AND pao.date BETWEEN %s AND %s
              GROUP BY paol.employee_id, pat.id, pat.potongan, pat.tunjangan, pat.koperasi, pat.rapel
              ORDER BY paol.employee_id, pat.id ASC
          """, (self.company_id.id, self.from_date, self.to_date))
      for allow_other in self.env.cr.fetchall():
          new_lines = {
              'salary_id': self.id,
              'employee_id': allow_other[0],
              'allowance_type_id': allow_other[1],
              'potongan_lain': allow_other[2] if allow_other[2] > 0 else 0,
              'tunjangan_lain': allow_other[3] if allow_other[3] > 0 else 0,
              'koperasi': allow_other[4] if allow_other[4] > 0 else 0,
              'rapel': allow_other[5] if allow_other[5] > 0 else 0,
          }
          if new_lines:
              self.env['plantation.salary.allowance'].create(new_lines)
      # End Potongan Lain ##########################################################

      # Start Daftar Upah*******************************************************************************
      if self.upah_ids:
          self.upah_ids.unlink()

      # Loop Data employee
      self.env.cr.execute("""
          SELECT he.kemandoran_id
          , he.id
          , he.ptkp_id
          , he.type_id
          , he.division_id
          , SUM(ltl.work_day) AS HKE
          , SUM(ltl.non_work_day) AS HKNE
          , SUM(CASE WHEN hat.type_hk = 'hke' and het.monthly_employee = true and ltl.work_day > 0 THEN (ltl.min_wage_value * ltl.work_day)
              WHEN hat.type_hk = 'hke' and het.sku_employee = true and ltl.work_day > 0 THEN (ltl.min_wage_value * ltl.work_day)
              WHEN hat.type_hk = 'hke' and het.bhl_employee = true and ltl.work_day > 0 THEN (ltl.min_wage_value * ltl.work_day)
              WHEN hat.type_hk = 'hke' and het.contract_employee = true and ltl.work_day > 0 THEN (ltl.min_wage_value * ltl.work_day)
              ELSE 0
              END) AS HKE_BYR
          , SUM(CASE WHEN hat.type_hk = 'hkne' and het.monthly_employee = true and ltl.non_work_day > 0 THEN (ltl.min_wage_value * ltl.non_work_day)
              WHEN hat.type_hk = 'hkne' and het.sku_employee = true and ltl.non_work_day > 0 THEN (ltl.min_wage_value * ltl.non_work_day)
              WHEN hat.type_hk = 'hkne' and het.contract_employee = true and ltl.non_work_day > 0 THEN (ltl.min_wage_value * ltl.non_work_day)
              ELSE 0
              END) AS HKNE_BYR
          , hmw.umr_month
          , SUM(ltl.premi+ltl.overtime_value-ltl.penalty) AS premi_lebur
          , hn.nature - COALESCE(SUM(CASE WHEN hat.type_hk is null AND hat.type is null THEN  1 END) * hn.potongan_rp, 0) as natura
          , (select bpjs_pensiun_tunj FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select bpjs_kesehatan_tunj FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select bpjs_tk_tunj FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select bpjs_pensiun_pot FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select bpjs_kesehatan_pot FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select bpjs_tk_pot FROM plantation_salary_bpjs WHERE employee_id = he.id AND salary_id = %s)
          , (select sum(potongan_lain) FROM plantation_salary_allowance WHERE employee_id = he.id AND salary_id = %s)
          , (select sum(tunjangan_lain) FROM plantation_salary_allowance WHERE employee_id = he.id AND salary_id = %s)
          , (select sum(koperasi) FROM plantation_salary_allowance WHERE employee_id = he.id AND salary_id = %s)
          , (select sum(rapel) FROM plantation_salary_allowance WHERE employee_id = he.id AND salary_id = %s)
      FROM lhm_transaction lt
      INNER JOIN hr_foreman hf ON lt.kemandoran_id=hf.id
      INNER JOIN lhm_transaction_line ltl ON ltl.lhm_id=lt.id
      INNER JOIN hr_employee he ON he.id = ltl.employee_id
      INNER JOIN resource_resource rr ON rr.id = he.resource_id
      INNER JOIN hr_employee_type het ON het.id = he.type_id
      INNER JOIN hr_nature hn ON hn.ptkp_id = he.ptkp_id
      LEFT OUTER JOIN hr_division hd ON he.division_id=hd.id
      INNER JOIN hr_attendance_type hat ON ltl.attendance_id=hat.id
      INNER JOIN hr_ptkp hp ON he.ptkp_id=hp.id
      INNER JOIN hr_minimum_wage hmw ON ltl.min_wage_id=hmw.id
      LEFT OUTER JOIN lhm_location_type llt ON ltl.location_type_id=llt.id
      LEFT OUTER JOIN lhm_location ll ON ltl.location_id=ll.id
      LEFT OUTER JOIN lhm_activity la ON ltl.activity_id=la.id 
      INNER JOIN res_users ru ON ru.id= lt.create_uid 
      INNER JOIN res_partner rp ON rp.id=ru.partner_id

      WHERE lt.date::DATE BETWEEN %s::DATE AND %s::DATE
      AND lt.state in ('done','in_progress', 'close')
      AND ltl.attendance_id is not null
      GROUP BY he.kemandoran_id, he.id, he.ptkp_id, he.type_id, he.division_id, hmw.umr_month, hn.nature, hn.potongan_rp
      ORDER BY he.kemandoran_id, he.id
      """, (self.id, self.id, self.id, self.id, self.id, self.id, self.id, self.id, self.id, self.from_date, self.to_date))

      for upah in self.env.cr.fetchall():
          employee_stat = self.env['hr.employee'].browse(upah[1])
          hke = upah[5] or 0.0
          hkne = upah[6] or 0.0
          total_hk = hke + hkne
          hke_rp = upah[7] or 0.0
          hkne_rp = upah[8] or 0.0
          total_hk_rp = hke_rp + hkne_rp
          basic_salary = upah[9] or 0.0
          premi_lembur = upah[10] or 0.0
          natura = upah[11] or 0.0
          tunj_bpjs_pensiun = upah[12] or 0.0
          tunj_bpjs_kesehatan = upah[13] or 0.0
          tunj_bpjs_tk = upah[14] or 0.0

          tunj_lebih_hari = max(total_hk_rp - basic_salary, 0)
          pot_kurang_hari = max(basic_salary - total_hk_rp, 0)
          gaji_bruto = total_hk_rp + premi_lembur + natura + tunj_bpjs_pensiun + tunj_bpjs_kesehatan + tunj_bpjs_tk
          pot_bpjs_pensiun = upah[15] or 0.0
          pot_bpjs_kesehatan = upah[16] or 0.0
          pot_bpjs_tk = upah[17] or 0.0
          pot_lain = upah[18] or 0.0
          tunj_lain = upah[19] or 0.0
          koperasi = upah[20] or 0.0
          rapel = upah[21] or 0.0
          total_potongan = pot_bpjs_pensiun + pot_bpjs_kesehatan + pot_bpjs_tk + pot_lain + koperasi
          total_tunjangan = tunj_lebih_hari + tunj_lain + rapel
          upah_diterima = gaji_bruto - total_potongan

          new_lines = {
              'kemandoran_id': upah[0],
              'employee_id': upah[1],
              'ptkp_id': upah[2],
              'employee_type_id': upah[3],
              'division_id': upah[4],
              'hke': hke,
              'hkne': hkne,
              'total_hk': total_hk,
              'hke_rp': hke_rp,
              'hkne_rp': hkne_rp,
              'total_hk_rp': total_hk_rp,
              'basic_salary': basic_salary,
              'tunjangan_lain': tunj_lain,
              'premi_lembur': premi_lembur,
              'natura': natura,
              'rapel': rapel,
              'koperasi': koperasi,
              'tunj_bpjs_pensiun': tunj_bpjs_pensiun,
              'tunj_bpjs_kesehatan': tunj_bpjs_kesehatan,
              'tunj_bpjs_tk': tunj_bpjs_tk,
              'tunj_lebih_hari': tunj_lebih_hari,
              'gaji_bruto': gaji_bruto,
              'pot_bpjs_pensiun': pot_bpjs_pensiun,
              'pot_bpjs_kesehatan': pot_bpjs_kesehatan,
              'pot_bpjs_tk': pot_bpjs_tk,
              'pot_lain': pot_lain,
              'pot_kurang_hari': pot_kurang_hari,
              'pph_21': 0,
              'total_potongan': total_potongan,
              'total_tunjangan': total_tunjangan,
              'upah_diterima': upah_diterima,
              'salary_id': self.id,
          }
          self.env['plantation.salary.daftar.upah'].create(new_lines)
      # End Daftar Upah ##########################################################
      return False

class plantation_salary_allowance(models.Model):
    _name         = 'plantation.salary.allowance'
    _description  = 'Daftar Tunjangan & Potongan'

    employee_id       = fields.Many2one(comodel_name="hr.employee", string="Nama")
    allowance_type_id = fields.Many2one("plantation.allowance.type", "Tipe")
    no_induk          = fields.Char("NIK", readonly=True, related="employee_id.no_induk", store=True)
    tunjangan_cuti    = fields.Float(string="Tunjangan Cuti", readonly=True)
    kompensasi_cuti   = fields.Float(string="Kompensasi Cuti", readonly=True)
    potongan_lain     = fields.Float(string="Potongan Lain")
    tunjangan_lain    = fields.Float(string="Tunjangan Lain")
    subsidi_kendaraan = fields.Float(string="Subsidi Kendaraan", readonly=True)
    rapel             = fields.Float(string="Rapel/THR", readonly=True)
    koperasi          = fields.Float(string="Koperasi", readonly=True)
    pph21             = fields.Float(string="PPh 21", readonly=True)
    salary_id         = fields.Many2one(comodel_name="plantation.salary", string="Daftar Upah", ondelete="cascade")


class plantation_salary_natura(models.Model):
    _name             = 'plantation.salary.natura'
    _description      = 'Daftar Natura'

    employee_id       = fields.Many2one(comodel_name="hr.employee", string="Nama", readonly=True)
    employee_type_id  = fields.Many2one(comodel_name="hr.employee.type", string="Tipe Karyawan", readonly=True)
    no_induk          = fields.Char("NIK", readonly=True, related="employee_id.no_induk", store=True)
    ptkp_id           = fields.Many2one(comodel_name="hr.ptkp", string="PTKP", readonly=True)
    natura_rp         = fields.Float(string="Natura (Rp)", readonly=True)
    salary_id         = fields.Many2one(comodel_name="plantation.salary", string="Daftar Upah", ondelete="cascade")

class plantation_salary_bpjs(models.Model):
    _name                 = 'plantation.salary.bpjs'
    _description          = 'Daftar BPJS'

    employee_id           = fields.Many2one(comodel_name="hr.employee", string="Nama", readonly=True)
    employee_type_id      = fields.Many2one(comodel_name="hr.employee.type", string="Tipe Karyawan", readonly=True)
    no_induk              = fields.Char("NIK", readonly=True, related="employee_id.no_induk", store=True)
    bpjs_tk_id            = fields.Char("BPJS TK ID", readonly=True, related="employee_id.bpjs_ketenagakerjaan", store=True)
    bpjs_tk_tunj          = fields.Float(string="BPJS TK Tunjangan", readonly=True)
    bpjs_tk_pot           = fields.Float(string="BPJS TK Potongan", readonly=True)
    bpjs_tk_setor         = fields.Float(string="BPJS TK Setoran", readonly=True)
    bpjs_pensiun_id       = fields.Char(string="BPJS Pensiun ID", readonly=True, related="employee_id.bpjs_ketenagakerjaan", store=True)
    bpjs_pensiun_tunj     = fields.Float(string="BPJS Pensiun Tunjangan", readonly=True)
    bpjs_pensiun_pot      = fields.Float(string="BPJS Pensiun Potongan", readonly=True)
    bpjs_pensiun_setor    = fields.Float(string="BPJS Pensiun Setoran", readonly=True)
    bpjs_kesehatan_id     = fields.Char(string="BPJS Kesehatan ID", readonly=True, related="employee_id.bpjs_kesehatan", store=True)
    bpjs_kesehatan_tunj   = fields.Float(string="BPJS Kesehatan Tunjangan", readonly=True)
    bpjs_kesehatan_pot    = fields.Float(string="BPJS Kesehatan Potongan", readonly=True)
    bpjs_kesehatan_setor  = fields.Float(string="BPJS Kesehatan Setoran", readonly=True)
    salary_id             = fields.Many2one(comodel_name="plantation.salary", string="Daftar Upah", ondelete="cascade")

class plantation_salary_daftar_upah(models.Model):
    _name           = 'plantation.salary.daftar.upah'
    _description    = 'Daftar Upah'

    kemandoran_id       = fields.Many2one(comodel_name="hr.foreman", string="Kemandoran", readonly=True)
    employee_id         = fields.Many2one(comodel_name="hr.employee", string="Nama", readonly=True)
    no_induk            = fields.Char("NIK", readonly=True, related="employee_id.no_induk", store=True)
    ptkp_id             = fields.Many2one(comodel_name="hr.ptkp", string="Status", readonly=True)
    employee_type_id    = fields.Many2one(comodel_name="hr.employee.type", string="Tipe Karyawan", readonly=True)
    division_id         = fields.Many2one(comodel_name="hr.division", string="Division", readonly=True)
    hke                 = fields.Float(string="HKE", readonly=True)
    hkne                = fields.Float(string="HKNE", readonly=True)
    total_hk            = fields.Float(string="Total", readonly=True)
    hke_rp              = fields.Float(string="HKE (Rp) Dibayar", readonly=True)
    hkne_rp             = fields.Float(string="HKNE (Rp) Dibayar", readonly=True)
    total_hk_rp         = fields.Float(string="Total (Rp) Dibayar", readonly=True)
    basic_salary        = fields.Float(string="Gaji Pokok", readonly=True)
    tunjangan_lain      = fields.Float(string="Tunjangan Lain", readonly=True)
    premi_lembur        = fields.Float(string="Premi/Lembur", readonly=True)
    natura              = fields.Float(string="Natura", readonly=True)
    rapel               = fields.Float(string="Rapel/THR/Bonus", readonly=True)
    tunj_bpjs_pensiun   = fields.Float(string="Tunjangan BPJS Pensiun", readonly=True)
    tunj_bpjs_kesehatan = fields.Float(string="Tunjangan BPJS Kesehatan", readonly=True)
    tunj_bpjs_tk        = fields.Float(string="Tunjangan BPJS TK", readonly=True)
    tunj_lebih_hari     = fields.Float(string="Tunjangan Lebih Hari", readonly=True)
    gaji_bruto          = fields.Float(string="Gaji Bruto", readonly=True)
    pot_bpjs_pensiun    = fields.Float(string="Potongan BPJS Pensiun", readonly=True)
    pot_bpjs_kesehatan  = fields.Float(string="Potongan BPJS Kesehatan", readonly=True)
    pot_bpjs_tk         = fields.Float(string="Potongan BPJS TK", readonly=True)
    pot_lain            = fields.Float(string="Potongan Lain", readonly=True)
    koperasi            = fields.Float(string="Potongan Koperasi", readonly=True)
    pot_kurang_hari     = fields.Float(string="Potongan Kurang Hari", readonly=True)
    pph_21              = fields.Float(string="PPH 21", readonly=True)
    total_potongan      = fields.Float(string="Total Potongan", readonly=True)
    total_tunjangan     = fields.Float(string="Total Tunjangan", readonly=True)
    upah_diterima       = fields.Float(string="Upah Diterima", readonly=True)
    selisih_hari        = fields.Float(string="Lebih/Kurang Hari & Pembulatan", readonly=True)
    salary_id           = fields.Many2one(comodel_name="plantation.salary", string="Daftar Upah", ondelete="cascade")

    # BEGIN : POC Nyalindung
    grade             = fields.Selection([('5','A+'),('4','A'),('3','B'),('2','C'),('1','D')], string='Grade')
    target_panen      = fields.Float('Target Panen (kg)')
    hasil_panen       = fields.Float('Hasil Panen (kg)')
    # lebih_panen     = fields.Float(compute='_compute_premi_penyadap', string='Lebih Panen (kg)', store=True)
    # rate_premi_panen = fields.Float(compute='_compute_premi_penyadap', string='Rate Premi', help='Sesuai dengan Grade Performa per Bulan', store=True)
    # premi_penyadap  = fields.Float(compute='_compute_premi_penyadap', string='Premi Penyadap', store=True)
    lebih_panen       = fields.Float('Lebih Panen (kg)')
    rate_premi_panen  = fields.Float('Rate Premi', help='Sesuai dengan Grade Performa per Bulan')
    premi_penyadap    = fields.Float('Premi Penyadap')

    # @api.depends('grade', 'target_panen', 'hasil_panen')
    # def _compute_premi_penyadap(self):
    #     for line in self:
    #         line.lebih_panen = line.hasil_panen - line.target_panen if line.hasil_panen>line.target_panen else 0.0
    #         rate_premi = {
    #             '5': 1050.0,
    #             '4': 900.0,
    #             '3': 650.0,
    #             '2': 0.0,
    #             '1': 0.0,
    #         }
    #         line.rate_premi_panen = rate_premi.get(line.grade, 0.0)
    #         line.premi_penyadap = line.rate_premi * line.lebih_panen

    premi_kehadiran = fields.Float('Premi Kehadiran')

    rate_premi_mandor_lebih_panen_per_kg  = fields.Float()
    rate_premi_mandor_panen_per_kg        = fields.Float()
    # @api.depends('hasil_panen','lebih_panen', 'rate_premi_mandor_lebih_panen_per_kg', 'rate_premi_mandor_panen_per_kg')
    # def _compute_premi_mandor(self):
    #     for line in self:
    #         line.premi_mandor = (line.hasil_panen * line.rate_premi_mandor_panen_per_kg) + (line.lebih_panen * line.rate_premi_mandor_lebih_panen_per_kg)
    # premi_mandor = fields.Float(compute='_compute_premi_mandor', string='Premi Mandor', store=True)
    premi_mandor = fields.Float('Premi Mandor')
    # END : POC Nyalindung

class plantation_performa_grade(models.Model):
    _name           = 'plantation.performa.grade'
    _description    = 'Nilai Performa'

    salary_id     = fields.Many2one('plantation.salary', string='Daftar Upah', ondelete='cascade')
    employee_id   = fields.Many2one('hr.employee', string='Karyawan', required=True)
    grade         = fields.Selection([('5','A+'),('4','A'),('3','B'),('2','C'),('1','D')], string='Grade')

class PlantationAllowanceOther(models.Model):
    _name         = 'plantation.allowance.other'
    _description  = 'Daftar Tunjangan & Potongan'
    _inherit      = ['mail.thread', 'mail.activity.mixin']

    name              = fields.Char('No. Register', required=False)
    date              = fields.Date("Tanggal", tracking=True)
    koperasi          = fields.Boolean("Koperasi", related="allowance_type_id.koperasi")
    tunjangan         = fields.Boolean("Tunjangan Lain", related="allowance_type_id.tunjangan")
    potongan          = fields.Boolean("Potongan Lain", related="allowance_type_id.potongan")
    rapel             = fields.Boolean("Rapel/THR", related="allowance_type_id.rapel")
    account_period_id = fields.Many2one(comodel_name="account.period", string="Accounting Periode", ondelete="restrict", tracking=True)
    allowance_type_id = fields.Many2one(comodel_name="plantation.allowance.type", string="Tipe", ondelete="restrict", tracking=True)
    reference         = fields.Char("Referensi", tracking=True)
    company_id        = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    state             = fields.Selection([
                            ('draft', 'New'), ('cancel', 'Cancelled'),
                            ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                            copy=False, default='draft', index=True, readonly=True,
                            help="* New: Dokumen Baru.\n"
                                 "* Cancelled: Dokumen Telah Dibatalkan.\n"
                                 "* Confirmed: Dokumen Sudah Diperiksa Pihak Terkait.\n"
                                 "* Done: Dokumen Sudah Selesai Diproses. \n", tracking=True)

    image             = fields.Binary(string='File Excel', required=False, tracking=True)
    image_filename    = fields.Char(string='File Name', tracking=True)
    allowance_ids     = fields.One2many(comodel_name='plantation.allowance.other.line', inverse_name='other_id', string="Daftar Tunjangan & Potongan Detail", )

    def import_excel(self):
        if not self.image_filename:
            raise UserError(_("Upload File Terlebih Dahulu"))
        if self.allowance_ids:
            self.allowance_ids.unlink()
        data = base64.decodebytes(self.image)
        wb = xlrd.open_workbook(file_contents=data)
        nSheet = len(wb.sheet_names()) - 1
        no = 0
        for i in range(nSheet):
            no += 1
            allowance_obj = self.env['plantation.allowance.other.line']
            sh = wb.sheet_by_index(i)
            for rx in range(sh.nrows):
                if rx > 0:
                    if sh.cell(rx, 0) is not None:
                        val = sh.cell(rx, 0).value

                        if isinstance(val, float):
                            nik_new = str(int(val))
                        else:
                            nik_new = val
                        wt = self.env['hr.employee']
                        employee_id = wt.search([('no_induk', '=', nik_new)]).id
                        allowance_obj.create({
                            # 'no_induk'      : nik_new or False,
                            'employee_id': employee_id,
                            'note': self.reference,
                            'amount': sh.cell(rx, 2).value or False,
                            'other_id': self.id
                        })

    def unlink(self):
        for allowance in self:
            if allowance.state not in ['draft']:
                raise UserError(_('Status Potongan Lainnya dengan nomor %s adalah %s.\n'
                                  'Potongan Lainnya hanya bisa dihapus pada status New.\n'
                                  'Hubungi Administrator untuk info lebih lanjut') % (allowance.name, allowance.state.title()))
        return super(PlantationAllowanceOther, self).unlink()

    def button_confirm(self):
        if not self.allowance_ids:
            raise UserError(_("Setidaknya harus ada 1 Detail"))
        self.state = 'confirmed'

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('plantation.allowance.other') or _('New')
        return super(PlantationAllowanceOther, self).create(values)

class PlantationAllowanceOtherLine(models.Model):
    _name         = 'plantation.allowance.other.line'
    _description  = 'Potongan Lainnya - Detail'

    employee_id   = fields.Many2one(comodel_name="hr.employee", string="Nama", ondelete="restrict", required=1)
    no_induk      = fields.Char("NIK", related="employee_id.no_induk", store=True, readonly=1)
    note          = fields.Char("Keterangan", required=1)
    amount        = fields.Float("Jumlah", required=1)
    other_id      = fields.Many2one(comodel_name="plantation.allowance.other", string="Daftar Tunjangan & Potongan", ondelete="cascade")

class PlantationAllowanceType(models.Model):
    _name         = 'plantation.allowance.type'
    _description  = 'Tipe Potongan'

    name          = fields.Char("Name")
    code          = fields.Char("Code")
    account_id    = fields.Many2one(comodel_name="account.account", string="Expense Account", ondelete="restrict")
    company_id    = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    koperasi      = fields.Boolean("Koperasi")
    tunjangan     = fields.Boolean("Tunjangan Lain")
    potongan      = fields.Boolean("Potongan Lain")
    rapel         = fields.Boolean("Rapelan/THR")
    active        = fields.Boolean("Active", default=True)
    create_invoice      = fields.Boolean("Create Vendor Bill", default=False, help="Create Vendor Bill when making Salary Bill")
    default_partner_id  = fields.Many2one('res.partner', 'Default Partner')

class WizardReportDuAllSelect(models.TransientModel):
    _name           = "wizard.report.du.all.select"
    _description    = "Plantation Salary Select"

    name            = fields.Selection([
                          ('daftar_upah', 'Daftar Upah'),
                          ('daftar_upah_kemandoran', 'Daftar Upah - Kemandoran'),
                          ('slip_gaji', 'Slip Gaji'),
                          ('tanda_terima_gaji', 'Tanda Terima Gaji')
                      ], string='Nama Laporan', default='daftar_upah')
    
    employee_type_id  = fields.Many2many(comodel_name="hr.employee.type", string="Tipe Karyawan", ondelete="restrict", required=False)
    hr_foreman_id     = fields.Many2many(comodel_name="hr.foreman", string="Kemandoran", ondelete="restrict", required=False)
    report_type       = fields.Selection([
                            ('html', 'HTML'), ('csv', 'CSV'), ('xls', 'XLS'), ('rtf', 'RTF'),
                            ('odt', 'ODT'), ('ods', 'ODS'), ('txt', 'Text'), ('pdf', 'PDF'),
                            ('jrprint', 'Jasper Print')
                        ], string='Type', default='xls')

    @api.onchange('name')
    def _onchange_name(self):
        if self.name == "daftar_upah":
            self.report_type = 'xls'
        else:
            self.report_type = 'pdf'

    def create_report(self):
        data = self.read()[-1]
        name_report = False
        if self.name == "daftar_upah":
            name_report = "report_du_all"
        elif self.name == "daftar_upah_kemandoran":
            name_report = "report_du_kemandoran"
        elif self.name == "slip_gaji":
            name_report = "report_du_slip_gaji"
        elif self.name == "tanda_terima_gaji":
            name_report = "report_du_tanda_terima"
        else:
            return True

        return {
            'type': 'ir.actions.report.xml',
            'report_name': name_report,
            'datas': {
                'model': 'wizard.report.du.all.select',
                'id': self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                'ids': self._context.get('active_ids') and self._context.get('active_ids') or [],
                'report_type': self.report_type,
                'form': data
            },
            'nodestroy': False
        }

