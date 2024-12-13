# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Accounting Report",
    'summary': """
        Customization of Accounting Report for PT Nyalindung""",
    'description': """
    """,
    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",
    'category': 'Accounting',
    'version': '16.0.0',
    'depends': [
        'accounting_pdf_reports',
        'account'
    ],
    'data': [
        # 'security/ir.model.access.csv',

        'views/financial_report.xml',
        'wizard/balance_sheet.xml',
        'report/report_financial.xml',
    ],
}
