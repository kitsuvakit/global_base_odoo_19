# -*- coding: utf-8 -*-
{
    'name': 'Mobile Presale PWA PRO',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Touch Screen Digital Signature, Offline Mode & GPS Route Optimization',
    'description': """
Mobile Presale PWA PRO for Odoo 19.
===================================
- Customer Touch Screen Digital Signature capture.
- Offline Mode (IndexedDB / PWA sync status tracking).
- GPS Sequence Route Optimization by geographic distance.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 349.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['mobile_presale_pwa', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/presale_visit_pro_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
