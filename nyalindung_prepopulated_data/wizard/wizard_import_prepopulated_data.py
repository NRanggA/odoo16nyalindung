from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import binascii

class wizardImportPrepopulatedData(models.TransientModel):
    _name = 'wizard.import.prepopulated.data'
    _description = 'Wizard Import Prepopulated Data'

    file_import = fields.Binary('File Import')

    def button_upload(self):
        if not self.file_import:
            raise ValidationError("Please Upload Your Excel File First")
        
        imp = self.env['import.excel']
        if not self.file_import:
            return True
            
        df = imp.get_row_excel(self.file_import)
        datas = []
        data_npwp = []

        header_prepopulated_data = [
            'NPWP',
            'Nama',
            'Jenis Transaksi',
            'Status Pengganti',
            'Nomor Faktur',
            'Tanggal Faktur',
            'DPP',
            'PPN',
            'PPnBM',
            'Dikreditkan',
        ]

        if not all(title_header in df.columns for title_header in header_prepopulated_data):
            raise ValidationError("Pastikan header file excel anda (NPWP, Nama, Jenis Transaksi, Status Pengganti, Nomor Faktur, Tanggal Faktur, DPP, PPN, PPnBM, Dikreditkan)")

        for i in df.index:
            row = {}
            
            for h in header_prepopulated_data:                
                row[h] = imp.string_false(imp.nan_to_false(df[h][i]))
                
            try:
                nomor_faktur = self.env['prepopulated.data'].search([('nomor_faktur', '=', row.get('Nomor Faktur'))])
                dict(self.env['prepopulated.data']._fields['is_dikreditkan'].selection)
                if not row.get('Dikreditkan') or row.get('Dikreditkan') not in ['Ya','Tidak']:
                    raise ValidationError("Field harus di isi, Opsi (Ya, Tidak)")

                if not nomor_faktur:
                    datas.append({
                        'name': row.get('Nama'),
                        'npwp': row.get('NPWP'),
                        'jenis_transaksi': row.get('Jenis Transaksi'),
                        'status_pengganti': row.get('Status Pengganti'),
                        'nomor_faktur': row.get('Nomor Faktur'),
                        'tanggal_faktur': row.get('Tanggal Faktur'),
                        'dpp': float(row.get('DPP') or 0),
                        'ppn': float(row.get('PPN') or 0),
                        'ppnbm': float(row.get('PPnBM') or 0),
                        'is_dikreditkan': row.get('Dikreditkan'),
                    })


                    partner_npwp = self.env['res.partner'].search([('vat','like',row.get('NPWP'))])
                    if not partner_npwp:
                        data_npwp.append({
                            'npwp': row.get('NPWP'),
                        })
                
            except binascii.Error as err:
                pass

        if data_npwp:
            npwp_list = []
            for list in data_npwp:
                npwp_list.append(list['npwp'])

            if len(npwp_list) > 1:
                raise ValidationError(f"Please register these NPWPs as partners first:\n{npwp_list}")
            else:
                raise ValidationError(f"Please register this NPWP as partners first:\n{npwp_list}")

        
        self.env['prepopulated.data'].create(datas)
        self.file_import = False

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }