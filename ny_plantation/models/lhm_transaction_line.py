from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class LhmLine(models.Model):
    _inherit = 'lhm.transaction.line'
    
    # Custom Perubahan Karyawan Panen jadi Mitra
    drc_latex = fields.Float('drc Latex (%)')
    drc_lump = fields.Float('drc Lump (%)')

    target_produksi_sheet = fields.Float('Target Produksi Sheet', default=10.08)
    target_produksi_compo = fields.Float('Target Produksi Compo', default=1.92)
    
    upah_produksi_sheet = fields.Float('Upah Produksi Sheet')
    upah_produksi_compo = fields.Float('Upah Produksi Compo')

    inst_produksi_sheet = fields.Float('Upah Kelebihan Produksi Sheet')
    inst_produksi_compo = fields.Float('Upah Kelebihan Produksi Compo')

    do_lansir = fields.Boolean('Lansir')

    def compute_conversion(self, lhm_nap_line):
        """
        Fungsi untuk menghitung konversi hasil latex dan lump.
        """
        convert_hasil_latex = self.hasil_1 * self.drc_latex / 100
        convert_hasil_lump  = self.hasil_2 * self.drc_lump / 100
            
        lhm_nap_line.write({
            'hasil_convert_latex': convert_hasil_latex,
            'hasil_convert_lump' : convert_hasil_lump
        })
        
        return convert_hasil_latex, convert_hasil_lump
    
    # Fungsi untuk mendapatkan gaji
    def get_wage_borong_panen(self):
        for record in self:
            record = record.sudo()
            if not record.activity_id.is_nap:
                continue

            # Panggil fungsi untuk mengecek apakah employee ini bulanan atau bukan
            record._check_employee_bulanan()
            lhm_nap_line = self.env['lhm.transaction.nap.line'].sudo().search([('lhm_transaction_line_id', '=', record.id)])
            
            # Hitung konversi menggunakan fungsi compute_conversion
            convert_hasil_latex, convert_hasil_lump = record.compute_conversion(lhm_nap_line)

            if record.is_hasil_2:
                # Dapatkan harga borongan berdasarkan DRC
                price_1 = 6000 # TODO: harus narik dari master data. tapi master data apa yah msh bingung
                price_2 = 4500
                lebih_panen_price_1 = 5000
                lebih_panen_price_2 = 3500
                
                # Menghitun g hasil akhir
                hasil_latex = (record.target_produksi_sheet if record.target_produksi_sheet > convert_hasil_latex else convert_hasil_latex) * price_1
                hasil_lump  = (record.target_produksi_compo if record.target_produksi_compo > convert_hasil_lump else convert_hasil_lump)  * price_2
                hasil_latex2 = (0.0 if record.target_produksi_sheet > convert_hasil_latex else convert_hasil_latex - record.target_produksi_sheet) * lebih_panen_price_1
                hasil_lump2  = (0.0 if record.target_produksi_compo > convert_hasil_lump else convert_hasil_lump - record.target_produksi_compo)  * lebih_panen_price_2
                if record.is_borong:
                    record.write({
                        'contract_wage_value': hasil_latex + hasil_lump + hasil_latex2 + hasil_lump2,
                        'upah_produksi_sheet': hasil_latex,
                        'upah_produksi_compo': hasil_lump,
                        'inst_produksi_sheet': hasil_latex2,
                        'inst_produksi_compo': hasil_lump2,
                    })
            else:
                # Menghitung gaji menggunakan data dari get_price_borongan tanpa DRC
                price_1 = record.activity_id.get_price_borongan()
                if record.is_borong:
                    record.write({
                        'contract_wage_value': lhm_nap_line.hasil_1_nap * price_1,
                    })
        