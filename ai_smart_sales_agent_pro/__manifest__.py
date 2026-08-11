# -*- coding: utf-8 -*-
{
    'name': 'AI Smart Sales Agent PRO',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Vision AI Part Recognition & Instant Payment Link Generation',
    'description': """
AI Smart Sales Agent PRO for Odoo 19.
====================================
- Gemini Vision AI image processing for spare parts, label photos & damaged products.
- Instant Payment Link autogeneration for fast WhatsApp closing.
- Automated Cross-Selling & Up-Selling suggestions.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 399.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['ai_smart_sales_agent', 'crm', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_ai_pro_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
