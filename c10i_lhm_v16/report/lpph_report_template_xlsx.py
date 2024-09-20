from odoo import fields, models, api

class ReportLpphExcel(models.AbstractModel):
    _name = 'report.c10i_lhm_v16.report_lpph_excel'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'LPPH Excel'

    wbf = {}

    def add_workbook_format(self, workbook):
        self.wbf['title'] = workbook.add_format({'bold': 1, 'align': 'left'})
        self.wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center', 'bg_color': '#B8CCE4', 'font_color': '#000000'})
        self.wbf['header'].set_border()
        self.wbf['header'].set_text_wrap()
        self.wbf['header'].set_align('vcenter')
        self.wbf['header'].set_font_size(10)

        self.wbf['date'] = workbook.add_format({'align': 'center', 'num_format': 'mm/dd/yyyy'})
        self.wbf['date'].set_border()
        self.wbf['date'].set_text_wrap()
        self.wbf['date'].set_align('vcenter')
        self.wbf['date'].set_font_size(8)

        self.wbf['content'] = workbook.add_format({'align': 'center'})
        self.wbf['content'].set_border()
        self.wbf['content'].set_text_wrap()
        self.wbf['content'].set_align('vcenter')
        self.wbf['content'].set_font_size(8)

        return workbook

    def generate_xlsx_report(self, workbook, data, objects):
        workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet("LPPH Report")
        wbf = self.wbf

        worksheet.set_column(0, 12, 15)

        # Header
        next_row = 0
        headers = ["Equipment Name", "Equipment Code", "Brand", "Model", "Serial Number", 
                   "Location", "Expired on", "Employee", "Department", "Other"]
        for col, header in enumerate(headers):
            worksheet.write(next_row, col, header, wbf['header'])

        next_row += 1