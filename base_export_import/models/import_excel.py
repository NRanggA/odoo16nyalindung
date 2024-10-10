from odoo import _, api, fields, models
from odoo.exceptions import UserError
import tempfile
import binascii
import pandas as pd
import os

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

    def get_row_file(self, file, filename):
        if not file:
            raise UserError('Masukan Filenya terlebih dahulu')

        # Get the file extension from the original file name
        file_extension = os.path.splitext(filename)[1].lower()

        # Create a temporary file with the appropriate suffix
        if file_extension in ['.xlsx', '.xls', '.csv']:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            fp.write(binascii.a2b_base64(file))
            fp.seek(0)
        else:
            raise UserError('Unsupported file format. Please upload an XLSX, XLS, or CSV file.')

        try:
            # Read the file based on its extension
            if file_extension in ['.xlsx', '.xls']:
                # Read Excel files (XLSX and XLS)
                df = pd.read_excel(fp, dtype=object)
            elif file_extension == '.csv':
                # Read CSV files
                df = pd.read_csv(fp, dtype=object, encoding='utf-8', header=0, skip_blank_lines=True)

                # Strip any leading/trailing whitespace from header names
                df.columns = df.columns.str.strip()

            return df
        except Exception as e:
            raise UserError(f'Error reading file: {str(e)}')
        finally:
            fp.close()  # Close the file

    def nan_to_false(self, data):
        if str(data) == 'nan':
            return False
        return data

    def string_false(self, data):
        if data == 'False':
            return False
        return data