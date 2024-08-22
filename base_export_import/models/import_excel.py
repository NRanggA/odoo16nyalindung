
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import tempfile
import binascii
import pandas as pd


class ImportExcel(models.Model):
    _name = 'import.excel'
    _description = 'Import Excel'


    def search_by_name(self, object, code, condition='1=1', param='name'):
        sql = "SELECT id FROM {} WHERE {} = '{}' and {}".format(object, param, code, condition)
        self._cr.execute(sql)
        result = self._cr.dictfetchone()
        if result:
            return result['id']
        else:
            return False


    def get_row_excel(self, file):
        if not file:
            raise UserError('Masukan Filenya terlebih dahulu')
        
        fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
        fp.write(binascii.a2b_base64(file))
        fp.seek(0)
        
        df = pd.read_excel(fp,dtype=object)
        return df
    

    def nan_to_false(self, data):
        if str(data) == 'nan':
            return False
        return data


    def string_false(self, data):
        if data == 'False':
            return False
        return data