# -*- coding: utf-8 -*-
{
    'name': 'Mobile Presale PWA',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Mobile Field Sales Route Planning, GPS Visit Tracking & Touch Catalog',
    'description': """
Mobile Presale PWA & Route Planner for Odoo 19.
===============================================
- Salesperson route planning & daily customer visit assignments.
- Georeferenced visit check-in with GPS latitude & longitude.
- Touch-optimized Mobile Kanban Catalog.
- Reason for non-sale registration.
- Duplicate order prevention.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 199.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/presale_security.xml',
        'security/ir.model.access.csv',
        'views/presale_route_views.xml',
        'views/presale_visit_views.xml',
        'views/presale_catalog_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
