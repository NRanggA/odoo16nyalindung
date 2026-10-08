# -*- coding: utf-8 -*-
{
    'name': "Nyalindung Management Viewer & Auditor Access",
    'version': '16.0.1.0.0',
    'category': 'Security',
    'summary': "Read-only access for Management and Auditor across Inventory, Plantation, MRP, Purchase, Sales, and Accounting.",
    'description': """
Nyalindung Management Viewer & Auditor Access
=============================================
Module providing centralized read-only and reporting access for Management,
Executive Officers, and Auditors across 7 core operational and financial modules:
- Inventory: View operational dashboard, stock balance, and turnover reports.
- Plantation: View LHM, NAP, DRC, Master Blocks, and download all plantation reports.
- Manufacturing: View Manufacturing Orders, BoM, Work Orders, and production reports.
- Purchase: View Purchase Orders, Requests for Quotation, and vendor details.
- Purchase Request: View Purchase Requests and download/print reports.
- Sales: View Sales Orders and Quotations.
- Accounting: View Invoices, Bills, Journal Entries, and download Financial Reports (GL, Balance Sheet, P&L, AR).
    """,
    'author': "PT Nyalindung",
    'website': "https://nyalindung.com",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'purchase',
        'purchase_request',
        'stock',
        'mrp',
        'account',
        'c10i_lhm_v16',
        'ny_plantation',
        'ny_mrp',
        'nyalindung_report',
        'ny_account_report1',
        'c10i_inventory_report',
        'accounting_pdf_reports',
    ],
    'data': [
        'security/viewer_security.xml',
        'security/ir.model.access.csv',
        'views/menu_access_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
