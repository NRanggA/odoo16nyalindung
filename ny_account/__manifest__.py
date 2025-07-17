# -*- coding: utf-8 -*-
{
    'name': "ny_account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT. Konsalten Solusi Indonesia",
    'website': "https://konsalten.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'c10i_payment', 'c10i_payment_credit_balance', 'account', 'om_account_asset', 'c10i_direct_payment', 'hr', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',

        # Report Payment Vendor
        'report/report_payment_bank_template.xml',
        'report/report_payment_cash_template.xml',
        'views/account_payment_views.xml',
        'views/account_asset_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',

        # Customer Payment
        'report/report_customer_payment_bank_template.xml',
        'report/report_customer_payment_cash_template.xml',

        # Direct Payment
        'report/report_direct_payment_bank_template.xml',
        'report/report_direct_payment_bank_receive_template.xml',
        'report/report_direct_payment_cash_template.xml',
        'report/report_direct_payment_cash_receive_template.xml',
        'views/account_direct_payment_views.xml',

        'report/report_amount_charge_template.xml',

        'report/action_report_payment.xml',

        # Direct Payment
        'views/account_skb_views.xml',

        # E-Faktur List
        'views/efaktur_list_views.xml',

        'wizard/wizard_action_confirm_payment.xml',
        'wizard/wizard_action_confirm_invoice.xml',
        # 'wizard/wizard_action_save_entries.xml',

        # No Create & No Edit
        'views/accounting_nocreate_noedit.xml',
        'report/report_customer_excel_action.xml',
        'wizard/wizard_report_customer_invoice_view.xml',

        # payment sequence
        # 'data/payment_sequence_data.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application' : True,
    'installable' : True
}
