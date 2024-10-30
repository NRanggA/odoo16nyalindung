# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Report",

    'summary': """
        Nyalindung Reports Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'purchase', 'purchase_request', 'c10i_lhm_v16'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'report/sales_quotation_karet.xml',
        'report/purchase_order_report_template.xml',
        'report/purchase_request_report_template.xml',
        'report/form_pengeluaran_barang_template.xml',
        'report/surat_jalan_template.xml',
        'report/form_pengeluaran_barang_action.xml',
        'report/sales_quotation_karet_action.xml',
        'report/purchase_order_report_action.xml',
        'report/purchase_request_report_action.xml',
        'report/surat_jalan_action.xml',
        'report/report_summary_bkm_action.xml',
        'wizard/wizard_report_summary_bkm_view.xml',

        'report/bukti_penerimaan_barang_template.xml',
        'report/bukti_penerimaan_barang_action.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application' : True,
    'installable' : True
}
