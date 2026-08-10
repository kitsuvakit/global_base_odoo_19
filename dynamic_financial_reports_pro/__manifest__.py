# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Financial Reports PRO',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Multi-Period Comparison, Variance Analysis & Native Live Excel Export (.xlsx)',
    'description': """
Dynamic Financial Reports PRO for Odoo 19.
=========================================
- Export to formatted Excel (.xlsx / .xls) with live total formulas.
- Multi-Period Comparison (Current Year vs Previous Year).
- Variance Percentage Calculation (% Delta).
- Executive financial dashboards.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 299.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['dynamic_financial_reports_community', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/financial_report_pro_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
