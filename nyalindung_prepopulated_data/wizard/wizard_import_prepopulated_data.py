from odoo import models, fields, api
from odoo.exceptions import ValidationError
import os
import re
import binascii

class wizardImportPrepopulatedData(models.TransientModel):
    _name = 'wizard.import.prepopulated.data'
    _description = 'Wizard Import Prepopulated Data'

    file_import = fields.Binary('File Import')
    filename = fields.Char('Filename')

    def button_upload(self):
        if not self.file_import:
            raise ValidationError("Please Upload Your Excel File First")
        
        imp = self.env['import.excel']
        if not self.file_import:
            return True
        
        file_extension = os.path.splitext(self.filename)[1].lower()
            
        df = imp.get_row_file(self.file_import, self.filename)
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
                is_dikreditkan_selection = dict(self.env['prepopulated.data']._fields['is_dikreditkan'].selection)

                npwp = row.get('NPWP')
                dikreditkan_value = row.get('Dikreditkan')

                if dikreditkan_value is not False:
                    dikreditkan_value = str(dikreditkan_value).strip()
                    
                    if not dikreditkan_value or dikreditkan_value not in is_dikreditkan_selection.values():
                        raise ValidationError("Field 'Dikreditkan' harus diisi dengan opsi valid: Ya atau Tidak.")

                dpp_value = row.get('DPP') or 0
                if isinstance(dpp_value, str) and file_extension == '.csv':
                    dpp_value = dpp_value.replace(',', '')  # Remove commas for CSV data

                # Safely handle PPN value
                ppn_value = row.get('PPN') or 0
                if isinstance(ppn_value, str) and file_extension == '.csv':
                    ppn_value = ppn_value.replace(',', '')  # Remove commas for CSV data

                # Safely handle PPnBM value
                ppnbm_value = row.get('PPnBM') or 0
                if isinstance(ppnbm_value, str) and file_extension == '.csv':
                    ppnbm_value = ppnbm_value.replace(',', '')  # Remove commas for CSV data

                # Convert to float after processing
                dpp_value = float(dpp_value)
                ppn_value = float(ppn_value)
                ppnbm_value = float(ppnbm_value)

                if not nomor_faktur and npwp is not False:
                    datas.append({
                        'name': row.get('Nama'),
                        'npwp': str(row.get('NPWP')).split('.')[0],
                        'jenis_transaksi': row.get('Jenis Transaksi'),
                        'status_pengganti': row.get('Status Pengganti'),
                        'nomor_faktur': row.get('Nomor Faktur'),
                        'tanggal_faktur': row.get('Tanggal Faktur'),
                        'dpp': dpp_value,
                        'ppn': ppn_value,
                        'ppnbm': ppnbm_value,
                        'is_dikreditkan': dikreditkan_value,
                    })


                    partner_npwp = self.env['res.partner'].search([('vat','like',row.get('NPWP'))])
                    if not partner_npwp:
                        data_npwp.append({
                            'npwp': row.get('NPWP'),
                        })
                
            except binascii.Error as err:
                pass

        print("===================================", data_npwp)

        if data_npwp:
            npwp_list = []
            for list in data_npwp:
                npwp_list.append(str(list['npwp']).split('.')[0])
            
            print("===================================", npwp_list)

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