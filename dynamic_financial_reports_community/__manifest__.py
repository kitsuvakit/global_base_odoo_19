# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Financial Reports Community',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Interactive Real-Time P&L, Balance Sheet & Trial Balance for Odoo Community',
    'description': """
Dynamic Financial Reports for Odoo 19 Community.
===============================================
- Interactive Profit & Loss (P&L) Report.
- Interactive Balance Sheet (Financial Position).
- Trial Balance (Sum & Balances).
- Fiscal closing entries filter.
- Fast direct SQL calculation.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 149.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/financial_report_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
