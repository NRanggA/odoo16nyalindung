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
    'depends': ['base', 'stock', 'hr', 'account', 'c10i_hr_16', 'operating_unit', 'om_account_asset', 'report_xlsx', 'c10i_attendance'],

    # always loaded
    'data': [
        'security/plantation_security.xml',
        'security/plantation_security_new.xml',
        'security/ir.model.access.csv',

        'data/res_doc_type_data.xml',
        'data/location_type_data.xml',
        # 'data/product_data.xml',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'data/user_data.xml',
        'data/operating_unit_data.xml',
        # 'data/stock_data.xml',
        'data/running_sequence_data.xml',
        'data/allowance_type_data.xml',
        'data/account_journal.xml',
        'data/stock_location_data.xml',
        'data/picking_type_data.xml',

        'wizard/wizard_move_employee_views.xml',

        'views/account_views.xml',                     
        'views/hr_views.xml',

        'wizard/wizard_add_employee_views.xml',
        'wizard/wizard_salary_bill_views.xml',

        'views/res_views.xml',
        'views/lhm_kontraktor_harian_views.xml',
        
        # LHM Transaction
        'views/lhm_transaction_views.xml',
        # LHM Activity
        'views/lhm_activity_views.xml',
        # LHM Contractor
        'views/lhm_contractor_views.xml',
        'views/lhm_contractor_line_views.xml',
        # LHM Mesin
        'views/lhm_machine_views.xml',

        'views/lhm_views.xml',
        'wizard/lhm_nap_wizard_views.xml',
        'views/lhm_transaction_line_views.xml',
        'views/plant_varieties_view.xml',
        'views/product_views.xml',                     
        'views/res_partner_views.xml',
        'views/stock_views.xml',
        'views/plantation_salary_views.xml',
        'views/report_invoice.xml',
        'views/account_report.xml',                     
        'views/running_account_views.xml',              
        'views/report_costing_views.xml',               


        # 'wizard/stock_backorder_confirmation_views.xml',
        'wizard/wizard_nab_generate_invoice_views.xml',
        'wizard/wizard_nap_generate_invoice_views.xml',
        'wizard/wizard_report_progres_kerja_views.xml',
        'report/lpph_report_action.xml',
        'report/lppb_report_action.xml',
        'wizard/wizard_report_export_data_views.xml',
        'wizard/wizard_report_monitor_views.xml',
        'wizard/wizard_report_invoice_views.xml',


        'wizard/wizard_report_stock_picking_views.xml',

        'views/stock_picking_views.xml',

        'wizard/wizard_report_inventory_views.xml',
        'wizard/wizard_report_cash_bank_views.xml',
        'wizard/wizard_contractor_bill_views.xml', 
        'wizard/wizard_plasma_bill_views.xml',
        

        'wizard/wizard_running_account_report_views.xml',
        'report/report_running_account_template.xml',
        'report/report_running_account_action.xml',

        'wizard/wizard_report_produksi_views.xml',
        'report/report_produksi_panen_template.xml',
        'report/report_produksi_panen_action.xml',

        
        'wizard/wizard_create_contractor_book_views.xml',
        'wizard/lhm_state_views.xml',
        'wizard/wizard_hasil_lhm_views.xml',
        'views/hr_attendance_correction_views.xml',
        'views/hr_attendance_sheet.xml',
        'views/lhm_tm_category_views.xml',
        'views/target_production_views.xml',
        'views/tarif_premi_production_views.xml',
        'views/lhm_wage_borongan_panen_views.xml',
        'views/lhm_wage_borongan_rawat_views.xml',
        'views/lhm_wage_borongan_contractor_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_cost_center_views.xml',
        'views/lhm_station_views.xml',
        
        'wizard/lhm_transaction_warning_views.xml',

        # Bibitan
        'views/mutation_type_views.xml',
        # 'views/seed_release_views.xml',
        # 'views/seed_semai_views.xml',
        # 'views/seed_mutation_views.xml',
        
        # wizard seed mutasi
        # 'wizard/wizard_seed_mutation_views.xml',


        #REPORT
        # 'report/report_running_account_template.xml',
        # 'report/report_running_account_action.xml',
        

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

}
