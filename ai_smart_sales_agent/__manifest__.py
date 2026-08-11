# -*- coding: utf-8 -*-
{
    'name': 'AI Smart Sales Agent',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'AI Sales Assistant for CRM Leads & Automated Quotation Generator (Gemini/OpenAI)',
    'description': """
AI Smart Sales Agent for Odoo 19.
=================================
- Connect with Google Gemini AI or OpenAI ChatGPT.
- Analyze CRM lead requests and write personalized sales responses.
- Auto-generate sale orders (sale.order) from stock catalog.
- Automatic customer creation and pricelist binding.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 199.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['crm', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_agent_config_views.xml',
        'views/crm_lead_ai_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
