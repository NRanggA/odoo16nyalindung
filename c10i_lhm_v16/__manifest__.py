# -*- coding: utf-8 -*-
{
    'name': "c10i_lhm_v16",

    'summary': """
        Modul Laporan Harian Mandor (LHM) - Odoo 16
        """,

    'description': """
        Modul Laporan Harian Mandor (LHM) yaitu laporan progress fisik dan biaya untuk penggajian karyawan di lapangan.
    """,

    'author': "PT. Konsulten Solusi Indonesia",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'hr', 'account', 'c10i_hr_16', 'operating_unit'],

    # always loaded
    'data': [
        'security/plantation_security.xml',
        'security/ir.model.access.csv',

        'data/res_doc_type_data.xml',
        'data/location_type_data.xml',
        # 'data/product_data.xml',
        'data/ir_sequence_data.xml',
        # 'data/ir_cron_data.xml',
        'data/user_data.xml',
        'data/operating_unit_data.xml',
        # 'data/stock_data.xml',
        'data/running_sequence_data.xml',
        'data/allowance_type_data.xml',

        'wizard/wizard_move_employee_views.xml', # button pindah di komen karena error nama fungsi nya

        'views/hr_views.xml',

        'wizard/wizard_add_employee_views.xml',
        'wizard/wizard_salary_bill_views.xml',

        'views/res_views.xml',
        'views/lhm_views.xml',
        'views/product_views.xml', # Ada group yang tidak di ketahui pada modul product
        'views/res_partner_views.xml',
        'views/stock_views.xml',
        'views/account_views.xml', # Banyak model yang tidak ditemukan di dalam security nya
        'views/plantation_salary_views.xml',
        'views/report_invoice.xml',
        'views/account_report.xml', # Penulisan report di ubah menjadi report versi 16
        'views/running_account_views.xml', # filter di komen line 165
        'views/report_costing_views.xml', # report dan filter di komen
        # 'views/account_voucher_views.xml', #c10i_account di ubah menjadi account
        # 'views/account_payment_views.xml', #c10i_account di ubah menjadi account


        'wizard/stock_backorder_confirmation_views.xml',
        'wizard/wizard_nab_generate_invoice_views.xml',
        'wizard/wizard_report_produksi_views.xml', # menu report nya masih bermasalah
        'wizard/wizard_report_progres_kerja_views.xml', # tag report di komen pada halaman ini
        'wizard/wizard_report_export_data_views.xml',
        'wizard/wizard_report_monitor_views.xml',
        'wizard/wizard_report_invoice_views.xml',

        # 'views/account_invoice_views.xml', # account.invoice_form dan account.invoice_supplier_form tidak di temukan

        'wizard/wizard_report_stock_picking_views.xml',

        'views/stock_picking_views.xml',

        'wizard/wizard_report_inventory_views.xml',
        'wizard/wizard_report_cash_bank_views.xml',
        'wizard/wizard_contractor_bill_views.xml', # beberapa field di komen karena tidak ada di model
        'wizard/wizard_plasma_bill_views.xml',
        'wizard/wizard_running_account_report_views.xml', # error sintaks
        
        'wizard/wizard_create_contractor_book_views.xml',
        'wizard/lhm_state_views.xml',
        # 'views/data_demo_account_period.xml', # Data dummy dari account.period

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
