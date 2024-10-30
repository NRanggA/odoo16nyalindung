# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrPayslipPph(models.Model):
    _name = "hr.payslip.pph"
    _description = 'Perhitungan PPH'
    _rec_name = 'slip_id'
    _order = 'date desc, id desc'

    slip_id = fields.Many2one('hr.payslip', 'Slip', ondelete='cascade', required=False)

    # company_id = fields.Many2one(related='slip_id.company_id', string='Company', store=True)
    # currency_id = fields.Many2one(related='slip_id.company_id.currency_id', string='Currency', store=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', store=True)
    
    first_contract_date = fields.Date('First Contract Date', required=True)
    termination_date = fields.Date('Termination/Pension End')
    
    ptkp_id = fields.Many2one('hr.ptkp', string='PTKP', ondelete='restrict', required=True)
    date = fields.Date('Masa Pajak', required=True)
    masa_pajak_penyetahun = fields.Integer(compute='_compute_masa_pajak_penyetahun', string='Masa Pajak Penyetahun')
    total_masa_penyetahun = fields.Integer(compute='_compute_masa_pajak_penyetahun', string='Total Masa Pajak Penyetahun')
    
    ######################################################################
    #                     VARIABLE PPH PP58                              #
    ######################################################################
    current_income_base_pph_amount = fields.Float("Pendapatan Tetap Bulan Ini")
    prev_income_base_pph_amount = fields.Float("Pendapatan Tetap Sebelumnya di Bulan ini")
    tunj_pph_this_month = fields.Float(compute='_compute_pph', store=True, stirng='Tunj. PPH Bulan ini')
    cumm_pph_base_amount = fields.Float(compute='_compute_pph_pp58', store=True, string='Pendapatan Kumulatif di Bulan ini')
    current_jht = fields.Float(string='Current JHT/Pensiun')

    rate_category = fields.Char(compute='_compute_pph_pp58', store=True, string='Kategori Tarif')
    rate_pph = fields.Float(compute='_compute_pph_pp58', store=True, string='% Potongan PPH')
    this_month_pph_paid_amount = fields.Float("PPH yang telah dibayar Bulan ini")
    n_loop_1 = fields.Float(compute='_compute_pph_pp58', store=True, string='Jumlah Loop PPH PP58')
    pph_pp58_amount = fields.Float(compute='_compute_pph_pp58', store=True, string='PPH bulan ini')
    
    ######################################################################
    #                     VARIABLE PPH PROGRESIF                         #
    ######################################################################
    # 1. Penghasilan Setahun
    prev_income_this_year = fields.Float("Pendapatan Tetap Sebelumnya di Tahun ini")
    a_year_income = fields.Float(compute='_compute_pph_progresif', string='Pendapatan Setahun')
    
    # 2. Pengurang Penghasilan Setahun
    # 2.1. Potongan Jaminan Hari Tua
    a_year_jht = fields.Float(string='Potongan Pensiun atau JHT/THT Setahun')
    # 2.2. Biaya Jabatan
    biaya_jabatan = fields.Float(compute='_compute_pph_progresif', store=True, string='Biaya Jabatan Setahun')
    # 2.3. PTKP
    ptkp_amount = fields.Float(compute='_compute_ptkp', string='Nilai PTKP', store=True)
    pkp_amount = fields.Float(compute='_compute_pph_progresif', store=True, string='Nilai PKP')

    # 3. Penghitungan PPH Progresif
    pph_progresif_line_ids = fields.One2many('hr.payslip.pph.progresif', 'payslip_pph_id', string='Progresif Lines atas Gaji')
    # 3.1. PPH Setahun
    a_year_tunj_pph = fields.Float(compute='_compute_pph_progresif', store=True, stirng='Tunj. PPH Setahun')
    a_year_pph = fields.Float(compute='_compute_pph_progresif', store=True, string='PPH Setahun')
    # 3.1. PPH Terbayar
    prev_pph_paid_amount = fields.Float("PPH Terbayar Sebelumnya di Tahun Ini")
    pph_paid_amount = fields.Float(compute='_compute_pph_pp58', string="Total PPH Terbayar")
    # 3.1. PPH Terhutang
    pph_unpaid_amount = fields.Float(compute='_compute_pph', store=True, string='PPH Terhutang')
    status_potongan = fields.Selection([('lebih','Lebih Bayar'),('kurang','Kurang Bayar'),('benar','Tidak Terhutang')], compute='_compute_pph', string='Status Potongan Saat ini', store=True)
    
    ############################################################
    # Final Potongan PPH
    ############################################################
    pph_amount = fields.Float(compute='_compute_pph', store=True, string='Potongan PPH')

    count_payslip_pph = fields.Integer(compute='_compute_pph_datas', string='# PPH', store=True)

    ##########################################
    #            COMPUTED METHOD             #
    ##########################################
    @api.depends('date')
    def _compute_pph_datas(self):
        for slip in self:
            pph_slip = self.search([('date','>=',f"{slip.date.year}-01-01"),('date','<=',slip.date),('employee_id','=',slip.employee_id.id)])
            slip.count_payslip_pph = len(pph_slip.ids) if pph_slip else 0

    @api.depends('ptkp_id')
    def _compute_ptkp(self):
        for line in self:
            if line.ptkp_id:
                line.ptkp_amount = line.ptkp_id.value
            else:
                line.ptkp_amount = 0.0

    @api.depends('date', 'first_contract_date', 'termination_date')
    def _compute_masa_pajak_penyetahun(self):
        for line in self:
            # Jika tahun bergabung ke perusahaan lebih kecil dari masa pajak tahun ini
            # Artinya masa pajaknya akan dimulai dari Awal tahun ini
            # Contoh : Tahun gabung 2019, Tahun Masa pajak 2022, Maka masa penyetahunnya adalah 12 bulan di tahun 2022
            # Sehingga jika gaji nya adalah 10jt, maka Penghasilan disetahunkannya adalah 10jt * 12 = 120jt
            if line.first_contract_date.year < line.date.year:
                if not line.termination_date or (line.termination_date and line.termination_date.year>line.date.year):
                    # Selain itu maka total penyetahunnya adalah 12 bulan
                    line.total_masa_penyetahun = 12
                    line.masa_pajak_penyetahun = line.date.month
                else:
                    # Jika potongan ini adalah potongan terakhir dimasa kerjanya
                    if line.termination_date.year==line.date.year and line.termination_date.month>line.date.month:
                        line.total_masa_penyetahun = line.termination_date.month
                        line.masa_pajak_penyetahun = line.date.month
                    elif line.termination_date.year==line.date.year and line.termination_date.month<=line.date.month:
                        line.total_masa_penyetahun = line.termination_date.month
                        line.masa_pajak_penyetahun = line.termination_date.month
                    else:
                        line.total_masa_penyetahun = 1
                        line.masa_pajak_penyetahun = 1
            # Selain itu, artinya karyawan bergabung di tahun yg sama
            # Sehingga masa penyetahunnya dimulai dari bulan mulai bergabung
            # Contoh : Waktu bergabung Februari 2022, tahun pajak 2022. Maka Penghasilan disetahunkan adalah 10jt * 11 = 110jt
            # 11 bulan didapat dari estimasi jumlah bulan kerja selama setahun dimulai dari bulan februari. Des - Feb + 1 = 11 bulan
            else:
                if not line.termination_date or (line.termination_date and line.termination_date.year>line.date.year):
                    line.total_masa_penyetahun = 12 - line.first_contract_date.month + 1
                    line.masa_pajak_penyetahun = line.date.month - line.first_contract_date.month + 1
                else:
                    if line.termination_date.year==line.date.year and line.termination_date.month>line.date.month:
                        # line.total_masa_penyetahun = line.termination_date.month - (12 - line.first_contract_date.month)
                        line.total_masa_penyetahun = line.termination_date.month - line.first_contract_date.month + 1
                        line.masa_pajak_penyetahun = line.date.month - line.first_contract_date.month + 1
                    elif line.termination_date.year==line.date.year and line.termination_date.month<=line.date.month:
                        line.total_masa_penyetahun = line.termination_date.month - line.first_contract_date.month + 1
                        line.masa_pajak_penyetahun = line.termination_date.month - line.first_contract_date.month + 1
                    else:
                        line.total_masa_penyetahun = 1
                        line.masa_pajak_penyetahun = 1

    @api.depends('total_masa_penyetahun',
        'masa_pajak_penyetahun',
        # 'slip_id.contract_id.with_tunjangan_pph21',
        'current_income_base_pph_amount',
        'prev_income_base_pph_amount',
        'prev_pph_paid_amount',
        'ptkp_id',
        'this_month_pph_paid_amount')
    def _compute_pph_pp58(self):
        for line in self:
            if line.total_masa_penyetahun==line.masa_pajak_penyetahun:
                line.cumm_pph_base_amount = line.current_income_base_pph_amount + line.prev_income_base_pph_amount
                line.rate_category = False
                line.rate_pph = 0.0
                # line.tunj_pph_this_month = 0.0
                line.pph_pp58_amount = 0.0
                line.n_loop_1 = 0
                line.pph_paid_amount = line.prev_pph_paid_amount
            else:
                # if line.slip_id.with_tunjangan_pph21:
                if False:
                    pph_pp58_amount = 0.0
                    rate_pph = 0.0
                    rate_category = False
                    
                    cumm_pph_base_amount = line.current_income_base_pph_amount + line.prev_income_base_pph_amount
                    recursive_limit = 30
                    n_loop = 1
                    found = False
                    while (n_loop<recursive_limit and not found):
                        range_pph = self.env['hr.rate.pp58'].sudo().search([
                            ('tier_type','=',line.ptkp_id.pp58_tier_type),
                            ('range_start','<',cumm_pph_base_amount),
                            ('range_stop','>=',cumm_pph_base_amount)], limit=1)
                        rate_category = range_pph.tier_type.replace('tier_','').upper() if range_pph else 'Tidak Terkategorikan'
                        rate_pph = range_pph.percentage if range_pph else 0.0
                        pph_pp58_amount = cumm_pph_base_amount * rate_pph / 100.0
                        cumm_pph_base_amount = line.current_income_base_pph_amount + line.prev_income_base_pph_amount + pph_pp58_amount
                        n_loop+=1
                    
                    line.cumm_pph_base_amount = cumm_pph_base_amount
                    line.rate_category = rate_category
                    line.rate_pph = rate_pph
                    # line.tunj_pph_this_month = pph_pp58_amount - line.this_month_pph_paid_amount
                    line.pph_pp58_amount = pph_pp58_amount - line.this_month_pph_paid_amount
                    line.n_loop_1 = n_loop
                    line.pph_paid_amount = line.prev_pph_paid_amount + (pph_pp58_amount - line.this_month_pph_paid_amount)
                else:
                    line.cumm_pph_base_amount = line.current_income_base_pph_amount + line.prev_income_base_pph_amount
                    range_pph = self.env['hr.rate.pp58'].sudo().search([
                        ('tier_type','=',line.ptkp_id.pp58_tier_type),
                        ('range_start','<',line.cumm_pph_base_amount),
                        ('range_stop','>=',line.cumm_pph_base_amount)], limit=1)
                    line.rate_category = range_pph.tier_type.replace('tier_','').upper() if range_pph else 'Tidak Terkategorikan'
                    line.rate_pph = range_pph.percentage if range_pph else 0.0
                    # line.tunj_pph_this_month = 0.0
                    line.pph_pp58_amount = (line.cumm_pph_base_amount * line.rate_pph / 100.0) - line.this_month_pph_paid_amount
                    line.n_loop_1 = 0.0
                    line.pph_paid_amount = line.prev_pph_paid_amount + line.pph_pp58_amount

    @api.depends('employee_id',
        # 'slip_id.with_tunjangan_pph21',
        'ptkp_id',
        'current_income_base_pph_amount',
        'total_masa_penyetahun',
        'masa_pajak_penyetahun',
        'prev_income_this_year',
        'pph_paid_amount')
    def _compute_pph_progresif(self):
        for line in self:
            # if line.slip_id.with_tunjangan_pph21:
            if False:
                a_year_income = line.prev_income_this_year + line.current_income_base_pph_amount
                biaya_jabatan = line.employee_id._get_biaya_jabatan2(a_year_income)
                a_year_income2 = a_year_income - biaya_jabatan
                pkp_amount = round(a_year_income2 - line.ptkp_amount if a_year_income2>line.ptkp_amount else 0.0, -3)
                tunjangan_pph = 0.0
                recursive_limit = 30
                n_loop = 0
                found = False
                pph_progresif = prev_pph_progresif = 0.0
                while (n_loop<recursive_limit and not found):
                    a_year_pph = line.compute_from_progresif_lines(pkp_amount)
                    # pph_progresif = round(a_year_pph - pph_paid_amount, -2)
                    pph_progresif = round(a_year_pph, -2)
                    if pph_progresif==prev_pph_progresif:
                        found = True
                    else:
                        prev_pph_progresif = pph_progresif

                    a_year_income = line.prev_income_this_year + line.current_income_base_pph_amount + pph_progresif
                    biaya_jabatan = line.employee_id._get_biaya_jabatan2(a_year_income)
                    a_year_income2 = a_year_income - biaya_jabatan
                    pkp_amount = round(a_year_income2 - line.ptkp_amount if a_year_income2>line.ptkp_amount else 0.0, -3)
                    n_loop+=1
                tunjangan_pph = pph_progresif
            else:
                a_year_income = line.prev_income_this_year + line.current_income_base_pph_amount
                biaya_jabatan = line.employee_id._get_biaya_jabatan2(a_year_income)
                a_year_income2 = a_year_income - biaya_jabatan
                pkp_amount = round(a_year_income2 - line.ptkp_amount if a_year_income2>line.ptkp_amount else 0.0, -3)
                a_year_pph = round(line.compute_from_progresif_lines(pkp_amount), -2)
                pph_progresif = a_year_pph
                tunjangan_pph = 0.0

            line.a_year_income = a_year_income
            line.biaya_jabatan = biaya_jabatan
            line.pkp_amount = pkp_amount
            line.a_year_tunj_pph = tunjangan_pph
            line.a_year_pph = a_year_pph
            line.pph_unpaid_amount = pph_progresif - line.pph_paid_amount

    @api.depends('total_masa_penyetahun',
        'masa_pajak_penyetahun',
        'pph_pp58_amount',
        # 'slip_id.with_tunjangan_pph21',
        'pph_unpaid_amount')
    def _compute_pph(self):
        for line in self:
            if line.total_masa_penyetahun==line.masa_pajak_penyetahun:
                line.pph_amount = round(line.pph_unpaid_amount) if round(line.pph_unpaid_amount)>=0.0 else 0.0
                # line.tunj_pph_this_month = line.pph_unpaid_amount if line.slip_id.with_tunjangan_pph21 else 0.0
                line.tunj_pph_this_month = 0.0
                line.status_potongan = False
                line.status_potongan = 'benar' if round(line.pph_unpaid_amount)>=0.0 else 'lebih'
            else:
                line.pph_amount = round(line.pph_pp58_amount)
                # line.tunj_pph_this_month = line.pph_pp58_amount if line.slip_id.with_tunjangan_pph21 else 0.0
                line.tunj_pph_this_month = 0.0
                if line.pph_unpaid_amount < 0:
                    line.status_potongan = 'lebih'
                elif line.pph_unpaid_amount > 0:
                    line.status_potongan = 'kurang'
                else:
                    line.status_potongan = 'benar'
    ##########################################
    #             HELPER METHOD              #
    ##########################################
    def compute_from_progresif_lines(self, pkp_amount):
        pph_amount = 0.0
        for line in self.pph_progresif_line_ids:
            base = 0.0
            if (pkp_amount - line.prev_range_stop) > 0.0:
                base = pkp_amount - line.prev_range_stop
                if (pkp_amount - line.range_stop) > 0.0:
                    if not line.range_stop:
                        base = pkp_amount - line.range_start
                    else:
                        base = line.range_stop - line.range_start
            pph_amount += base * (line.rate * (1.0 + line.rate_denda))
        return pph_amount

    ##########################################
    #            BUSINESS METHOD             #
    ##########################################
    def unlink(self):
        for rec in self:
            if rec.slip_id:
                if rec.slip_id.state!='draft':
                    raise UserError("Tidak dapat menghapus tax entry yang tidak dalam status Draft")
        return super().unlink()

    def action_compute_tax(self):
        for tax_line in self:
            pkp_progresif = self.env['hr.pph21.pkp'].search([], order='sequence asc')
            # if tax_line.type=='pph21_progresif':
            for x in tax_line.pph_progresif_line_ids:
                x.unlink()
            # if tax_line.masa_pajak_penyetahun == tax_line.total_masa_penyetahun:
            # Kalau Karyawan Tidak Tetap tidak perlu hitung akhir masa
            if True:
                progresif_lines = []
                prev_range_stop = 0.0
                rate_denda = tax_line.employee_id._get_percent_denda() if not tax_line.employee_id._check_npwp() else 0.0
                pph21_progresif_lines = []
                pph21_progresif_incentive_lines = []
                for pkp in pkp_progresif:
                    pph21_progresif_lines.append((0,0,{
                        'pkp_id': pkp.id,
                        'prev_range_stop': prev_range_stop,
                        'range_start': pkp.range_start,
                        'range_stop': pkp.range_stop,
                        'rate': pkp.percentage / 100.0,
                        'rate_denda': rate_denda,
                        }))
                    prev_range_stop = pkp.range_stop
                tax_line.write({
                        'pph_progresif_line_ids': pph21_progresif_lines,
                    })
            # else:
                # rate = 0.0
                # tax_line.rate_pph_final = 5 * (1.0 + tax_line.employee_id._get_percent_denda())

    def action_view_payslip_pph(self):
        result = self.env["ir.actions.actions"]._for_xml_id('bpdpks_hr_pph.action_hr_payslip_pph')
        pph_slip = self.search([('date','>=',f"{self.date.year}-01-01"),('date','<=',self.date),('employee_id','=',self.employee_id.id)])
        if len(pph_slip) > 1:
            result['domain'] = "[('id','in',%s)]" % (pph_slip.ids)
        elif len(pph_slip)==1:
            res = self.env.ref('bpdpks_hr_pph.hr_payslip_pph_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pph_slip.id
        else:
            result['domain'] = "[('id','=',0)]"
        return result

class PphProgresif(models.Model):
    _name = 'hr.payslip.pph.progresif'
    _description = 'PPH Progresif'

    payslip_pph_id = fields.Many2one('hr.payslip.pph', 'Slip PPH', ondelete='cascade')
    pkp_id = fields.Many2one('hr.pph21.pkp', 'PKP')
    pkp_amount = fields.Float(string='PKP Amount')
    prev_range_stop = fields.Float('Prev. Range Stop')
    range_start = fields.Float('From')
    range_stop = fields.Float('To')
    rate = fields.Float('Rate')
    rate_denda = fields.Float('+ Rate Denda')
    base_amount = fields.Float(compute='_compute_amount', string='Base Amount', store=True)
    amount = fields.Float(compute='_compute_amount', store=True, string='Amount')
    
    @api.depends(
        'prev_range_stop',
        'range_start',
        'range_stop',
        'rate', 
        'payslip_pph_id.pkp_amount',
        'pkp_amount')
    def _compute_amount(self):
        for line in self.filtered(lambda x: x.payslip_pph_id):
            base = 0.0
            if (line.payslip_pph_id.pkp_amount - line.prev_range_stop) > 0.0:
                base = line.payslip_pph_id.pkp_amount - line.prev_range_stop
                if (line.payslip_pph_id.pkp_amount - line.range_stop) > 0.0:
                    if not line.range_stop:
                        base = line.payslip_pph_id.pkp_amount - line.range_start
                    else:
                        base = line.range_stop - line.range_start
            line.base_amount = base
            line.amount = base * (line.rate * (1.0 + line.rate_denda))